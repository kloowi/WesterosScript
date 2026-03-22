# WesterosScript

A Game of Thrones–themed educational compiler that teaches lexical analysis, parsing, semantic analysis, and program execution in a single cohesive project. Students experience the full compilation pipeline from source code to runtime output—seeing how each stage transforms the program step by step.

## Quick Start

**Prerequisites:** Python ≥ 3.11 (Windows: use `py` launcher)

**Analyze and run a program:**

```bash
wss analyze examples/valid.wss --run
```

This executes all five compilation stages and shows the output. Try it with any example file!

## Installation

### From Source (Recommended for Development)

```bash
pip install -e .
```

**Note:** Setup configuration files are still being added. If this command fails, use the alternative below.

### Alternative: Direct Module Execution

```bash
python -m westerosscript.cli analyze examples/valid.wss --run
```

This bypasses the installation and runs the compiler directly from the source tree.

## What Is WesterosScript?

WesterosScript is a **complete compiler** that demonstrates all stages of compilation:

| Stage | Theme | What It Does |
|-------|-------|--------------|
| **1. Lexical Analysis** | Maesters read the scroll | Breaks source into tokens (keywords, identifiers, operators, literals) |
| **2. Syntax Analysis** | Small Council validates | Parses tokens into an Abstract Syntax Tree (AST); checks grammar |
| **3. Semantic Analysis** | Citadel records the realm | Type-checks variables, validates scope, resolves symbol references |
| **4. Symbol Table** | Great Ledger | Tracks all declarations with types, values, and memory layout per scope |
| **5. Runtime Execution** | Raven delivers the word | Interprets the AST; executes the program and produces output |

Students can inspect the output from each stage to understand how a compiler transforms code.

## Using the Compiler

### Command-Line Interface

All commands use the format: `wss analyze <file> [flags]`

#### Basic Analysis (Default Behavior)

```bash
wss analyze examples/valid.wss
```

Shows all analysis stages (Lexical → Syntax → Semantic) and the symbol table. No execution happens.

#### Execute the Program

```bash
wss analyze examples/valid.wss --run
```

Runs all stages AND executes the program. Output appears in the **Raven** tab.

#### View Diagnostic Output

Include any of these flags to see additional details:

| Flag | Effect |
|------|--------|
| `--print-tokens` | Show the token stream from the lexer |
| `--print-ast` | Display the Abstract Syntax Tree |
| `--print-ledger` | Print the symbol table (enabled by default) |
| `--narration full` | Verbose output; explains each compilation step |
| `--narration minimal` | Quiet mode; minimal output |
| `--narration off` | Silent except for errors and execution output |

**Example: See tokens + run the program with verbose narration:**

```bash
wss analyze examples/valid.wss --run --print-tokens --narration full
```

### Desktop Application

Launch the interactive GUI:

```bash
py -m ui.desktop_app.main
```

**Features:**
- Code editor (load/save files)
- Single "Analyze" button to run all stages
- Tabbed output pane showing results from each compilation stage
- Five analysis tabs:
  - **Grand Maester** (Lexical): Tokens and lexical diagnostics
  - **Small Council** (Syntax): Parse tree and structural errors
  - **Citadel** (Semantic): Type errors, scope violations, symbol resolution
  - **Great Ledger** (Symbol Table): Variable declarations, types, memory layout
  - **Raven** (Runtime): Program output and execution results

## Language Reference

### Data Types

| Keyword | Type | Example |
|---------|------|---------|
| `coin` | 32-bit integer | `coin x claims 42!` |
| `stag` | 32-bit float | `stag height claims 5.5!` |
| `essence` | 64-bit double | `essence pi claims 3.14159!` |
| `scroll` | String | `scroll message claims "Hello Westeros"!` |
| `oath` | Single character | `oath initial claims 'A'!` |

### Declarations

**Variables with `claims`:**

```
coin gold claims 100!
stag tax claims gold forge 0.15!
```

**Constants with `sigil`:**

```
sigil coin MAX_DRAGONS claims 3!
```

Constants cannot be reassigned, and constant names cannot be redeclared in inner scopes.

### Operators

| Operator | Keyword | Example |
|----------|---------|---------|
| Addition | `unite` | `x unite 5` |
| Subtraction | `clash` | `x clash 3` |
| Multiplication | `forge` | `x forge 2` |
| Division | `divide_realm` | `x divide_realm 4` |
| Equals (comparison) | `equals` | `x equals 10` |
| Greater than | `greater_than` | `x greater_than 5` |
| Less than | `less_than` | `x less_than 20` |
| Assignment | `claims` | `x claims 7!` |

