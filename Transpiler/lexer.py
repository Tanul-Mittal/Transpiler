import re
from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    IF = auto()          # agar
    ELSE = auto()        # nahi_to
    WHILE = auto()       # jabtak
    FOR = auto()         # karo
    FUNCTION = auto()    # vidhi
    RETURN = auto()      # wapas
    PRINT = auto()       # likho
    
    # Logical operators
    AND = auto()         # aur
    OR = auto()          # ya
    NOT = auto()         # nahi
    
    # Data types
    INT = auto()         # ank
    FLOAT = auto()       # sankhya
    STRING = auto()      # vakya
    CHAR = auto()        # akshar
    
    # Literals
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    MULTIPLY = auto()    # *
    DIVIDE = auto()      # /
    MODULO = auto()      # %
    ASSIGN = auto()      # =
    EQUALS = auto()      # ==
    NOT_EQUALS = auto()  # !=
    LESS_THAN = auto()   # <
    GREATER_THAN = auto() # >
    LESS_EQUAL = auto()  # <=
    GREATER_EQUAL = auto() # >=
    
    # Delimiters
    LEFT_PAREN = auto()  # (
    RIGHT_PAREN = auto() # )
    LEFT_BRACE = auto()  # {
    RIGHT_BRACE = auto() # }
    SEMICOLON = auto()   # ;
    COMMA = auto()       # ,
    
    # Special
    EOF = auto()
    UNKNOWN = auto()

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Define keyword mappings
        self.keywords = {
            'agar': TokenType.IF,
            'nahi_to': TokenType.ELSE,
            'jabtak': TokenType.WHILE,
            'karo': TokenType.FOR,
            'vidhi': TokenType.FUNCTION,
            'wapas': TokenType.RETURN,
            'ank': TokenType.INT,
            'sankhya': TokenType.FLOAT,
            'vakya': TokenType.STRING,
            'akshar': TokenType.CHAR,
            'likho': TokenType.PRINT,
            
            # Logical operators
            'aur': TokenType.AND,
            'ya': TokenType.OR,
            'nahi': TokenType.NOT
        }

    def peek(self):
        """Look at the current character without consuming it"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def advance(self):
        """Consume the current character and return it"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return char
    
    def skip_whitespace(self):
        """Skip all whitespace characters"""
        while self.peek() and self.peek().isspace():
            self.advance()
    
    def skip_comment(self):
        """Skip a comment starting with #"""
        self.advance()  # Skip the # character
        
        # Skip until end of line
        while self.peek() and self.peek() != '\n':
            self.advance()
        
        # We don't consume the newline here, as it will be handled by skip_whitespace
    
    def tokenize(self):
        """Convert the source code into tokens"""
        while self.position < len(self.source):
            # Skip whitespace
            self.skip_whitespace()
            
            # Check if we've reached the end
            if self.position >= len(self.source):
                break
            
            char = self.peek()
            
            # Handle comments
            if char == '#':
                self.skip_comment()
                continue
            
            # Handle identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokenize_identifier()
            
            # Handle numbers
            elif char.isdigit():
                self.tokenize_number()
            
            # Handle string literals
            elif char == '"':
                self.tokenize_string()
            
            # Handle character literals
            elif char == "'":
                self.tokenize_char()
            
            # Handle operators and delimiters
            elif char in '+-*/(){}[];,=<>!':
                self.tokenize_operator_or_delimiter()
                
            # Unrecognized character
            else:
                self.tokens.append(Token(TokenType.UNKNOWN, char, self.line, self.column))
                self.advance()
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
    
    def tokenize_identifier(self):
        """Tokenize an identifier or keyword"""
        start_column = self.column
        identifier = ""
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            identifier += self.advance()
        
        # Check if it's a keyword
        if identifier in self.keywords:
            token_type = self.keywords[identifier]
        else:
            token_type = TokenType.IDENTIFIER
        
        self.tokens.append(Token(token_type, identifier, self.line, start_column))
    
    def tokenize_number(self):
        """Tokenize a number (integer or float)"""
        start_column = self.column
        number = ""
        is_float = False
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                if is_float:  # Second decimal point is invalid
                    break
                is_float = True
            
            number += self.advance()
        
        if is_float:
            self.tokens.append(Token(TokenType.FLOAT_LITERAL, number, self.line, start_column))
        else:
            self.tokens.append(Token(TokenType.INTEGER_LITERAL, number, self.line, start_column))
    
    def tokenize_string(self):
        """Tokenize a string literal"""
        start_column = self.column
        self.advance()  # Skip the opening quote
        string = ""
        
        while self.peek() and self.peek() != '"':
            # Handle escape sequences
            if self.peek() == '\\' and self.position + 1 < len(self.source):
                self.advance()  # Skip the backslash
                escaped_char = self.advance()
                
                if escaped_char == 'n':
                    string += '\n'
                elif escaped_char == 't':
                    string += '\t'
                elif escaped_char == '\\':
                    string += '\\'
                elif escaped_char == '"':
                    string += '"'
                else:
                    string += escaped_char
            else:
                string += self.advance()
        
        if self.peek() == '"':
            self.advance()  # Skip the closing quote
            self.tokens.append(Token(TokenType.STRING_LITERAL, string, self.line, start_column))
        else:
            # Unterminated string error handling
            self.tokens.append(Token(TokenType.UNKNOWN, string, self.line, start_column))
    
    def tokenize_char(self):
        """Tokenize a character literal"""
        start_column = self.column
        self.advance()  # Skip the opening quote
        
        char_value = ""
        
        # Handle escape sequences
        if self.peek() == '\\' and self.position + 1 < len(self.source):
            self.advance()  # Skip the backslash
            escaped_char = self.advance()
            
            if escaped_char == 'n':
                char_value = '\n'
            elif escaped_char == 't':
                char_value = '\t'
            elif escaped_char == '\\':
                char_value = '\\'
            elif escaped_char == "'":
                char_value = "'"
            else:
                char_value = escaped_char
        else:
            if self.peek():
                char_value = self.advance()
        
        # Check for closing quote
        if self.peek() == "'":
            self.advance()  # Skip the closing quote
            
            # Validate that it's a single character
            if len(char_value) == 1:
                self.tokens.append(Token(TokenType.CHAR_LITERAL, char_value, self.line, start_column))
            else:
                # Invalid character literal (empty or too long)
                error_msg = "Invalid character literal"
                self.tokens.append(Token(TokenType.UNKNOWN, error_msg, self.line, start_column))
        else:
            # Unterminated character literal
            self.tokens.append(Token(TokenType.UNKNOWN, char_value, self.line, start_column))
    
    def tokenize_operator_or_delimiter(self):
        """Tokenize operators and delimiters"""
        char = self.advance()
        column = self.column - 1
        
        # Two-character operators
        if char == '=' and self.peek() == '=':
            self.advance()
            self.tokens.append(Token(TokenType.EQUALS, "==", self.line, column))
        elif char == '!' and self.peek() == '=':
            self.advance()
            self.tokens.append(Token(TokenType.NOT_EQUALS, "!=", self.line, column))
        elif char == '<' and self.peek() == '=':
            self.advance()
            self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", self.line, column))
        elif char == '>' and self.peek() == '=':
            self.advance()
            self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", self.line, column))
        # Single-character operators and delimiters
        else:
            token_map = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
                '(': TokenType.LEFT_PAREN,
                ')': TokenType.RIGHT_PAREN,
                '{': TokenType.LEFT_BRACE,
                '}': TokenType.RIGHT_BRACE,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA
            }
            
            if char in token_map:
                self.tokens.append(Token(token_map[char], char, self.line, column))
            else:
                self.tokens.append(Token(TokenType.UNKNOWN, char, self.line, column))

# Example usage
def tokenize_file(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
    
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    return tokens

# Test function
if __name__ == "__main__":
    # You can add a simple test here if needed
    test_code = """
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
        
        agar (x >= 5 aur y <= 4.0) {
            likho("Condition met!");
        }
        
        agar (x == 5 ya y != 3.0) {
            likho("Or condition met!");
        }
        
        agar (nahi (x < 3)) {
            likho("Not condition met!");
        }
        
        jabtak (x > 0) {
            likho(x);
            x = x - 1;
        }
        
        karo (ank i = 0; i < 5; i = i + 1) {
            y = y + i;
        }
        
        wapas 0;
    }
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(token)