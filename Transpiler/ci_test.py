from test import run_test, run_generator_test, tests, code_gen_tests
import sys
import xml.etree.ElementTree as ET
import datetime

# Add a function to suppress detailed output
def run_test_ci(name, source_code, expected_pattern=None, expect_semantic_errors=None):
    """Run a test with minimal output for CI environments"""
    # Just print the test name without the full source code and details
    print(f"Running test: {name}...", end=" ")
    
    from test import Lexer, Parser, SemanticAnalyzer
    
    syntax_pass = False
    semantic_pass = False

    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        ast_repr = str(ast)
        
        if expected_pattern:
            if expected_pattern in ast_repr:
                syntax_pass = True
            else:
                print("❌ (syntax)")
                return False
        else:
            syntax_pass = True
        
        # Semantic analysis phase
        if syntax_pass:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            if expect_semantic_errors:
                # Check for expected semantic errors
                errors_found = [err for err in analyzer.errors if any(expected in err for expected in expect_semantic_errors)]
                
                if errors_found:
                    semantic_pass = True
                else:
                    print("❌ (semantic)")
                    return False
            else:
                # No semantic errors expected
                if not analyzer.errors:
                    semantic_pass = True
                else:
                    print("❌ (semantic)")
                    return False
        
        result = syntax_pass and (semantic_pass if expect_semantic_errors is not None else True)
        print("✅" if result else "❌")
        return result
        
    except Exception as e:
        print(f"❌ (error: {type(e).__name__})")
        return False

def run_generator_test_ci(name, source_code, expected_output=None):
    """Run a code generation test with minimal output for CI environments"""
    print(f"Running code gen test: {name}...", end=" ")
    
    from test import Lexer, Parser, SemanticAnalyzer, CodeGenerator
    import tempfile, subprocess, os
    
    try:
        # Run the transpilation pipeline
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        
        analysis_result = analyzer.analyze(ast)

        if not analysis_result['success']:
            print("❌ (analysis failed)")
            return False
            
        generator = CodeGenerator(analysis_result['symbol_table'])
        c_code = generator.generate(ast)
        
        # Only attempt to compile and run if there's expected output to verify
        if expected_output is not None:
            # Save C code to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.c', delete=False) as temp_c_file:
                temp_c_path = temp_c_file.name
                temp_c_file.write(c_code.encode())
            
            # Compile the C code
            temp_exe_path = temp_c_path + '.exe'
            compile_result = subprocess.run(
                ['gcc', temp_c_path, '-o', temp_exe_path], 
                capture_output=True, 
                text=True
            )
            
            if compile_result.returncode != 0:
                print("❌ (compilation failed)")
                
                # Clean up
                os.unlink(temp_c_path)
                return False
            
            # Run the compiled program
            run_result = subprocess.run(
                [temp_exe_path], 
                capture_output=True, 
                text=True
            )
            
            # Clean up
            os.unlink(temp_c_path)
            os.unlink(temp_exe_path)
            
            # Check output
            if expected_output in run_result.stdout:
                print("✅")
                return True
            else:
                print("❌ (output mismatch)")
                return False
        
        # If no expected output was provided, just consider it a pass
        print("⚠️ (no output check)")
        return True
    
    except Exception as e:
        print(f"❌ (error: {type(e).__name__})")
        return False

def run_all_tests_with_junit():
    """Run all test cases with minimal console output and generate JUnit XML report"""
    # Initialize test counters
    passed = 0
    total = len(tests)
    
    syntax_passed = 0
    semantic_passed = 0
    semantic_total = sum(1 for test in tests if "expect_semantic_errors" in test)
    
    # Create JUnit XML structure
    test_suite = ET.Element("testsuite")
    test_suite.set("name", "Transpiler Tests")
    test_suite.set("timestamp", datetime.datetime.now().isoformat())
    
    # Run syntax and semantic tests
    print("\nRunning basic tests...")
    for test in tests:
        test_case = ET.SubElement(test_suite, "testcase")
        test_case.set("name", test["name"])
        test_case.set("classname", "BasicTests")
        
        start_time = datetime.datetime.now()
        result = run_test_ci(test["name"], test["source"], test["expected"], 
                          test.get("expect_semantic_errors"))
        end_time = datetime.datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        test_case.set("time", str(duration))
        
        if result:
            passed += 1
            if "expect_semantic_errors" in test:
                semantic_passed += 1
            else:
                syntax_passed += 1
        else:
            # Add failure element for failed tests
            failure = ET.SubElement(test_case, "failure")
            failure.set("message", f"Test {test['name']} failed")
    
    # Run code generation tests
    print("\nRunning code generation tests...")
    gen_passed = 0
    gen_total = len(code_gen_tests)
    
    for test in code_gen_tests:
        test_case = ET.SubElement(test_suite, "testcase")
        test_case.set("name", test["name"])
        test_case.set("classname", "CodeGenTests")
        
        start_time = datetime.datetime.now()
        result = run_generator_test_ci(
            test["name"], 
            test["source"], 
            test.get("expected_output")
        )
        end_time = datetime.datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        test_case.set("time", str(duration))
        
        if result:
            gen_passed += 1
        else:
            # Add failure element for failed tests
            failure = ET.SubElement(test_case, "failure")
            failure.set("message", f"Code generation test {test['name']} failed")
    
    # Update test counts in XML
    test_suite.set("tests", str(total + gen_total))
    test_suite.set("failures", str((total - passed) + (gen_total - gen_passed)))
    
    # Print summary to console
    print(f"\nSUMMARY:")
    print(f"- Basic tests: {passed}/{total} passed")
    print(f"  - Syntax: {syntax_passed}/{total-semantic_total}")
    print(f"  - Semantics: {semantic_passed}/{semantic_total}")
    print(f"- Code generation: {gen_passed}/{gen_total} passed")
    print(f"- Overall: {passed + gen_passed}/{total + gen_total} passed")
    
    # Write XML to file
    tree = ET.ElementTree(test_suite)
    tree.write("test-results.xml", encoding="utf-8", xml_declaration=True)
    
    # Return overall success/failure
    return (passed + gen_passed) == (total + gen_total)

if __name__ == "__main__":
    print("Running Transpiler CI tests...")
    success = run_all_tests_with_junit()
    sys.exit(0 if success else 1)