### Control Flow

**If/Else Chain:**

```
council x greater_than 50 {
  raven "High power"!
} another_path x equals 50 {
  raven "Balanced"!
} otherwise {
  raven "Low power"!
}
```

**For Loop (iteration count: max 100,000):**

```
for_each_house coin i claims 1 then 10 {
  raven i!
}
```

Loops from 1 to 10 (inclusive), printing each value.

**While Loop (iteration count: max 10,000):**

```
coin countdown claims 5!
while_winter countdown greater_than 0 {
  raven countdown!
  countdown claims countdown clash 1!
}
```

**Loop Control:**
- `break_chain` — Exit the loop immediately
- `continue_march` — Skip to next iteration

### Input & Output

**Output:**

```
raven "Prepare for winter"!
raven x!
```

**Input (via `summon`):**

```
summon x!
```

Prompts for a value and stores it in variable `x`.

### Functions

**Definition:**

```
decree coin add(coin a, coin b) {
  deliver a unite b!
}
```

**Return Statement:**

```
deliver <value>!
```

### Scope & Nesting

Curly braces `{ }` create new scopes. Variables declared in inner scopes shadow outer variables.

```
coin x claims 1!
{
  coin x claims 2!
  raven x!  // prints 2 (inner x)
}
raven x!    // prints 1 (outer x)
```

## Examples

The `examples/` directory contains programs demonstrating compiler concepts:

### Valid Programs

- **`valid.wss`** — Simple variable declaration and output
- **`valid_if_else.wss`** — If/else chain with conditional logic
- **`valid_for_loop.wss`** — Counting loop with iteration
- **`valid_while_loop.wss`** — While loop with decrement
- **`valid_scoping.wss`** — Nested scopes and variable shadowing
- **`valid_const_sigil.wss`** — Immutable constant declaration and usage

### Error Examples (for Learning)

**Syntax Errors:**
- `syntax_error_missing_bang.wss` — Missing `!` statement terminator
- `syntax_error_identifier_starts_with_digit.wss` — Invalid identifier (e.g., `1x`)
- `syntax_error_missing_delimiter.wss` — Unmatched brackets or quotes

**Semantic Errors:**
- `semantic_error_type_mismatch.wss` — Type mismatch in assignment
- `semantic_error_type_mismatch_declaration.wss` — Type mismatch in declaration
- `semantic_error_type_mismatch_assignment.wss` — Type mismatch in expression
- `semantic_error_const_reassignment.wss` — Attempted reassignment of a `sigil` constant
- `semantic_error_const_shadowing.wss` — Attempted redeclaration of a constant name in nested scope

**Run any example:**

```bash
wss analyze examples/valid_for_loop.wss --run
```

## Compiler Internals

### Project Structure

```
src/westerosscript/
  ├── lexer.py          # Tokenization (Maesters)
  ├── tokens.py         # Token definitions
  ├── parser.py         # AST construction (Small Council)
  ├── ast.py            # AST node classes
  ├── semantic.py       # Type checking & scope validation (Citadel)
  ├── symbols.py        # Symbol table and scope management (Great Ledger)
  ├── interpreter.py    # Program execution (Raven)
  ├── compiler.py       # Main pipeline orchestrator
  ├── cli.py            # Command-line interface
  ├── errors.py         # Error reporting
  └── explain.py        # Narration and diagnostics

ui/desktop_app/
  ├── main.py           # Tkinter GUI launcher
  ├── bridge.py         # Python↔UI communication
  └── webview_main.py   # (Reference implementation)
```

### Important Constraints

**Loop Iteration Caps:**
- While loops: maximum 10,000 iterations (prevents infinite loops)
- For loops: maximum 100,000 iterations

Exceeding these limits produces an error rather than hanging the program.

**Division by Zero:**
A runtime error is flagged if division by zero is attempted. The program halts at that statement.

### How to Extend

To add features, modify files in this order:

1. **tokens.py** — Add new token types
2. **lexer.py** — Add tokenization rules
3. **parser.py** — Add grammar rules and AST construction
4. **semantic.py** — Add type checking or validation rules
5. **interpreter.py** — Add execution logic
6. **cli.py** — Expose new flags if needed

Each stage is independent; changes in one rarely break others if interfaces are preserved.

## Educational Goals

This project demonstrates:
- **Lexical analysis:** How source text becomes tokens
- **Parsing:** How tokens become structured programs (ASTs)
- **Semantic analysis:** How to validate and type-check code
- **Symbol tables:** How to track variables and scopes
- **Interpretation:** How to execute code

By examining the output from each stage, students develop intuition for how modern compilers and interpreters work.

