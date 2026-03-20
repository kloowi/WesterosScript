from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Single-character
    BANG = auto()  # !
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }

    # Literals / identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Keywords: types
    SIGIL = auto()  # constant modifier
    COIN = auto()  # int
    STAG = auto()  # float
    ESSENCE = auto()  # double
    SCROLL = auto()
    OATH = auto()

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
    WHILE_WINTER = auto()
    BREAK_CHAIN = auto()
    CONTINUE_MARCH = auto()
    DECREE = auto()  # function definition
    DELIVER = auto()  # return statement

    # Comments
    WHISPER = auto()

    # Operators / relations
    CLAIMS = auto()  # assignment
    UNITE = auto()  # +
    CLASH = auto()  # -
    # NOTE: `forge` is also used as multiplication; parser decides by context.
    DIVIDE_REALM = auto()  # /
    EQUALS = auto()  # ==
    GREATER_THAN = auto()  # >
    LESS_THAN = auto()  # <

    EOF = auto()


KEYWORDS: dict[str, TokenType] = {
    "sigil": TokenType.SIGIL,
    "coin": TokenType.COIN,
    "stag": TokenType.STAG,
    "essence": TokenType.ESSENCE,
    "scroll": TokenType.SCROLL,
    "oath": TokenType.OATH,
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
    "break_chain": TokenType.BREAK_CHAIN,
    "continue_march": TokenType.CONTINUE_MARCH,
    "decree": TokenType.DECREE,
    "deliver": TokenType.DELIVER,
    "whisper": TokenType.WHISPER,
    "claims": TokenType.CLAIMS,
    "unite": TokenType.UNITE,
    "clash": TokenType.CLASH,
    # `forge` is context-sensitive (function vs operator).
    "divide_realm": TokenType.DIVIDE_REALM,
    "equals": TokenType.EQUALS,
    "greater_than": TokenType.GREATER_THAN,
    "less_than": TokenType.LESS_THAN,
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

