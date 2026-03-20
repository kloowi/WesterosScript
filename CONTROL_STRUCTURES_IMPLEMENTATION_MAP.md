# WesterosScript Control Structures - Implementation Map

## File References

### 1. Token Definitions
**File:** [tokens.py](src/westerosscript/tokens.py)

**Control Structure Tokens:**
- Line 23: `COUNCIL = auto()` - if keyword
- Line 24: `ANOTHER_PATH = auto()` - else if keyword
- Line 25: `THEN = auto()` - separator/block opener
- Line 26: `OTHERWISE = auto()` - else keyword
- Line 29: `FOR_EACH_HOUSE = auto()` - for keyword
- Line 31: `WHILE_WINTER = auto()` - while keyword
- Line 32: `BREAK_CHAIN = auto()` - break keyword
- Line 33: `CONTINUE_MARCH = auto()` - continue keyword
- Line 14: `LBRACE = auto()` - { 
- Line 15: `RBRACE = auto()` - }

**Keyword Mappings (Lines 36-81):**
- "council" → TokenType.COUNCIL
- "another_path" → TokenType.ANOTHER_PATH
- "then" → TokenType.THEN
- "otherwise" → TokenType.OTHERWISE
- "while_winter" → TokenType.WHILE_WINTER
- "for_each_house" → TokenType.FOR_EACH_HOUSE
- "break_chain" → TokenType.BREAK_CHAIN
- "continue_march" → TokenType.CONTINUE_MARCH

---

### 2. AST Node Definitions
**File:** [ast.py](src/westerosscript/ast.py)

**Control Structure Nodes:**
- Lines 36-38: `Block` - represents `{ statements }`
- Lines 41-49: `Council` - if/else if/else structure
- Lines 52-54: `WhileWinter` - while loop
- Lines 57-66: `ForEachHouse` - for loop
- Lines 69-70: `BreakChain` - break statement
- Lines 73-74: `ContinueMarch` - continue statement

**Node Details:**
```python
class Block(Stmt):
    statements: list[Stmt]

class Council(Stmt):
    branches: list[tuple[Expr, Block]]  # (condition, block) pairs
    otherwise_block: Block | None

class WhileWinter(Stmt):
    condition: Expr
    body: Block

class ForEachHouse(Stmt):
    type_name: TypeName
    name: str
    start: Expr
    end: Expr
    body: Block

class BreakChain(Stmt):
    pass

class ContinueMarch(Stmt):
    pass
```

---

### 3. Parser Implementation
**File:** [parser.py](src/westerosscript/parser.py)

**Control Structure Parsing Methods:**

#### IF/ELSE IF/ELSE
- **Lines 76-82:** `if self._match(TokenType.COUNCIL):` - entry point
- **Lines 263-281:** `_council_stmt()` - full implementation
  - Syntax: `council <cond> { <block> } (another_path <cond> { <block> })* (otherwise { <block> })?`
  - Creates branches list of (condition, block) tuples
  - Supports multiple `another_path` branches
  - Optional `otherwise` block

#### WHILE LOOP
- **Lines 83-86:** `if self._match(TokenType.WHILE_WINTER):` - entry point
- **Lines 283-287:** `_while_stmt()` - full implementation
  - Syntax: `while_winter <cond> { <block> }`
  - Evaluates condition, executes body block if true

#### FOR LOOP
- **Lines 87-90:** `if self._match(TokenType.FOR_EACH_HOUSE):` - entry point
- **Lines 289-302:** `_for_each_house_stmt()` - full implementation
  - Syntax: `for_each_house (coin|stag)? <name> claims <start> then <end> { <block> }`
  - Optional type specification (defaults to coin)
  - Stores start/end as Expr (evaluated at runtime)
  - Creates ForEachHouse AST node

#### BREAK
- **Lines 91-93:** `if self._match(TokenType.BREAK_CHAIN):` - entry point
- Creates `BreakChain()` AST node
- Must be terminated with `!`

#### CONTINUE
- **Lines 94-96:** `if self._match(TokenType.CONTINUE_MARCH):` - entry point
- Creates `ContinueMarch()` AST node
- Must be terminated with `!`

#### BARE BLOCKS
- **Lines 99-103:** `if self._match(TokenType.LBRACE):` - entry point
- **Lines 304-311:** `_curly_block()` - block parsing implementation
  - Accumulates statements until `}`
  - Handles nested blocks recursively

---

### 4. Semantic Analysis
**File:** [semantic.py](src/westerosscript/semantic.py)

**Control Structure Analysis:**

