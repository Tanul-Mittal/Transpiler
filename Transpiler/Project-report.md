# Hinglish to C Transpiler - Project Report

## Project Overview
The Hinglish to C Transpiler is a compiler that translates programs written in "Hinglish" (a programming language with Hindi-English hybrid syntax) into C code. This transpiler enables programmers to write code using natural Hindi-inspired keywords while leveraging the performance and compatibility of C.

## Architecture
The transpiler follows a classic compiler pipeline with four main stages:
1. **Lexical Analysis** - Tokenizing the source code
2. **Parsing** - Building an Abstract Syntax Tree (AST)
3. **Semantic Analysis** - Checking semantics and building symbol tables
4. **Code Generation** - Producing equivalent C code

## Components

### 1. Lexer (`lexer.py`)
The lexer performs lexical analysis by breaking the source code into tokens.

**Key features:**
- Converts Hinglish keywords (`agar`, `nahi_to`, `vidhi`, etc.) into their respective token types
- Identifies literals (integers, floats, strings, characters)
- Recognizes operators, delimiters, and identifiers
- Handles comments and whitespace
- Tracks line and column positions for error reporting

### 2. Parser (`parser.py`)
The parser converts the token stream into an Abstract Syntax Tree (AST).

**Key features:**
- Implements a recursive descent parser for the Hinglish language grammar
- Builds a hierarchical representation of the program structure
- Handles expressions with proper operator precedence
- Parses function declarations, statements, and control structures

### 3. Semantic Analyzer (`sem_analyser.py`)
The semantic analyzer checks for semantic errors and builds symbol tables.

**Key features:**
- Validates variable declarations and function calls
- Ensures type compatibility in expressions and assignments
- Builds a symbol table for scope management
- Checks for undefined variables and functions

### 4. Code Generator (`generator.py`)
The code generator translates the AST into equivalent C code.

**Key features:**
- Maps Hinglish language constructs to C constructs
- Preserves program semantics during translation
- Generates readable and maintainable C code

### 5. Compiler Interface (`compiler.py`)
The main interface that ties all components together and provides a user-friendly CLI.

**Key features:**
- Processes command-line arguments
- Orchestrates the compilation pipeline
- Handles file I/O operations
- Compiles generated C code using GCC
- Provides options for keeping intermediate files and running the compiled program

## Language Features
The Hinglish language supports:

1. **Data Types**:
   - `ank` (integer)
   - `sankhya` (float)
   - `vakya` (string)
   - `akshar` (character)

2. **Control Structures**:
   - `agar`/`nahi_to` (if/else) conditionals
   - `jabtak` (while) loops
   - `karo` (for) loops

3. **Functions**:
   - Function declaration with `vidhi` keyword
   - Parameters and return values
   - Return statements with `wapas` keyword

4. **Operations**:
   - Arithmetic operations (+, -, *, /, %)
   - Logical operations (`aur` for AND, `ya` for OR, `nahi` for NOT)
   - Comparison operations (==, !=, <, >, <=, >=)

5. **Output**:
   - Print statements with `likho` keyword

## Compilation Process
1. The source code is read from a `.hp` file
2. Lexer tokenizes the source code
3. Parser builds an AST from the tokens
4. Semantic analyzer validates the AST and builds symbol tables
5. Code generator translates the AST to C code
6. GCC compiles the C code into an executable
7. Optionally, the executable is run automatically

## Deployment
The project can be used as a Python script or compiled into a standalone binary using Nuitka for easier distribution.

## Conclusion
The Hinglish to C Transpiler demonstrates how programming languages can incorporate natural language elements while maintaining the performance benefits of compiled languages. This project serves as both an educational tool for understanding compiler design and as a practical tool for programmers who prefer using Hindi-inspired syntax.
