from parser import *  # Import all AST node classes

class CodeGenerator:
    def __init__(self, symbol_table=None):
        self.c_code = []
        self.indent_level = 0
        self.symbol_table = symbol_table  # Store the symbol table
    
    def generate(self, program, symbol_table=None):
        """Convert AST to C code"""
        self.c_code = []
        self.indent_level = 0
        
        # Use provided symbol table or the one from initialization
        if symbol_table:
            self.symbol_table = symbol_table
            
        self.visit(program)
        return "\n".join(self.c_code)
    
    def indent(self):
        """Return the current indentation string"""
        return "    " * self.indent_level
    
    def visit(self, node):
        """Visit an AST node and dispatch to the appropriate method"""
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Default handler for unhandled node types"""
        raise Exception(f"No visit method defined for {type(node).__name__}")
    
    def visit_Program(self, program):
        """Generate code for a program node"""
        # Include standard headers
        self.c_code.append("#include <stdio.h>")
        self.c_code.append("#include <stdlib.h>")
        self.c_code.append("#include <string.h>")
        self.c_code.append("")
        
        # Generate code for all statements
        for statement in program.statements:
            self.visit(statement)
    
    def visit_FunctionDeclaration(self, func):
        """Generate code for a function declaration"""
        # Determine return type
        return_type = "int" if func.name == "main" or (func.return_type and func.return_type.value == "ank") else \
                      "float" if func.return_type and func.return_type.value == "sankhya" else \
                      "char*" if func.return_type and func.return_type.value == "vakya" else \
                      "char" if func.return_type and func.return_type.value == "akshar" else \
                      "void"
        
        # Build parameter list
        params = []
        for param in func.params:
            param_type = "int" if param.type.value == "ank" else \
                         "float" if param.type.value == "sankhya" else \
                         "char*" if param.type.value == "vakya" else \
                         "char"
            params.append(f"{param_type} {param.name}")
        
        param_list = ", ".join(params) if params else "void"
        
        # Function header
        self.c_code.append(f"{return_type} {func.name}({param_list}) {{")
        self.indent_level += 1
        
        # Function body
        self.visit(func.body)
        
        # Add default return for main if needed - FIX HERE
        if func.name == "main" and not any(isinstance(stmt, ReturnStatement) for stmt in func.body.statements):
            self.c_code.append(f"{self.indent()}return 0;")
        
        self.indent_level -= 1
        self.c_code.append("}")
        self.c_code.append("")
    
    def visit_VarDeclaration(self, var_decl):
        """Generate code for variable declarations"""
        var_type = "int" if var_decl.var_type.value == "ank" else \
                  "float" if var_decl.var_type.value == "sankhya" else \
                  "char*" if var_decl.var_type.value == "vakya" else \
                  "char"
        
        # Handle initialization if present
        if var_decl.initializer:
            initializer = self.visit(var_decl.initializer)
            
            # Type-specific handling for literals
            if isinstance(var_decl.initializer, Literal):
                value = var_decl.initializer.value
                
                # Integer type
                if var_type == "int":
                    # Remove any quotes that might have been added
                    if isinstance(initializer, str) and initializer.startswith('"') and initializer.endswith('"'):
                        initializer = initializer[1:-1]
                    self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = {initializer};")
                
                # Float type
                elif var_type == "float":
                    # Remove any quotes that might have been added
                    if isinstance(initializer, str) and initializer.startswith('"') and initializer.endswith('"'):
                        initializer = initializer[1:-1]
                    self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = {initializer};")
                
                # String type
                elif var_type == "char*":
                    # Ensure string literals are properly quoted
                    if not (initializer.startswith('"') and initializer.endswith('"')):
                        initializer = f'"{initializer}"'
                    self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = {initializer};")
                
                # Character type
                elif var_type == "char":
                    # Ensure character literals use single quotes
                    if initializer.startswith('"') and initializer.endswith('"') and len(initializer) == 3:
                        # Convert double quotes to single quotes for characters
                        initializer = f"'{initializer[1]}'"
                    elif not (initializer.startswith("'") and initializer.endswith("'")):
                        # Add single quotes if missing
                        initializer = f"'{initializer}'" if len(initializer) == 1 else f"'{initializer[0]}'"
                    self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = {initializer};")
            else:
                # Non-literal initializer (expressions, variables, etc.)
                self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = {initializer};")
        else:
            # Default initialization
            if var_type == "char*":
                self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = \"\";")
            elif var_type == "char":
                self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = '\\0';")
            else:
                self.c_code.append(f"{self.indent()}{var_type} {var_decl.name} = 0;")
    
    def visit_BlockStatement(self, block):
        """Generate code for a block of statements"""
        for statement in block.statements:
            self.visit(statement)
    
    def visit_ExpressionStatement(self, expr_stmt):
        """Generate code for an expression statement"""
        expr_code = self.visit(expr_stmt.expression)
        self.c_code.append(f"{self.indent()}{expr_code};")
    
    def visit_PrintStatement(self, print_stmt):
        """Generate code for print statements"""
        expr = self.visit(print_stmt.expression)
        
        # Try to determine the type of the expression
        if isinstance(print_stmt.expression, Literal):
            value = print_stmt.expression.value
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                self.c_code.append(f"{self.indent()}printf(\"%d\\n\", {expr});")
            elif isinstance(value, float) or self.is_float(value):
                self.c_code.append(f"{self.indent()}printf(\"%f\\n\", {expr});")
            elif isinstance(value, str):
                if len(value) == 1 and value.startswith("'") and value.endswith("'"):
                    # Character
                    self.c_code.append(f"{self.indent()}printf(\"%c\\n\", {expr});")
                else:
                    # String
                    self.c_code.append(f"{self.indent()}printf(\"%s\\n\", {expr});")
        elif isinstance(print_stmt.expression, Variable):
            var_name = print_stmt.expression.name
            
            # Use type annotation if available from semantic analyzer
            if hasattr(print_stmt.expression, 'type'):
                var_type = print_stmt.expression.type
            # Or look up in symbol table
            elif self.symbol_table:
                var_type = self.symbol_table.lookup(var_name)
            else:
                var_type = None
                
            if var_type == "vakya":
                self.c_code.append(f"{self.indent()}printf(\"%s\\n\", {expr});")
            elif var_type == "akshar":
                self.c_code.append(f"{self.indent()}printf(\"%c\\n\", {expr});")
            elif var_type == "ank":
                self.c_code.append(f"{self.indent()}printf(\"%d\\n\", {expr});")
            elif var_type == "sankhya":
                self.c_code.append(f"{self.indent()}printf(\"%f\\n\", {expr});")
            else:
                # Fall back to guessing based on variable name
                if var_name == 'message' or var_name.endswith('_msg') or var_name.endswith('_str'):
                    self.c_code.append(f"{self.indent()}printf(\"%s\\n\", {expr});")
                elif var_name == 'first' or var_name == 'ch' or (len(var_name) == 1 and var_name.isalpha()):
                    self.c_code.append(f"{self.indent()}printf(\"%c\\n\", {expr});")
                else:
                    self.c_code.append(f"{self.indent()}printf(\"%d\\n\", {expr});")
        else:
            # Default to integer for complex expressions
            self.c_code.append(f"{self.indent()}printf(\"%d\\n\", {expr});")
    
    def visit_IfStatement(self, if_stmt):
        """Generate code for if statements"""
        condition = self.visit(if_stmt.condition)
        self.c_code.append(f"{self.indent()}if ({condition}) {{")
        self.indent_level += 1
        self.visit(if_stmt.then_branch)
        self.indent_level -= 1
        
        if if_stmt.else_branch:
            self.c_code.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            self.visit(if_stmt.else_branch)
            self.indent_level -= 1
        
        self.c_code.append(f"{self.indent()}}}")
    
    def visit_WhileStatement(self, while_stmt):
        """Generate code for while statements"""
        condition = self.visit(while_stmt.condition)
        self.c_code.append(f"{self.indent()}while ({condition}) {{")
        self.indent_level += 1
        self.visit(while_stmt.body)
        self.indent_level -= 1
        self.c_code.append(f"{self.indent()}}}")
    
    def visit_ForStatement(self, for_stmt):
        """Generate code for for statements"""
        # Generate initializer
        initializer = ""
        if for_stmt.initializer:
            if isinstance(for_stmt.initializer, VarDeclaration):
                # Special handling for variable declaration initializers
                var_type = "int" if for_stmt.initializer.var_type.value == "ank" else \
                          "float" if for_stmt.initializer.var_type.value == "sankhya" else \
                          "char*" if for_stmt.initializer.var_type.value == "vakya" else \
                          "char"
                init_expr = self.visit(for_stmt.initializer.initializer) if for_stmt.initializer.initializer else "0"
                initializer = f"{var_type} {for_stmt.initializer.name} = {init_expr}"
            else:
                initializer = self.visit(for_stmt.initializer)
        
        # Generate condition
        condition = self.visit(for_stmt.condition) if for_stmt.condition else ""
        
        # Generate increment
        increment = self.visit(for_stmt.increment) if for_stmt.increment else ""
        
        # Generate the for loop
        self.c_code.append(f"{self.indent()}for ({initializer}; {condition}; {increment}) {{")
        self.indent_level += 1
        self.visit(for_stmt.body)
        self.indent_level -= 1
        self.c_code.append(f"{self.indent()}}}")
    
    def visit_ReturnStatement(self, return_stmt):
        """Generate code for return statements"""
        if return_stmt.value:
            value = self.visit(return_stmt.value)
            self.c_code.append(f"{self.indent()}return {value};")
        else:
            self.c_code.append(f"{self.indent()}return;")
    
    def visit_Binary(self, binary):
        """Generate code for binary expressions"""
        left = self.visit(binary.left)
        right = self.visit(binary.right)
        operator = binary.operator.value
        
        # Direct translation for most operators
        return f"({left} {operator} {right})"
    
    def visit_Logical(self, logical):
        """Generate code for logical expressions"""
        left = self.visit(logical.left)
        right = self.visit(logical.right)
        
        # Map logical operators to C
        if logical.operator.value == "aur":
            return f"({left} && {right})"
        elif logical.operator.value == "ya":
            return f"({left} || {right})"
        else:
            raise Exception(f"Unknown logical operator: {logical.operator.value}")
    
    def visit_Unary(self, unary):
        """Generate code for unary expressions"""
        right = self.visit(unary.right)
        
        # Map unary operators to C
        if unary.operator.value == "nahi":
            return f"(!{right})"
        elif unary.operator.value == "-":
            return f"(-{right})"
        else:
            raise Exception(f"Unknown unary operator: {unary.operator.value}")
    
    def visit_Grouping(self, grouping):
        """Generate code for grouped expressions"""
        expr = self.visit(grouping.expression)
        return f"({expr})"
    
    def visit_Literal(self, literal):
        """Generate code for literals"""
        value = literal.value
        
        # Handle different types of literals
        if isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, int):
            return str(value)  # Integer literals don't need quotes
        elif isinstance(value, float):
            return str(value)  # Float literals don't need quotes
        elif isinstance(value, str):
            # Try to parse numeric strings
            if value.isdigit():
                # If it's a string containing only digits, return without quotes
                return value
            elif self.is_float(value):
                # If it's a string containing a float, return without quotes
                return value
            else:
                # Handle actual string literals
                if value.startswith("'") and value.endswith("'") and len(value) == 3:
                    # Character literal - keep single quotes
                    return value
                elif value.startswith('"') and value.endswith('"'):
                    # Already quoted string - leave as is
                    return value
                else:
                    # Add quotes for regular strings
                    return f'"{value}"'
        elif value is None:
            return "NULL"
        else:
            # Try to see if it's a numeric string
            str_value = str(value)
            if str_value.isdigit() or self.is_float(str_value):
                return str_value
            else:
                return f'"{str_value}"'
    
    def visit_Variable(self, variable):
        """Generate code for variable references"""
        return variable.name
    
    def visit_Assignment(self, assign):
        """Generate code for assignment expressions"""
        value = self.visit(assign.value)
        return f"{assign.name} = {value}"
    
    def visit_Call(self, call):
        """Generate code for function calls"""
        callee = self.visit(call.callee)
        args = [self.visit(arg) for arg in call.arguments]
        return f"{callee}({', '.join(args)})"
    
    # Utility methods
    def is_float(self, value):
        """Check if a string can be parsed as a float"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False


# Example usage
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    from sem_analyser import SemanticAnalyzer
    import sys
    
    # Check for command line arguments
    if len(sys.argv) != 3:
        print("Usage: python generator.py input.hp output.c")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Read input file
        with open(input_file, 'r') as f:
            source = f.read()
        
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            print("Semantic analysis failed. Cannot generate code.")
            sys.exit(1)
        
        # Generate code
        generator = CodeGenerator()
        c_code = generator.generate(ast)
        
        # Write to output file
        with open(output_file, 'w') as f:
            f.write(c_code)
        
        print(f"Successfully translated {input_file} to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)