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

        if c.isdigit():
            self._number()
            return

        if self._is_alpha(c):
            self._identifier()
            return

        # Comments (PRD): whisper ... (single line) / chronicle ... end! (multi-line)
        # For milestone 1 we treat them as whitespace by skipping at parse-time later;
        # Here we just don't tokenize unknown punctuation.
        self.diags.warn(f"Unrecognized character {c!r} ignored.", filename=self.filename, line=self.line, col=self._col())

    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)

        # Comments (CHEATSHEET): whisper ... (single line) / chronicle ... end! (multi-line)
        # Treat them as whitespace: do not emit tokens.
        if token_type == TokenType.WHISPER:
            # consume until end-of-line (but not the newline itself; _scan_token handles it)
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return
        if token_type == TokenType.CHRONICLE:
            self._multiline_comment()
            return

        literal = None
        if token_type == TokenType.TRUE:
            literal = True
        elif token_type == TokenType.FALSE:
            literal = False

        self._add(token_type, literal=literal)

        # Maester narration for noteworthy discoveries
        if token_type in {
            TokenType.COIN,
            TokenType.DRAGON_GOLD,
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
            self.diags.fatal("Unterminated string literal.", filename=self.filename, line=self.line, col=self._col())
            return

        # closing quote
        self._advance()

        value = self.source[self.start + 1 : self.current - 1]
        self._add(TokenType.STRING, literal=value)

    def _multiline_comment(self) -> None:
        """
        Consume characters until the terminator sequence 'end!' is found.
        The terminator itself is consumed and discarded.
        """
        while not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self.line_start_idx = self.current + 1
                self._advance()
                continue

            # Look for 'end!' in the raw stream
            if self._peek() == "e" and self.source[self.current : self.current + 4] == "end!":
                # consume 'end!'
                self.current += 4
                return

            self._advance()

        self.diags.fatal("Unterminated chronicle comment (expected 'end!').", filename=self.filename, line=self.line, col=self._col())

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

