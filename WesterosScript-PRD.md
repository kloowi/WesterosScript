Product Requirements Document (PRD)
WesterosScript: A Game of Thrones Programming Language
1. Product Overview
WesterosScript is a custom programming language inspired by the world of Game of Thrones. It transforms traditional programming constructs into thematic elements from the political and mystical culture of Westeros.
Instead of generic keywords like int, print, or if, WesterosScript uses immersive terms such as coin, raven, and council.
The language is designed primarily as an educational compiler project, demonstrating the three major stages of compilation:
Lexical Analysis – identifying tokens from the language vocabulary
Syntax Analysis – verifying the grammar of statements
Semantic Analysis – validating types and binding variables to memory
To enhance clarity and creativity, the compiler includes a Maester Explainability Layer, where the compiler narrates its actions as if a Maester from the Citadel is analyzing royal decrees.

2. Product Vision
The goal of WesterosScript is to:
Demonstrate compiler design concepts
Create a memorable and creative programming language
Provide transparent compiler reasoning through a themed Explainability Layer
Showcase advanced features beyond the minimum requirements

3. Target Users
Primary users:
Computer Science students studying Programming Languages
Developers learning compiler architecture
Demonstrations for programming language design

4. Language Philosophy
WesterosScript follows three guiding principles:
Immersion
All keywords are inspired by the culture and governance of Westeros.
Readability
Statements resemble royal decrees or orders to the realm.
Explainability
The compiler explains every decision through a Maester narrative system.

5. Basic Program Structure
A WesterosScript program represents decrees issued from the Iron Throne.
Example:
coin gold claims 100!
scroll name claims "Arya"!
raven gold!


6. Core Language Rules
Statement Format
All variable declarations follow this grammar:
[DATATYPE] [IDENTIFIER] [ASSIGNMENT] [VALUE] [DELIMITER]

Example:
coin gold claims 100!

Meaning:
int gold = 100;


7. Data Types
WesterosScript
Traditional Type
Description
coin
integer
Whole numbers
dragon_gold
float
Decimal numbers
scroll
string
Text
oath
boolean
true/false values
ledger
array
Collection of values

Example:
coin soldiers claims 500!
dragon_gold treasury claims 9999.75!
scroll king claims "Joffrey"!
oath winter claims true!


8. Operators
WesterosScript
Meaning
Equivalent
claims
assignment
=
unite
addition
+
clash
subtraction
-
forge
multiplication
*
divide_realm
division
/
equals
equality
==
greater_than
greater than
>
less_than
less than
<

Example:
coin gold claims 10 unite 5!

Equivalent:
int gold = 10 + 5;


9. Input and Output
Output
Keyword: raven
Example:
raven gold!

Meaning:
print(gold)


Input
Keyword: summon
Example:
summon name!

Meaning:
input(name)


10. Conditional Statements
Conditional logic is governed by the Small Council.
If Statement
Keyword: council
Example:
council gold greater_than 100 then
    raven "The treasury is strong!"
otherwise
    raven "The crown is poor."
end!


11. Loops
While Loop
Keyword: while_winter
Example:
while_winter gold less_than 10
    gold claims gold unite 1!
end!

Meaning:
while(gold < 10){
    gold = gold + 1;
}


12. Functions
Functions are forged like weapons.
Keyword: forge
Example:
forge add_coin
    coin result claims 10 unite 5!
    deliver result!
end!


13. Object-Oriented System
Classes represent Great Houses of Westeros.
Keyword: great_house
Example:
great_house Stark
    coin honor claims 100!
end!

Object creation:
heir jon claims Stark!

Inheritance:
bloodline Bolton inherits Stark!


14. Comments
Single Line
whisper This is a secret comment

Multi-line
chronicle
The history of this code
is recorded in the Citadel
end!


15. Compiler Architecture
The WesterosScript compiler is implemented in Python and follows a traditional three-phase compiler pipeline.
User Code
   ↓
