# WesterosScript Control Structures - Quick Reference

## All Available Control Structures

```
IF/ELSE IF/ELSE       council ... otherwise ... another_path
WHILE LOOP            while_winter <condition> { }
FOR LOOP              for_each_house name claims start then end { }
BREAK                 break_chain!
CONTINUE              continue_march!
BLOCKS                { }
```

---

## Exact Syntax Cheat Sheet

### IF/ELSE IF/ELSE
```westerosscript
council x greater_than 5 {
  raven "greater"!
}
another_path x less_than 5 {
  raven "less"!
}
otherwise {
  raven "equal"!
}
```

### WHILE LOOP
```westerosscript
coin i claims 0!
while_winter i less_than 10 {
  raven i!
  i claims i unite 1!
}
```

### FOR LOOP
```westerosscript
for_each_house i claims 0 then 10 {
  raven i!
}
```

### BREAK
```westerosscript
for_each_house i claims 0 then 100 {
  council i equals 5 {
    break_chain!
  }
}
```

### CONTINUE  
```westerosscript
for_each_house i claims 0 then 5 {
  council i equals 2 {
    continue_march!
  }
  raven i!
}
```

### BARE BLOCK
```westerosscript
{
  coin x claims 10!
  raven x!
}
```

---

## Condition Operators (For if/while)

| Keyword | Meaning |
|---------|---------|
| `equals` | equal to `==` |
| `greater_than` | greater than `>` |
| `less_than` | less than `<` |

Example: `council x greater_than 5 { }`

---

## Arithmetic Operators (In expressions)

| Keyword | Meaning |
|---------|---------|
| `unite` | addition `+` |
| `clash` | subtraction `-` |
| `forge` | multiplication `*` |
| `divide_realm` | division `/` |

Example: `coin result claims x unite y!`

---

## Key Rules

- **Every statement ends with `!`** (except if/while/for - those end with `}`)
- **All blocks use `{ }`** - no `then`/`end` delimiters
- **For loops auto-increment by 1** each iteration
- **For loops range is [start, end)** - includes start, excludes end
- **Each control structure block gets its own scope** - variables don't leak out
- **Safety caps:**
  - `while_winter`: 10,000 iterations max
  - `for_each_house`: 100,000 iterations max

---

## Loop Variable Scope

```westerosscript
coin x claims 10!            // Outer x

for_each_house i claims 0 then 5 {
  // i exists here, scoped to the loop
  raven i!
}
// i does NOT exist here

raven x!                     // Outer x still accessible
```

---

## Variable Types

- `coin` - integer
- `stag` - float
- `essence` - double
- `scroll` - string
- `oath` - character
- `ledger` - array (not implemented)

---

## Working Examples Quick Copy-Paste

### Count 0 to 4
```westerosscript
for_each_house i claims 0 then 5 {
  raven i!
}
```

### Conditional Output
```westerosscript
coin x claims 7!
council x greater_than 5 {
  raven "big"!
}
otherwise {
  raven "small"!
}
```

### Multiplication Table (1-3)
```westerosscript
for_each_house i claims 1 then 4 {
  for_each_house j claims 1 then 4 {
    raven i forge j!
  }
}
```

### While Loop Sum 0-4
```westerosscript
coin i claims 0!
coin sum claims 0!
while_winter i less_than 5 {
  sum claims sum unite i!
  i claims i unite 1!
}
raven sum!
```

### Skip Number 3
```westerosscript
for_each_house i claims 0 then 5 {
  council i equals 3 {
    continue_march!
  }
  raven i!
}
```

### Stop at 5
```westerosscript
for_each_house i claims 0 then 100 {
  council i equals 5 {
    break_chain!
  }
  raven i!
}
```

---

## Common Patterns

### Conditional with Multiple Paths
```westerosscript
council condition1 {
  // path 1
}
another_path condition2 {
  // path 2
}
another_path condition3 {
  // path 3
}
otherwise {
  // default path
}
```

### Nested Loops
```westerosscript
for_each_house i claims 0 then 3 {
  for_each_house j claims 0 then 3 {
    raven i forge j!
  }
}
```

### Loop with Early Exit
```westerosscript
for_each_house i claims 0 then 100 {
  council i greater_than 10 {
    break_chain!
  }
  raven i!
}
```

### Conditional Skip
```westerosscript
for_each_house i claims 0 then 10 {
  council i equals 5 {
    continue_march!
  }
  raven i!
}
```

---

## Implementation Status

✅ **WORKING:** council, while_winter, for_each_house, break_chain, continue_march, bare blocks
❌ **NOT IMPLEMENTED:** switch/case, do-while, return validation for loop control

