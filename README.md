# LR(1) Parser Generator

**Authors**: Gabe Krishnadasan and Marissa Esteban  
**Date**: December 2023

## Description

This project implements an **LR(1) parser generator**, capable of parsing source files based on context-free grammars specified by the user. The parser constructs parse trees in a depth-first, pre-order traversal format. Additionally, it includes mechanisms for detecting and handling errors such as invalid tokens, syntax errors, and non-LR grammars.

## Features

- **LR Automaton**:
  - Constructs LR(1) parse tables and states from the given grammar.
  - Handles shift, reduce, and accept actions in the parsing process.
- **Error Handling**:
  - Detects and raises exceptions for invalid tokens, source file syntax errors, and non-LR grammars.
- **Parse Tree Construction**:
  - Generates a parse tree and outputs it as a depth-first, pre-order traversal of the tree nodes.
- **First and Follow Sets**:
  - Computes the First and Follow sets for all grammar symbols.
- **Modular Design**:
  - Includes well-defined classes for `Item`, `State`, `Rule`, and `Parser`.

## How It Works

1. **Input Files**:
   - **Lexical Specifications** (`tokens1.txt`): Defines terminals via regular expressions.
   - **Grammar Specifications** (`grammar1.txt`): Defines the context-free grammar, with rules separated into terminals, nonterminals, and productions.
   - **Source File** (`src1.txt`): Contains the source code or input to be parsed.
   - **Correct Results File** (`correct1.txt`): Contains the expected parse tree or exception type.

2. **Initialization**:
   - Reads grammar and token specifications.
   - Constructs First and Follow sets.
   - Builds LR(1) automaton states and parse tables.

3. **Parsing**:
   - Tokenizes the source file using the lexical specifications.
   - Uses the LR(1) automaton to process tokens and construct a parse tree.
   - Validates the parse tree against the expected output.

4. **Output**:
   - Prints the parse tree or raises an exception for errors.
