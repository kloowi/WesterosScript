from __future__ import annotations

from westerosscript.errors import DiagnosticSink
from westerosscript.explain import Explainer
from westerosscript.tokens import KEYWORDS, Token, TokenType


class Lexer:
    def __init__(self, source: str, *, explainer: Explainer, diags: DiagnosticSink, filename: str = "<source>") -> None:
        self.source = source
        self.explainer = explainer
        self.diags = diags
        self.filename = filename

        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.line_start_idx = 0

    def scan_tokens(self) -> list[Token]:
        self.explainer.section("THE MAESTERS EXAMINE THE SCROLL")
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self._col()))
        self.explainer.say("MAESTER", "✓ The Maesters have finished reading the scroll.")
        return self.tokens

    def _scan_token(self) -> None:
        c = self._advance()

        if c in {" ", "\r", "\t"}:
            return
        if c == "\n":
            self.line += 1
            self.line_start_idx = self.current
            return

        if c == "!":
            self._add(TokenType.BANG)
            return

        if c == "(":
            self._add(TokenType.LPAREN)
            return

        if c == ")":
            self._add(TokenType.RPAREN)
            return

        if c == '"':
            self._string()
            return

        if c == "'":
            self._char()
            return

        if c.isdigit():
            self._number()
            return

        if self._is_alpha(c):
            self._identifier()
            return

    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)

        # Comments (CHEATSHEET): whisper ... (single line)
        # Treat them as whitespace: do not emit tokens.
        if token_type == TokenType.WHISPER:
            # consume until end-of-line (but not the newline itself; _scan_token handles it)
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return

        self._add(token_type)

        # Maester narration for noteworthy discoveries
        if token_type in {
            TokenType.COIN,
            TokenType.STAG,
            TokenType.SCROLL,
            TokenType.OATH,
            TokenType.LEDGER,
        }:
            self.explainer.say("MAESTER", f"I have discovered the word {text!r}. This represents a DATATYPE in the realm.")
        elif token_type == TokenType.CLAIMS:
            self.explainer.say("MAESTER", "I have discovered the word 'claims'. This is the sacred assignment operator.")
        elif token_type == TokenType.IDENTIFIER:
            self.explainer.say("MAESTER", f"The name {text!r} appears to be a treasury identifier.")

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        # Check for invalid identifier starting with digit (e.g., "123abc")
        if self._peek().isalpha() or self._peek() == "_":
            self.diags.fatal(
                "Invalid identifier — identifiers cannot start with digits. "
                "An identifier must begin with a letter or underscore, not a number.",
                filename=self.filename,
                line=self.line,
                col=self._col_at(self.start)
            )
            # Still consume the malformed identifier to avoid cascading errors
            while self._peek().isalnum() or self._peek() == "_":
                self._advance()
            return

        lexeme = self.source[self.start : self.current]
        value = float(lexeme) if is_float else int(lexeme)
        self._add(TokenType.NUMBER, literal=value)
        self.explainer.say("MAESTER", f"The value {lexeme!r} is recognized as NUMERIC WEALTH.")

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self.line_start_idx = self.current + 1
            self._advance()

        if self._is_at_end():
            self.diags.fatal(
                "Unterminated string literal — expected closing '\"' before end of line.",
                filename=self.filename,
                line=self.line,
                col=self._col()
            )
            return

        # closing quote
        self._advance()

        value = self.source[self.start + 1 : self.current - 1]
        self._add(TokenType.STRING, literal=value)

    def _char(self) -> None:
        """Parse a single character literal in apostrophes."""
        if self._is_at_end():
            self.diags.fatal(
                "Unterminated char literal — expected character and closing apostrophe after opening apostrophe.",
                filename=self.filename,
                line=self.line,
                col=self._col()
            )
            return

        char = self._advance()
        
        if self._is_at_end() or self._peek() != "'":
            self.diags.fatal(
                "Char literal must contain exactly one character — expected closing apostrophe but found end of input or multiple characters.",
                filename=self.filename,
                line=self.line,
                col=self._col()
            )
            return
        
        # closing apostrophe
        self._advance()
        self._add(TokenType.STRING, literal=char)

    def _add(self, type_: TokenType, *, literal: object | None = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type_, text, literal, self.line, self._col_at(self.start)))

    def _advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _col(self) -> int:
        return (self.current - self.line_start_idx) + 1

    def _col_at(self, idx: int) -> int:
        return (idx - self.line_start_idx) + 1

    @staticmethod
    def _is_alpha(c: str) -> bool:
        return c.isalpha() or c == "_"

