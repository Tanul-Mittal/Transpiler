# parser.py

from lexer import *

# AST Node Definitions
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Program({self.statements})"

class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"ExprStmt({self.expression})"

class PrintStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"Print({self.expression})"

class BlockStatement(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"While({self.condition}, {self.body})"

class ForStatement(ASTNode):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body
    def __repr__(self):
        return f"For({self.initializer}, {self.condition}, {self.increment}, {self.body})"

class Binary(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"Binary({self.left}, {self.operator.value}, {self.right})"

class Unary(ASTNode):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"Unary({self.operator.value}, {self.right})"

class Grouping(ASTNode):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"Grouping({self.expression})"

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Literal({self.value})"

class Variable(ASTNode):
    def __init__(self, token):
        self.name = token.value
    def __repr__(self):
        return f"Variable({self.name})"

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"Assign({self.name}, {self.value})"

class VarDeclaration(ASTNode):
    def __init__(self, var_type, name, initializer):
        self.var_type = var_type
        self.name = name
        self.initializer = initializer
    def __repr__(self):
        return f"VarDecl({self.var_type.value}, {self.name}, {self.initializer})"

class FunctionDeclaration(ASTNode):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
    def __repr__(self):
        return f"FuncDecl({self.name}, {self.params}, {self.return_type}, {self.body})"

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class Parameter(ASTNode):
    def __init__(self, type_token, name):
        self.type = type_token
        self.name = name
    def __repr__(self):
        return f"Param({self.type.value}, {self.name})"

class Logical(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"Logical({self.left}, {self.operator.value}, {self.right})"

class Call(ASTNode):
    def __init__(self, callee, arguments):
        self.callee = callee  # The function being called
        self.arguments = arguments  # List of argument expressions
    def __repr__(self):
        return f"Call({self.callee}, {self.arguments})"


# Parser Implementation
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return Program(statements)

    def declaration(self):
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR):
            return self.var_declaration()
        if self.match(TokenType.FUNCTION):
            return self.function_declaration()
        return self.statement()

    def var_declaration(self):
        var_type = self.previous()
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.").value
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarDeclaration(var_type, name, initializer)

    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.").value
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            # Parse parameters
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                
                # Use the new consume_any method
                type_tokens = [TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR]
                param_type = self.consume_any(type_tokens, "Expect parameter type.")
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value
                parameters.append(Parameter(param_type, param_name))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Optional return type - also use consume_any here
        return_type = None
        if self.check(TokenType.INT) or self.check(TokenType.FLOAT) or \
           self.check(TokenType.STRING) or self.check(TokenType.CHAR):
            return_type = self.consume_any([TokenType.INT, TokenType.FLOAT, 
                                          TokenType.STRING, TokenType.CHAR], 
                                         "Expect return type.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body = BlockStatement(self.block())
        
        return FunctionDeclaration(name, parameters, return_type, body)

    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.PRINT):  # Add this case for likho
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStatement(self.block())
        return self.expression_statement()

    def print_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'likho'.")
        expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after print statement.")
        return PrintStatement(expr)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'agar'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStatement(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'jabtak'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body = self.statement()
        return WhileStatement(condition, body)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'karo'.")
        
        # Initialization: can be a var declaration or an expression
        if self.match(TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.CHAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        # Condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        # Increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        
        # Body
        body = self.statement()
        
        return ForStatement(initializer, condition, increment, body)

    def return_statement(self):
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStatement(value)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStatement(expr)

    def block(self):
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()
        if self.match(TokenType.ASSIGN):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                return Assignment(expr.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN, 
                         TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()  # Changed from self.primary()

    def call(self):
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            # Parse arguments
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return Call(callee, arguments)

    def primary(self):
        if self.match(TokenType.INTEGER_LITERAL, TokenType.FLOAT_LITERAL,
                      TokenType.STRING_LITERAL, TokenType.CHAR_LITERAL):
            return Literal(self.previous().value)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        # Friendly error message with token info
        token = self.peek()
        if token.type == TokenType.PRINT:
            self.error(token, "Unexpected 'likho'. Did you mean to use it as a statement?")
        else:
            self.error(token, "Expect expression.")

    # Utility methods
    def match(self, *token_types):
        for t in token_types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        self.error(self.peek(), message)

    def consume_any(self, token_types, message):
        """Consume any of the given token types."""
        for t in token_types:
            if self.check(t):
                return self.advance()
        self.error(self.peek(), message)

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        raise Exception(f"[line {token.line}] Error at '{token.value}': {message}")
def print_ast(node, indent=0):
    prefix = '  ' * indent
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
        return

    print(f"{prefix}{node.__class__.__name__}")

    # Go deeper for composite nodes
    for attr in vars(node):
        value = getattr(node, attr)
        if isinstance(value, ASTNode) or isinstance(value, list):
            print(f"{prefix}  {attr}:")
            print_ast(value, indent + 2)
        else:
            print(f"{prefix}  {attr}: {value}")


# Example of usage with your lexer
if __name__ == "__main__":
    # Suppose `source_code` is your input file string.
    source = """
    # This is a test program in the custom language
    
    vidhi main() {
        ank x = 5;
        sankhya y = 3.14;
        vakya message = "Hello, world!";
        akshar ch = 'A';
        agar (x < 10) {
            likho("x is less than 10");
        } nahi_to {
            likho("x is 10 or greater");
        }
        karo (ank i = 0; i < 5; i = i + 1) {
            y = y + i;
        }
        wapas 0;
    }
    """
    # Assuming you have already imported your Lexer and TokenType classes from lexer.py:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    # print("tokens by lexer:", tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    print("ast generated successfully!")
    print_ast(ast)
