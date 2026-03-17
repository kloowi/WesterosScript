from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TypeName(str, Enum):
    COIN = "coin"
    DRAGON_GOLD = "dragon_gold"
    SCROLL = "scroll"
    OATH = "oath"
    LEDGER = "ledger"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Program:
    statements: list["Stmt"]


class Stmt:
    pass


class Expr:
    pass


@dataclass(frozen=True)
class VarDecl(Stmt):
    type_name: TypeName
    name: str
    initializer: Expr


@dataclass(frozen=True)
class Assign(Stmt):
    name: str
    value: Expr


@dataclass(frozen=True)
class Raven(Stmt):
    value: Expr


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]


@dataclass(frozen=True)
class Council(Stmt):
    """
    `council <condition> then <then_block> (another_path <condition> then <block>)* (otherwise <block>)? end!`
    """

    branches: list[tuple[Expr, Block]]  # (condition, block)
    otherwise_block: Block | None


@dataclass(frozen=True)
class WhileWinter(Stmt):
    condition: Expr
    body: Block


@dataclass(frozen=True)
class ForEachHouse(Stmt):
    """
    `for_each_house (coin|dragon_gold)? <name> claims <start> until_spring <end> then <block> end!`

    Semantics (initial milestone):
    - Initializes `<name>` to `<start>` (coerced to coin/int)
    - Repeats while `<name> < <end>` (end is evaluated once at loop entry)
    - Auto-increments `<name>` by 1 after each iteration
    """

    type_name: TypeName
    name: str
    start: Expr
    end: Expr
    body: Block


@dataclass(frozen=True)
class BreakChain(Stmt):
    pass


@dataclass(frozen=True)
class ContinueMarch(Stmt):
    pass


@dataclass(frozen=True)
class Literal(Expr):
    value: object


@dataclass(frozen=True)
class Identifier(Expr):
    name: str


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass(frozen=True)
class Compare(Expr):
    left: Expr
    op: str  # equals / greater_than / less_than
    right: Expr

