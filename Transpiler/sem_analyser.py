from parser import *

class SymbolTable:
    """Tracks variables and their types in different scopes"""
    
    def __init__(self):
        self.scopes = [{}]  # Start with global scope
    
    def enter_scope(self):
        """Create a new scope for a block"""
        self.scopes.append({})
    
    def exit_scope(self):
        """Exit the current scope"""
        if len(self.scopes) > 1:  # Never remove global scope
            self.scopes.pop()
    
    def define(self, name, var_type):
        """Define a variable in current scope"""
        self.scopes[-1][name] = var_type
    
    def lookup(self, name):
        """Look up a variable in all scopes, from innermost to outermost"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class SemanticError(Exception):
    """Exception raised for semantic errors"""
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()
        self.current_function = None
        self.errors = []
    
    def analyze(self, program):
        """Analyze AST for semantic errors and return type information"""
        try:
            self.visit(program)
            
            # Create result object with analysis results
            result = {
                'success': len(self.errors) == 0,
                'errors': self.errors.copy(),
                'symbol_table': self.symbols  # Return the symbol table for use by code generator
            }
            
            # Print errors if any
            if not result['success']:
                for error in self.errors:
                    print(f"Semantic Error: {error}")
            
            return result
        except SemanticError as e:
            print(f"Semantic Error: {e}")
            return {
                'success': False,
                'errors': [str(e)],
                'symbol_table': self.symbols
            }
    
    def visit(self, node):
        """Visit a node in the AST"""
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Default handler for unhandled node types"""
        pass
    
    def visit_Program(self, program):
        """Visit the program node"""
        for statement in program.statements:
            self.visit(statement)
    
    def visit_FunctionDeclaration(self, func):
        """Visit function declaration"""
        self.current_function = func
        
        # Create a special Token-like object for return type
        class TypeToken:
            def __init__(self, value):
                self.value = value
        
        # Special case for main function - default to ank (int) return type
        if func.name == "main" and func.return_type is None:
            self.current_function.return_type = TypeToken("ank")
        
        # Determine return type - default to "ank" for main function
        return_type = func.return_type.value if func.return_type else ("ank" if func.name == "main" else None)
        
        # Add function to symbol table
        self.symbols.define(func.name, return_type)
        
        # Process function body with new scope
        self.symbols.enter_scope()
        
        # Add parameters to scope
        for param in func.params:
            self.symbols.define(param.name, param.type.value)
        
        self.visit(func.body)
        self.symbols.exit_scope()
        self.current_function = None
    
    def visit_VarDeclaration(self, var_decl):
        """Visit variable declaration"""
        # Check if variable is already defined in current scope
        if var_decl.name in self.symbols.scopes[-1]:
            self.errors.append(f"Variable '{var_decl.name}' is already defined in this scope")
        
        # Validate initializer if present
        if var_decl.initializer:
            init_type = self.visit(var_decl.initializer)
            if not self.check_type_compatibility(var_decl.var_type.value, init_type):
                self.errors.append(f"Cannot assign {init_type} to variable '{var_decl.name}' of type {var_decl.var_type.value}")
        
        # Add to symbol table
        self.symbols.define(var_decl.name, var_decl.var_type.value)
    
    def visit_BlockStatement(self, block):
        """Visit block statement"""
        self.symbols.enter_scope()
        for statement in block.statements:
            self.visit(statement)
        self.symbols.exit_scope()
    
    def visit_IfStatement(self, if_stmt):
        """Visit if statement"""
        cond_type = self.visit(if_stmt.condition)
        if cond_type != "boolean":
            self.errors.append(f"Condition in if statement must be a boolean expression")
        
        self.visit(if_stmt.then_branch)
        if if_stmt.else_branch:
            self.visit(if_stmt.else_branch)
    
    def visit_WhileStatement(self, while_stmt):
        """Visit while statement"""
        cond_type = self.visit(while_stmt.condition)
        if cond_type != "boolean":
            self.errors.append(f"Condition in while statement must be a boolean expression")
        
        self.visit(while_stmt.body)
    
    def visit_ForStatement(self, for_stmt):
        """Visit for statement"""
        self.symbols.enter_scope()
        
        if for_stmt.initializer:
            self.visit(for_stmt.initializer)
        
        if for_stmt.condition:
            cond_type = self.visit(for_stmt.condition)
            if cond_type != "boolean":
                self.errors.append(f"Condition in for statement must be a boolean expression")
        
        if for_stmt.increment:
            self.visit(for_stmt.increment)
        
        self.visit(for_stmt.body)
        self.symbols.exit_scope()
    
    def visit_PrintStatement(self, print_stmt):
        """Visit print statement"""
        self.visit(print_stmt.expression)
    
    def visit_ReturnStatement(self, return_stmt):
        """Visit return statement"""
        if not self.current_function:
            self.errors.append(f"Return statement outside of function")
            return
        
        expected_type = self.current_function.return_type
        if expected_type is None:  # void function
            if return_stmt.value is not None:
                self.errors.append(f"Cannot return a value from a void function")
        else:
            if return_stmt.value is None:
                self.errors.append(f"Function must return a value of type {expected_type.value}")
            else:
                return_type = self.visit(return_stmt.value)
                if not self.check_type_compatibility(expected_type.value, return_type):
                    self.errors.append(f"Return type mismatch: expected {expected_type.value}, got {return_type}")
    
    def visit_ExpressionStatement(self, expr_stmt):
        """Visit expression statement"""
        self.visit(expr_stmt.expression)
    
    def visit_Assignment(self, assign):
        """Visit assignment"""
        var_type = self.symbols.lookup(assign.name)
        if var_type is None:
            self.errors.append(f"Variable '{assign.name}' is not defined")
            return "unknown"
        
        value_type = self.visit(assign.value)
        if not self.check_type_compatibility(var_type, value_type):
            self.errors.append(f"Cannot assign {value_type} to variable '{assign.name}' of type {var_type}")
        
        return var_type
    
    def visit_Logical(self, logical):
        """Visit logical expression"""
        left_type = self.visit(logical.left)
        right_type = self.visit(logical.right)
        
        if left_type != "boolean" or right_type != "boolean":
            self.errors.append(f"Logical operators require boolean operands")
        
        return "boolean"
    
    def visit_Binary(self, binary):
        """Visit binary expression"""
        left_type = self.visit(binary.left)
        right_type = self.visit(binary.right)
        op = binary.operator.value
        
        # Comparison operators
        if op in ["<", ">", "<=", ">=", "==", "!="]:
            # Type compatibility for comparison
            if not self.check_type_compatibility(left_type, right_type):
                self.errors.append(f"Cannot compare {left_type} with {right_type}")
            return "boolean"
        
        # Arithmetic operators
        elif op in ["+", "-", "*", "/", "%"]:
            # Special case for string concatenation
            if op == "+" and (left_type == "vakya" or right_type == "vakya"):
                return "vakya"
                
            # Numeric operations
            if not (self.is_numeric_type(left_type) and self.is_numeric_type(right_type)):
                self.errors.append(f"Operator '{op}' requires numeric operands")
            
            # Return the more precise type (float > int)
            if left_type == "sankhya" or right_type == "sankhya":
                return "sankhya"
            return "ank"
        
        return "unknown"
    
    def visit_Unary(self, unary):
        """Visit unary expression"""
        operand_type = self.visit(unary.right)
        op = unary.operator.value
        
        if op == "-":
            if not self.is_numeric_type(operand_type):
                self.errors.append(f"Unary '{op}' requires numeric operand")
            return operand_type
        elif op == "nahi":
            if operand_type != "boolean":
                self.errors.append(f"Unary 'nahi' requires boolean operand")
            return "boolean"
        
        return "unknown"
    
    def visit_Call(self, call):
        """Visit function call"""
        callee = call.callee
        if not isinstance(callee, Variable):
            self.errors.append(f"Cannot call a non-function value")
            return "unknown"
        
        func_name = callee.name
        func_type = self.symbols.lookup(func_name)
        
        if func_type is None:
            # Special case for built-in likho function
            if func_name == "likho":
                for arg in call.arguments:
                    self.visit(arg)
                return "void"
            
            self.errors.append(f"Function '{func_name}' is not defined")
            return "unknown"
        
        # TODO: Check argument count and types when we have function parameters
        
        return func_type
    
    def visit_Variable(self, variable):
        """Visit variable reference"""
        var_type = self.symbols.lookup(variable.name)
        if var_type is None:
            self.errors.append(f"Variable '{variable.name}' is not defined")
            return "unknown"
        
        # Annotate the variable node with its type for code generation
        variable.type = var_type
        return var_type
    
    def visit_Literal(self, literal):
        """Visit literal"""
        value = literal.value
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            return "ank"
        elif isinstance(value, float) or (isinstance(value, str) and self.is_float(value)):
            return "sankhya"
        elif isinstance(value, str):
            # Check if it's a character (single character in quotes)
            if len(value) == 1:
                return "akshar"
            # Otherwise treat as string
            return "vakya"
        return "unknown"
    
    def visit_Grouping(self, grouping):
        """Visit expression grouping"""
        return self.visit(grouping.expression)
    
    # Helper methods
    def is_float(self, value):
        """Check if a string represents a float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def is_numeric_type(self, type_name):
        """Check if a type is numeric"""
        return type_name in ["ank", "sankhya"]
    
    def check_type_compatibility(self, expected, actual):
        """Check if types are compatible for assignment or comparison"""
        # Same types are always compatible
        if expected == actual:
            return True
        
        # Numeric type compatibility
        if expected == "sankhya" and actual == "ank":
            return True  # Int can be assigned to float
        
        # For now, we don't allow any other implicit conversions
        return False


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    
    # Example source code
    source = """
    vidhi main() {
        ank x = 5;
        sankhya y = 3.14;
        vakya message = "Hello, world!";
        
        # Type error - assigning string to int
        ank z = "Hello";
        
        # Undefined variable
        likho(undefined_var);
        
        # Type error in condition
        agar (x + y) {
            likho("This will cause an error");
        }
        
        # Type error in arithmetic
        ank result = x + message;
        
        wapas 0;
    }
    """
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        print("Semantic analysis passed!")
    else:
        print("Semantic analysis failed with errors.")