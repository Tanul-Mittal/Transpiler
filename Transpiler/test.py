from lexer import Lexer, TokenType
from parser import Parser
from sem_analyser import SemanticAnalyzer
from generator import CodeGenerator
import subprocess
import os
import tempfile

def run_test(name, source_code, expected_pattern=None, expect_semantic_errors=None):
    """Run a parser test and verify the output contains expected patterns"""
    print(f"\n{'=' * 50}")
    print(f"TEST: {name}")
    print(f"{'=' * 50}")
    
    print("SOURCE CODE:")
    print(f"```\n{source_code}\n```")
    
    syntax_pass = False
    semantic_pass = False

    # Syntax/parsing phase
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        print("\nPARSER OUTPUT:")
        ast_repr = str(ast)
        print(ast_repr)
        
        if expected_pattern:
            if expected_pattern in ast_repr:
                print(f"\n✅ SYNTAX: Found expected pattern: '{expected_pattern}'")
                syntax_pass = True
            else:
                print(f"\n❌ SYNTAX: Expected pattern not found: '{expected_pattern}'")
        else:
            print("\n✅ SYNTAX: Parsing completed without errors")
            syntax_pass = True
        
        # Semantic analysis phase
        if syntax_pass:
            print("\nRUNNING SEMANTIC ANALYSIS:")
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            
            if expect_semantic_errors:
                # Check for expected semantic errors
                errors_found = [err for err in analyzer.errors if any(expected in err for expected in expect_semantic_errors)]
                
                if errors_found:
                    print(f"\n✅ SEMANTICS: Found expected semantic errors:")
                    for err in errors_found:
                        print(f"  - {err}")
                    semantic_pass = True
                else:
                    print(f"\n❌ SEMANTICS: Expected semantic errors not found!")
                    for err in analyzer.errors:
                        print(f"  - {err}")
            else:
                # No semantic errors expected
                if not analyzer.errors:
                    print("\n✅ SEMANTICS: No semantic errors found as expected")
                    semantic_pass = True
                else:
                    print("\n❌ SEMANTICS: Unexpected semantic errors found:")
                    for err in analyzer.errors:
                        print(f"  - {err}")
        
        return syntax_pass and (semantic_pass if expect_semantic_errors is not None else True)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def run_generator_test(name, source_code, expected_output=None):
    """Run a full transpilation test focusing only on program output validation"""
    print(f"\n{'=' * 50}")
    print(f"CODE GENERATION TEST: {name}")
    print(f"{'=' * 50}")
    
    print("SOURCE CODE:")
    print(f"```\n{source_code}\n```")
    
    try:
        # Run the transpilation pipeline
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        
        analysis_result = analyzer.analyze(ast)

        if not analysis_result['success']:
            print("Semantic analysis failed!")
            return
            
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
                print("\n❌ COMPILATION FAILED:")
                print(compile_result.stderr)
                print("\nGENERATED C CODE (for debugging):")
                print(f"```\n{c_code}\n```")
                
                # Clean up
                os.unlink(temp_c_path)
                return False
            
            # Run the compiled program
            run_result = subprocess.run(
                [temp_exe_path], 
                capture_output=True, 
                text=True
            )
            
            print("\nPROGRAM OUTPUT:")
            print(f"```\n{run_result.stdout}\n```")
            
            # Clean up
            os.unlink(temp_c_path)
            os.unlink(temp_exe_path)
            
            # Check output
            if expected_output in run_result.stdout:
                print(f"\n✅ OUTPUT: Expected output found")
                return True
            else:
                print(f"\n❌ OUTPUT: Expected output '{expected_output}' not found")
                print("\nGENERATED C CODE (for debugging):")
                print(f"```\n{c_code}\n```")
                return False
        
        # If no expected output was provided, just consider it a pass
        print("\n⚠️ NO EXPECTED OUTPUT: Skipping output verification")
        return True
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

