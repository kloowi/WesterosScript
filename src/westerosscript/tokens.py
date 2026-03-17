from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Single-character
    BANG = auto()  # !

    # Literals / identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Keywords: types
    SIGIL = auto()  # constant modifier
    COIN = auto()
    DRAGON_GOLD = auto()
    SCROLL = auto()
    OATH = auto()
    LEDGER = auto()

    # Keywords: statements
    RAVEN = auto()
    SUMMON = auto()
    COUNCIL = auto()
    ANOTHER_PATH = auto()
    THEN = auto()
    OTHERWISE = auto()
    END = auto()
    FOR_EACH_HOUSE = auto()
    FORGE = auto()
    DELIVER = auto()
    WHILE_WINTER = auto()
    UNTIL_SPRING = auto()
    BREAK_CHAIN = auto()
    CONTINUE_MARCH = auto()

    # Comments
    WHISPER = auto()
    CHRONICLE = auto()

    # OOP keywords (parsed later)
    GREAT_HOUSE = auto()
    HEIR = auto()
    BLOODLINE = auto()
    INHERITS = auto()

    # Operators / relations
    CLAIMS = auto()  # assignment
    UNITE = auto()  # +
    CLASH = auto()  # -
    # NOTE: `forge` is also used as multiplication; parser decides by context.
    DIVIDE_REALM = auto()  # /
    EQUALS = auto()  # ==
    GREATER_THAN = auto()  # >
    LESS_THAN = auto()  # <

    TRUE = auto()
    FALSE = auto()

    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "sigil": TokenType.SIGIL,
    "coin": TokenType.COIN,
    "dragon_gold": TokenType.DRAGON_GOLD,
    "scroll": TokenType.SCROLL,
    "oath": TokenType.OATH,
    "ledger": TokenType.LEDGER,
    "raven": TokenType.RAVEN,
    "summon": TokenType.SUMMON,
    "council": TokenType.COUNCIL,
    "another_path": TokenType.ANOTHER_PATH,
    "then": TokenType.THEN,
    "otherwise": TokenType.OTHERWISE,
    "end": TokenType.END,
    "for_each_house": TokenType.FOR_EACH_HOUSE,
    "forge": TokenType.FORGE,
    "deliver": TokenType.DELIVER,
    "while_winter": TokenType.WHILE_WINTER,
    "until_spring": TokenType.UNTIL_SPRING,
    "break_chain": TokenType.BREAK_CHAIN,
    "continue_march": TokenType.CONTINUE_MARCH,
    "whisper": TokenType.WHISPER,
    "chronicle": TokenType.CHRONICLE,
    "great_house": TokenType.GREAT_HOUSE,
    "heir": TokenType.HEIR,
    "bloodline": TokenType.BLOODLINE,
    "inherits": TokenType.INHERITS,
    "claims": TokenType.CLAIMS,
    "unite": TokenType.UNITE,
    "clash": TokenType.CLASH,
    # `forge` is context-sensitive (function vs operator).
    "divide_realm": TokenType.DIVIDE_REALM,
    "equals": TokenType.EQUALS,
    "greater_than": TokenType.GREATER_THAN,
    "less_than": TokenType.LESS_THAN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: object | None
    line: int
    col: int

    def __repr__(self) -> str:
        lit = f", literal={self.literal!r}" if self.literal is not None else ""
        return f"Token({self.type.name}, {self.lexeme!r}{lit}, {self.line}:{self.col})"