#### Block Scoping
- **Lines 91-103:** `_stmt()` for `ast.Block`
  - Calls `self._push_scope()` before entering block
  - Recursively analyzes block statements
  - Calls `self._pop_scope()` on completion
  - Line 95: `_scope_depth` incremented
  - Line 99: `_offset_stack` extended and reset

#### Council Analysis
- **Lines 105-122:** `_stmt()` for `ast.Council`
  - Ensures each branch condition is valid oath (comparison)
  - Each branch gets own scope via `_push_scope()`/`_pop_scope()`
  - Otherwise block also gets separate scope

#### While Analysis
- **Lines 124-135:** `_stmt()` for `ast.WhileWinter`
  - Calls `_ensure_oath()` to validate condition (lines 225-232)
  - Loop body gets new scope
  - Detects type errors in condition

#### For Loop Analysis
- **Lines 137-163:** `_stmt()` for `ast.ForEachHouse`
  - Validates start/end are numeric (coin or stag)
  - Creates loop scope
  - Records loop variable as coin type
  - Type-checks body in loop scope

#### Break/Continue Analysis
- **Lines 165-167:** `_stmt()` for `ast.BreakChain | ContinueMarch`
  - No semantic restrictions (validation at runtime)

#### Condition Validation
- **Lines 225-232:** `_ensure_oath()` method
  - Validates condition expressions
  - Allows Compare nodes directly
  - Evaluates other expressions for type validity

---

### 5. Runtime Interpreter
**File:** [interpreter.py](src/westerosscript/interpreter.py)

**Block Execution:**
- **Lines 108-116:** `_stmt()` for `ast.Block`
  - Calls `self.ledger.enter_scope("block")`
  - Executes all statements
  - Calls `self.ledger.exit_scope()` in finally block

**Council (If/Else) Execution:**
- **Lines 118-128:** `_stmt()` for `ast.Council`
  - Iterates through branches list
  - Evaluates condition: `if bool(self._eval(cond)):`
  - Executes matching block and returns
  - If all conditions false, executes `otherwise_block` if present

**While Loop Execution:**
- **Lines 130-145:** `_stmt()` for `ast.WhileWinter`
  - Iteration cap: 10,000
  - Loop: `while bool(self._eval(stmt.condition)):`
  - Catches `_LoopContinue` exception - skips to next iteration
  - Catches `_LoopBreak` exception - breaks loop
  - Line 140-143: Cap check with output message

**For Loop Execution:**
- **Lines 147-175:** `_stmt()` for `ast.ForEachHouse`
  - Creates loop scope: `self.ledger.enter_scope("for_each_house_loop")`
  - Iteration cap: 100,000
  - Converts start/end to int: `int(self._eval(stmt.start))`
  - Loop: `while i < end:`
  - Records loop variable: `self.ledger.define(stmt.name, ast.TypeName.COIN, i)`
  - Auto-increments: `i += 1`
  - Catches `_LoopContinue` and `_LoopBreak`
  - Line 169-171: Cap check with output message

**Break Handling:**
- **Lines 177-178:** `_stmt()` for `ast.BreakChain`
  - Raises `_LoopBreak()` exception
  - Caught by while/for loop handlers

**Continue Handling:**
- **Lines 180-181:** `_stmt()` for `ast.ContinueMarch`
  - Raises `_LoopContinue()` exception
  - Caught by while/for loop handlers

**Loop Control Error Handling:**
- **Lines 49-51:** `run()` method
  - Catches `_LoopBreak` outside loops: error "break_chain used outside of a loop."
  - Catches `_LoopContinue` outside loops: error "continue_march used outside of a loop."

**Exception Definitions:**
- **Lines 10-11:** `_LoopBreak` exception - used to signal break
- **Lines 12-14:** `_LoopContinue` exception - used to signal continue

---

### 6. Exception Classes
**File:** [errors.py](src/westerosscript/errors.py)

**Diagnostic System:**
- Provides `DiagnosticSink` for error/warning reporting
- Used by parser, semantic analyzer to report control structure errors
- Example: "Expected '{' after council condition"

---

## Call Flow: Parsing a Control Structure

### Example: `council x greater_than 5 { raven 100! }`

1. **Lexer** ([lexer.py](src/westerosscript/lexer.py))
   - Tokenizes: COUNCIL, IDENTIFIER(x), GREATER_THAN, NUMBER(5), LBRACE, RAVEN, NUMBER(100), BANG, RBRACE

2. **Parser** ([parser.py](src/westerosscript/parser.py))
   - `_statement()` detects COUNCIL token
   - Calls `_council_stmt()`
   - Parses condition: `_expression()` → `_comparison()` → returns `Compare(Identifier("x"), "greater_than", Literal(5))`
   - Consumes LBRACE
   - Calls `_curly_block()` to parse body
   - Returns `Council(branches=[(Compare(...), Block(...))], otherwise_block=None)`

