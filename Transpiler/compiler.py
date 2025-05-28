#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import traceback

class HinglishCompiler:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def log(self, message):
        if self.verbose:
            print(message)
    
    def compile(self, input_file, output_file=None, keep_c=False, run_after=False):
        """
        Compile a Hinglish program (.hp) to an executable.
        
        Args:
            input_file: Path to the .hp source file
            output_file: Path to the output executable (default: input basename)
            keep_c: Whether to keep the intermediate C file (default: False)
            run_after: Whether to run the executable after compilation (default: False)
        """
        # Validate input file
        if not input_file.endswith('.hp'):
            print(f"Warning: Input file '{input_file}' doesn't have .hp extension")
        
        # Determine output filenames
        base_name = os.path.splitext(input_file)[0]
        c_file = f"{base_name}.c"
        executable = output_file or base_name
        
        # Step 1: Read source file
        try:
            with open(input_file, 'r') as f:
                source_code = f.read()
                self.log(f"Read source file: {input_file} ({len(source_code)} bytes)")
        except FileNotFoundError:
            print(f"Error: Source file '{input_file}' not found")
            return False
        except Exception as e:
            print(f"Error reading source file: {str(e)}")
            return False
        
        # Step 2: Transpile to C
        try:
            c_code = self.transpile(source_code)
            if not c_code:
                return False
                
            self.log(f"Successfully transpiled to C code")
            
            # Write C code to file
            with open(c_file, 'w') as f:
                f.write(c_code)
                self.log(f"Wrote C code to: {c_file}")
        except Exception as e:
            print(f"Error during transpilation: {str(e)}")
            if self.verbose:
                traceback.print_exc()
            return False
        
        # Step 3: Compile C to executable
        try:
            result = self.compile_with_gcc(c_file, executable)
            if not result:
                return False
            self.log(f"Compilation successful: {executable}")
        except Exception as e:
            print(f"Error during compilation: {str(e)}")
            if self.verbose:
                traceback.print_exc()
            return False
        
        # Step 4: Clean up C file if not keeping it
        if not keep_c:
            try:
                os.remove(c_file)
                self.log(f"Removed intermediate C file: {c_file}")
            except Exception as e:
                print(f"Warning: Could not remove intermediate C file: {str(e)}")
        
        print(f"Successfully compiled '{input_file}' to '{executable}'")
        
        # Step 5: Run the executable if requested
        if run_after:
            return self.run_executable(executable)
            
        return True
    
    def run_executable(self, executable):
        """Run the compiled executable."""
        print(f"Running '{executable}'...")
        try:
            # Make sure the path is absolute or with ./ prefix for Linux
            if not os.path.isabs(executable) and not executable.startswith('./'):
                executable = f"./{executable}"
                
            # Run the executable and capture output
            result = subprocess.run(
                executable,
                check=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Program execution failed with exit code {result.returncode}")
                return False
                
            print("Program execution completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Program execution failed: {str(e)}")
            return False
        except FileNotFoundError:
            print(f"Error: Could not find executable '{executable}'")
            return False
        except PermissionError:
            print(f"Error: Permission denied when trying to run '{executable}'")
            print("Try running 'chmod +x {executable}' first.")
            return False
    
    def transpile(self, source_code):
        """Transpile Hinglish code to C."""
        # Import the components we need
        from lexer import Lexer
        from parser import Parser
        from generator import CodeGenerator
        
        # Lexical analysis
        self.log("Starting lexical analysis...")
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parsing
        self.log("Parsing tokens to AST...")
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Perform semantic analysis to get symbol table
        self.log("Performing semantic analysis...")
        try:
            from sem_analyser import SemanticAnalyzer
            analyzer = SemanticAnalyzer()
            analysis_result = analyzer.analyze(ast)
            symbol_table = analysis_result['symbol_table']
        except ImportError:
            self.log("Warning: Semantic analyzer not found, proceeding without symbol table")
            symbol_table = {}
        
        # Code generation - use the same generator as in run.py
        self.log("Generating C code...")
        generator = CodeGenerator(symbol_table)
        c_code = generator.generate(ast)
        
        return c_code
    
    def compile_with_gcc(self, c_file, output_file):
        """Compile C code with GCC."""
        self.log(f"Compiling {c_file} to {output_file} using GCC...")
        
        try:
            cmd = ['gcc', c_file, '-o', output_file]
            self.log(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                print(f"GCC compilation failed with code {result.returncode}")
                print(f"Error: {result.stderr.decode()}")
                return False
                
            return True
        except subprocess.CalledProcessError as e:
            print(f"GCC compilation failed: {e.stderr.decode()}")
            return False
        except FileNotFoundError:
            print("Error: GCC compiler not found. Please install GCC.")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Hinglish Programming Language Compiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hpc hello.hp               # Compile hello.hp to executable 'hello'
  hpc hello.hp -o greet      # Compile hello.hp to executable 'greet'
  hpc hello.hp --keep-c      # Keep the intermediate C file
  hpc hello.hp -v            # Verbose output showing compilation steps
  hpc hello.hp --run         # Run the program after compilation
"""
    )
    
    parser.add_argument('input_file', help='Input .hp source file')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('--keep-c', action='store_true', help='Keep intermediate C file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--run', action='store_true', help='Run the executable after compilation')
    
    args = parser.parse_args()
    
    compiler = HinglishCompiler(verbose=args.verbose)
    success = compiler.compile(args.input_file, args.output, args.keep_c, args.run)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())