# Test cases
tests = [
    # Basic syntax tests
    {
        "name": "Variable Declarations",
        "source": """
        vidhi main() {
            ank x = 5;
            sankhya y = 3.14;
            vakya message = "Hello, world!";
            akshar ch = 'A';
            wapas 0;
        }
        """,
        "expected": "VarDecl(ank, x, Literal(5))"
    },
    {
        "name": "Print Statements",
        "source": """
        vidhi main() {
            likho("Hello, world!");
            ank x = 10;
            likho(x);
            wapas 0;
        }
        """,
        "expected": "Print(Literal(Hello, world!))"
    },
    {
        "name": "If-Else Statements",
        "source": """
        vidhi main() {
            ank x = 5;
            agar (x < 10) {
                likho("Less than 10");
            } nahi_to {
                likho("Not less than 10");
            }
            wapas 0;
        }
        """,
        "expected": "If(Binary(Variable(x), <, Literal(10))"
    },
    {
        "name": "Logical Operators",
        "source": """
        vidhi main() {
            ank x = 5;
            sankhya y = 3.14;
            agar (x >= 5 aur y <= 4.0) {
                likho("Condition met!");
            }
            agar (x == 5 ya y != 3.0) {
                likho("Or condition met!");
            }
            wapas 0;
        }
        """,
        "expected": "Logical(Binary(Variable(x), >=, Literal(5)), aur, Binary(Variable(y), <=, Literal(4.0)))"
    },
    {
        "name": "While Loops",
        "source": """
        vidhi main() {
            ank x = 5;
            jabtak (x > 0) {
                likho(x);
                x = x - 1;
            }
            wapas 0;
        }
        """,
        "expected": "While(Binary(Variable(x), >, Literal(0))"
    },
    {
        "name": "For Loops",
        "source": """
        vidhi main() {
            karo (ank i = 0; i < 5; i = i + 1) {
                likho(i);
            }
            wapas 0;
        }
        """,
        "expected": "For(VarDecl(ank, i, Literal(0)), Binary(Variable(i), <, Literal(5))"
    },
    {
        "name": "Complex Expressions",
        "source": """
        vidhi main() {
            ank a = 5;
            ank b = 3;
            ank c = a * b + (a - b) / 2;
            agar (nahi (a < b)) {
                likho("a is greater than or equal to b");
            }
            wapas 0;
        }
        """,
        "expected": "Unary(nahi, Grouping(Binary(Variable(a), <, Variable(b))))"
    },
    
    # Semantic tests
    {
        "name": "Type Mismatch in Assignment",
        "source": """
        vidhi main() {
            ank x = "This is not an integer";
            wapas 0;
        }
        """,
        "expected": "VarDecl(ank, x, Literal(This is not an integer))",
        "expect_semantic_errors": ["Cannot assign", "to variable 'x' of type ank"]
    },
    {
        "name": "Undefined Variable",
        "source": """
        vidhi main() {
            likho(undefined_var);
            wapas 0;
        }
        """,
        "expected": "Print(Variable(undefined_var))",
        "expect_semantic_errors": ["Variable 'undefined_var' is not defined"]
    },
    {
        "name": "Non-Boolean Condition",
        "source": """
        vidhi main() {
            ank x = 5;
            agar (x + 3) {
                likho("This will cause an error");
            }
            wapas 0;
        }
        """,
        "expected": "If(Binary(Variable(x), +, Literal(3))",
        "expect_semantic_errors": ["Condition in if statement must be a boolean expression"]
    },
    {
        "name": "Type Mismatch in Arithmetic",
        "source": """
        vidhi main() {
            ank x = 5;
            vakya msg = "Hello";
            ank result = x + msg;
            wapas 0;
        }
        """,
        "expected": "Binary(Variable(x), +, Variable(msg))",
        "expect_semantic_errors": ["Cannot assign vakya to variable 'result'"]
    },
    {
        "name": "Function with Explicit Return Type",
        "source": """
        vidhi add(ank a, ank b) ank {
            wapas a + b;
        }
        
        vidhi main() {
            ank result = add(5, 3);
            likho(result);
            wapas 0;
        }
        """,
        "expected": "FuncDecl(add, [Param(ank, a), Param(ank, b)], Token(TokenType.INT, 'ank'"
    },
    {
        "name": "Nested Scope Variables",
        "source": """
        vidhi main() {
            ank x = 10;
            {
                ank x = 20;  # This shadows the outer x
                likho(x);    # Should print 20
            }
            likho(x);        # Should print 10
            wapas 0;
        }
        """,
        "expected": "Block([VarDecl(ank, x, Literal(20)), Print(Variable(x))])"
    },
    {
        "name": "Complex Type Checking",
        "source": """
        vidhi main() {
            ank a = 5;
            sankhya b = 3.14;
            ank c = a + b;   # This should be allowed (float to int conversion)
            
            # This should be an error (incompatible types for comparison)
            akshar ch = 'A';
            agar (a == ch) {
                likho("This shouldn't work");
            }
            wapas 0;
        }
        """,
        "expected": "Binary(Variable(a), ==, Variable(ch))",
        "expect_semantic_errors": ["Cannot compare"]
    }
]