3. **Semantic Analyzer** ([semantic.py](src/westerosscript/semantic.py))
   - `_stmt()` detects `ast.Council`
   - Calls `_ensure_oath(cond)` to validate condition
   - `_eval()` on condition returns (bool_value, TypeName)
   - Pushes scope for each branch
   - Recursively analyzes branch statements

4. **Interpreter** ([interpreter.py](src/westerosscript/interpreter.py))
   - `_stmt()` detects `ast.Council`
   - Iterates branches
   - Evaluates condition: `bool(self._eval(Compare(...)))`
   - If true, executes block: `self._stmt(block, res)`
   - Block creates new scope and executes statements

---

## Data Flow: Loop Variable in For Loop

### Example: `for_each_house i claims 0 then 5 { raven i! }`

**Parsing:**
- Creates `ForEachHouse(type_name=COIN, name="i", start=Literal(0), end=Literal(5), body=Block(...))`

**Semantic Analysis:**
- Evaluates start/end expressions (compile-time if constant)
- Creates loop scope: `_push_scope()`
- Defines loop variable: `self.ledger.define("i", ast.TypeName.COIN, 0)`
- Analyzes body with "i" in scope

**Runtime Execution:**
- Creates loop scope: `self.ledger.enter_scope("for_each_house_loop")`
- Loop: evaluates start (0) and end (5)
- For i=0 to 4:
  - Defines i in loop scope: `self.ledger.define("i", TypeName.COIN, i)`
  - Executes body (accesses i via symbol lookup)
  - Exits loop scope: `self.ledger.exit_scope()` in finally
- Variable i not accessible after loop

---

## Symbol Table Integration

From [symbols.py](src/westerosscript/symbols.py):

```python
class GreatLedger:
    def enter_scope(self, scope_kind: str = "block") -> None:
        # Called by interpreter when entering block/loop
        # Creates new scope dict on _scope_stack
        
    def exit_scope(self) -> None:
        # Called by interpreter when exiting block/loop
        # Pops scope from _scope_stack
        
    def define(name, type_name, value) -> None:
        # Defines variable in current scope
        # Used by semantic analyzer and interpreter
```

**Control Structure Scope Usage:**
- **Block:** `enter_scope("block")` / `exit_scope()`
- **Council branches:** Each branch gets scope
- **WhileWinter body:** `enter_scope()` before body
- **ForEachHouse:** `enter_scope("for_each_house_loop")` with loop var defined

---

## Key Design Patterns

### 1. Curly Braces for Blocks
- All control structures use `{ }` as block delimiters
- Parser calls `_curly_block()` to parse block contents
- No keyword-based delimiters (like `then`/`end`)

### 2. Scope Creation at Multiple Levels
- Semantic analyzer: tracks `_scope_depth`
- Interpreter: calls `ledger.enter_scope()`/`exit_scope()`
- Result: proper variable scoping and shadowing

### 3. Exception-Based Loop Control
- Break/Continue implemented as exceptions
- `_LoopBreak` / `_LoopContinue` caught by loop handlers
- Not caught by non-loop code → error message

### 4. Expression Evaluation for Conditions
- All conditions evaluated via `self._eval(expr)`
- Result coerced to bool: `bool(self._eval(cond))`
- Allows flexible condition expressions

### 5. Safety Caps
- While loops: 10,000 iteration limit (line 140)
- For loops: 100,000 iteration limit (line 169)
- Prevents UI freezing on runaway loops

---

## Testing Entry Points

### Parse Only
```bash
wss analyze <file> --print-ast
```
Verifies parser creates correct AST nodes

### Parse + Semantic Check
```bash
wss analyze <file> --print-ledger
```
Verifies semantic analyzer runs scope tracking

### Full Execution
```bash
wss run <file>
```
Executes interpreter with control structures

---

## Common Issues & Debugging

### Issue: "break_chain used outside of a loop"
- Cause: `break_chain!` not inside while/for loop
- Fix: Check break position in AST, ensure it's inside WhileWinter or ForEachHouse node

### Issue: Loop doesn't terminate
- Cause: Condition never becomes false
- Fix: Ensure loop variable is updated each iteration

### Issue: Variable "not found" after loop
- Cause: Loop variable scoped to loop only
- Fix: Declare loop variable outside loop if needed after loop ends

### Issue: Wrong number of iterations
- Cause: Misunderstanding for_each_house range
- Fix: Remember: `claims start then end` is [start, end) - excludes end