Lexer
   ↓
Parser
   ↓
Semantic Analyzer
   ↓
Symbol Table
   ↓
Explainability Layer Output


16. Lexical Analysis (The Maesters Read the Scroll)
The Lexer scans the code and identifies tokens.
Example input:
coin gold claims 100!

Output:
--- THE MAESTERS EXAMINE THE SCROLL ---

[MAESTER] I have discovered the word 'coin'.
[MAESTER] This represents a DATATYPE in the realm.

[MAESTER] The name 'gold' appears to be a treasury identifier.

[MAESTER] The decree uses the word 'claims'.
[MAESTER] This is the sacred assignment operator.

[MAESTER] The value '100' is recognized as NUMERIC WEALTH.

[MAESTER] The rune '!' marks the end of the royal decree.

✓ The Maesters have finished reading the scroll.


17. Syntax Analysis (Council Validation)
The parser checks if the statement matches the rule:
[DATATYPE] [ID] [ASSIGN] [VALUE] [DELIMITER]

Example output:
--- THE SMALL COUNCIL REVIEWS THE DECREE ---

[COUNCIL] Expected royal structure:
[DATATYPE] [IDENTIFIER] [ASSIGNMENT] [VALUE] [DELIMITER]

[COUNCIL] The decree follows the ancient laws of syntax.

✓ The council approves the structure.


18. Semantic Analysis (Binding the Realm)
The semantic analyzer verifies types and stores variables.
Example:
--- THE CITADEL RECORDS THE DECREE ---

[MAESTER] The variable 'gold' is declared as type 'coin'.
[MAESTER] The value '100' is numeric wealth.

[MAESTER] Types are compatible.

[MAESTER] Recording 'gold' into the Great Ledger.


19. Symbol Table (The Great Ledger)
The symbol table stores all variables.
Example output:
--- THE GREAT LEDGER OF THE REALM ---

NAME      TYPE        VALUE
gold      coin        100
name      scroll      Arya
winter    oath        true


20. Error Handling
Syntax Error Example
Input:
coin gold claims 100

Output:
[MAESTER WARNING]

The decree lacks the sacred ending rune '!'.

Recovery Strategy: The Citadel inserts the missing rune.


Semantic Error Example
Input:
coin gold claims "rich"!

Output:
[FATAL BETRAYAL]

Variable 'gold' is of type 'coin',
yet the value '"rich"' is a scroll (string).

The Citadel refuses this decree.


21. Multi-Statement Support
WesterosScript supports multiple decrees in a program:
Example:
coin gold claims 100!
scroll name claims "Arya"!
raven gold!

The compiler processes each decree sequentially.

22. Example Program
coin gold claims 50!
scroll name claims "Tyrion"!

council gold greater_than 10 then
    raven "The Lannisters send their regards."
otherwise
    raven "The treasury is empty."
end!


23. Creative Features (Beyond Minimum)
Maester Narration System
Compiler explains every step in immersive storytelling form.
Symbol Table Visualization
Displays the Great Ledger of the Realm.
Error Recovery
Automatically repairs missing delimiters.
Object-Oriented Houses
Supports Great Houses and heirs.

24. Execution Scenarios for Screenshots
Scenario 1 – Valid Code
coin gold claims 100!

Scenario 2 – Syntax Error
coin gold claims 100

Scenario 3 – Semantic Error
coin gold claims "rich"!

These satisfy the required demonstration scenarios.

25. WesterosScript Cheat Sheet
Data Types
coin → integer
dragon_gold → float
scroll → string
oath → boolean
ledger → array


Assignment
claims

Example:
coin gold claims 100!


Delimiter
!


Output
raven gold!


Input
summon name!


If Statement
council condition then
    statement
otherwise
    statement
end!


While Loop
while_winter condition
    statement
end!


Class
great_house Stark
    coin honor claims 100!
end!