# Test cases for code generation
code_gen_tests = [
    {
        "name": "Hello World",
        "source": """
        vidhi main() {
            likho("Hello, World!");
            wapas 0;
        }
        """,
        "expected_output": "Hello, World!"
    },
    {
        "name": "Integer Arithmetic",
        "source": """
        vidhi main() {
            ank a = 10;
            ank b = 5;
            ank sum = a + b;
            ank diff = a - b;
            ank prod = a * b;
            ank quot = a / b;
            
            likho(sum);   # 15
            likho(diff);  # 5
            likho(prod);  # 50
            likho(quot);  # 2
            
            wapas 0;
        }
        """,
        "expected_output": "15"  # Just check for one output
    },
    {
        "name": "If-Else Statement",
        "source": """
        vidhi main() {
            ank x = 10;
            
            agar (x > 5) {
                likho("x is greater than 5");
            } nahi_to {
                likho("x is not greater than 5");
            }
            
            wapas 0;
        }
        """,
        "expected_output": "x is greater than 5"
    },
    {
        "name": "While Loop",
        "source": """
        vidhi main() {
            ank i = 1;
            jabtak (i <= 3) {
                likho(i);
                i = i + 1;
            }
            wapas 0;
        }
        """,
        "expected_output": "1"  # Just check for the start of output
    },
    {
        "name": "For Loop",
        "source": """
        vidhi main() {
            karo (ank i = 1; i <= 3; i = i + 1) {
                likho(i);
            }
            wapas 0;
        }
        """,
        "expected_output": "1"  # Just check for the start of output
    },
    {
        "name": "Function Call",
        "source": """
        vidhi square(ank x) ank {
            wapas x * x;
        }
        
        vidhi main() {
            ank num = 5;
            ank result = square(num);
            likho(result);  # Should print 25
            wapas 0;
        }
        """,
        "expected_output": "25"
    },
    {
        "name": "Nested Loops and Conditionals",
        "source": """
        vidhi main() {
            ank i = 1;
            jabtak (i <= 3) {
                ank j = 1;
                jabtak (j <= i) {
                    agar (i == j) {
                        likho("Equal");
                    } nahi_to {
                        likho("Not equal");
                    }
                    j = j + 1;
                }
                i = i + 1;
            }
            wapas 0;
        }
        """,
        "expected_output": "Equal"  # Just check for one output
    },
    {
        "name": "String and Character Handling",
        "source": """
        vidhi main() {
            vakya message = "Hello";
            akshar first = 'H';
            
            likho(message);
            likho(first);
            
            wapas 0;
        }
        """,
        "expected_output": "Hello"
    },
    {
        "name": "Logical Operators",
        "source": """
        vidhi main() {
            ank a = 5;
            ank b = 10;
            
            agar (a < b aur a > 0) {
                likho("Condition 1 true");
            }
            
            agar (a > b ya a > 0) {
                likho("Condition 2 true");
            }
            
            agar (nahi (a > b)) {
                likho("Condition 3 true");
            }
            
            wapas 0;
        }
        """,
        "expected_output": "Condition 1 true"
    },
    {
        "name": "Recursive Function",
        "source": """
        vidhi factorial(ank n) ank {
            agar (n <= 1) {
                wapas 1;
            }
            wapas n * factorial(n - 1);
        }
        
        vidhi main() {
            likho(factorial(5));  # Should print 120
            wapas 0;
        }
        """,
        "expected_output": "120"
    },
    {
        "name": "Float Arithmetic",
        "source": """
        vidhi main() {
            sankhya a = 3.5;
            sankhya b = 1.5;
            sankhya sum = a + b;
            
            likho(sum);  # Should be around 5.0
            
            wapas 0;
        }
        """,
        "expected_output": "5"  # Simplified check, might have decimals
    },
    {
        "name": "Complex Expression",
        "source": """
        vidhi main() {
            ank a = 5;
            ank b = 3;
            ank c = 2;
            
            ank result = a * b + (a - b) * c;
            likho(result);  # Should be 19
            
            wapas 0;
        }
        """,
        "expected_output": "19"
    }
]

def run_all_tests():
    """Run all test cases and report results"""
    passed = 0
    total = len(tests)
    
    syntax_passed = 0
    semantic_passed = 0
    semantic_total = sum(1 for test in tests if "expect_semantic_errors" in test)
    
    for test in tests:
        if run_test(test["name"], test["source"], test["expected"], 
                   test.get("expect_semantic_errors")):
            passed += 1
            if "expect_semantic_errors" in test:
                semantic_passed += 1
            else:
                syntax_passed += 1
    
    print(f"\n{'=' * 50}")
    print(f"BASIC TESTS SUMMARY: {passed}/{total} tests passed")
    print(f"  - Syntax:    {syntax_passed}/{total-semantic_total} tests passed")
    print(f"  - Semantics: {semantic_passed}/{semantic_total} tests passed")
    print(f"{'=' * 50}")
    
    # Run code generation tests
    print(f"\n{'=' * 50}")
    print(f"RUNNING CODE GENERATION TESTS")
    print(f"{'=' * 50}")
    
    gen_passed = 0
    gen_total = len(code_gen_tests)
    
    for test in code_gen_tests:
        if run_generator_test(
            test["name"], 
            test["source"], 
            test.get("expected_output")
        ):
            gen_passed += 1
    
    print(f"\n{'=' * 50}")
    print(f"CODE GENERATION SUMMARY: {gen_passed}/{gen_total} tests passed")
    print(f"{'=' * 50}")
    
    # Overall summary
    print(f"\n{'=' * 50}")
    print(f"OVERALL SUMMARY: {passed + gen_passed}/{total + gen_total} tests passed")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    run_all_tests()