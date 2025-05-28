# Hinglish to C Transpiler

This project implements a transpiler that converts code written in "Hinglish" (a simple programming language with Hindi-English syntax) to C code. The transpiler supports a variety of programming constructs and provides a complete pipeline from lexical analysis to code generation.

## Overview

The transpiler follows a traditional compiler pipeline:

1. **Lexical Analysis**: Tokenizes the source code
2. **Parsing**: Converts tokens into an Abstract Syntax Tree (AST)
3. **Semantic Analysis**: Checks for semantic errors and builds a symbol table
4. **Code Generation**: Translates the AST into C code

## Language Features

The Hinglish programming language supports:

- Variable declarations (`ank` for integers, `sankhya` for floats, `vakya` for strings, `akshar` for characters)
- Function declarations with parameters and return types
- Control flow statements (`agar`/`nahi_to` for if-else, `jabtak` for while loops, `karo` for for loops)
- Arithmetic and logical expressions
- Print statements (`likho`)
- Nested blocks and scoping

## Example
```bash
# This is a simple Fibonacci program in Hinglish

vidhi fibonacci(ank n) ank {
    agar (n <= 1) {
        wapas n;
    }
    wapas fibonacci(n - 1) + fibonacci(n - 2);
}

vidhi main() {
    likho("Fibonacci Series:");
    
    karo (ank i = 0; i < 10; i = i + 1) {
        likho(fibonacci(i));
    }
    
    wapas 0;
}
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/Transpiler.git
cd Transpiler
```
2. Make sure you have Python 3.6+ installed:
```bash
python --version
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Ensure you have GCC installed for compiling the generated C code:
```bash
gcc --version
```

## Usage

### 1. Using compiler.py (Full compilation pipeline)
```bash
python compiler.py input.hp [options]
```
Options:

* --`-o, --output NAME`:  Output executable name
* --`--keep-c`:  Keep intermediate C file
* --`-v, --verbose`: Enable verbose output
* --`sample SAMPLE`: Run a built-in sample program instead of reading from a file
* --`run`: Run the executable after compilation
Examples:
```bash
python compiler.py hello.hp                # Basic compilation
python compiler.py hello.hp -o greet       # Custom output name
python compiler.py hello.hp --keep-c       # Keep C file
python compiler.py hello.hp --run          # Run after compiling                     # List available samples
```

### 2. Using Standalone compiler
* replace `python compiler.py` by `./compiler.bin` and rest is same as second method of compilation.

## Creating a standalone compiler binary
You can create a standalone binary for the compiler using nuitka:
```bash 
# make sure you have install nuitka with "pip install nuitka" 
nuitka --standalone --onefile compiler.py
```

## Contributing
1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add some amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request
=======
