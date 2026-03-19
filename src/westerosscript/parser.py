from __future__ import annotations

from westerosscript import ast
from westerosscript.errors import DiagnosticSink
from westerosscript.explain import Explainer
from westerosscript.tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token], *, explainer: Explainer, diags: DiagnosticSink, filename: str = "<source>") -> None:
        self.tokens = tokens
        self.explainer = explainer
        self.diags = diags
        self.filename = filename
        self.current = 0

    def parse_program(self) -> ast.Program:
        self.explainer.section("THE SMALL COUNCIL REVIEWS THE DECREE")
        statements: list[ast.Stmt] = []
        while not self._is_at_end():
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
            else:
                self._synchronize()
        return ast.Program(statements)

    def _statement(self) -> ast.Stmt | None:
        if self._match(TokenType.SIGIL):
            # Constant modifier for a declaration. For milestone 1 this behaves like a normal declaration.
            if not self._match(
                TokenType.COIN,
                TokenType.STAG,
                TokenType.ESSENCE,
                TokenType.SCROLL,
                TokenType.OATH,
                TokenType.LEDGER,
            ):
                t = self._peek()
                self.diags.fatal(
                    f"Expected a datatype after 'sigil' keyword, but found {t.lexeme!r}. "
                    f"Valid types are: coin, stag, essence, scroll, oath, ledger.",
                    filename=self.filename,
                    line=t.line,
                    col=t.col
                )
                return None
            type_tok = self._previous()
            decl = self._var_decl(type_tok)
            return decl

        if self._match(
            TokenType.COIN,
            TokenType.STAG,
            TokenType.ESSENCE,
            TokenType.SCROLL,
            TokenType.OATH,
            TokenType.LEDGER,
        ):
            type_tok = self._previous()
            self.explainer.say("COUNCIL", "Expected royal structure:")
            self.explainer.say("COUNCIL", "[DATATYPE] [IDENTIFIER] [ASSIGNMENT] [VALUE] [DELIMITER]")
            decl = self._var_decl(type_tok)
            self.explainer.say("COUNCIL", "✓ The council approves the structure.")
            return decl

        if self._match(TokenType.RAVEN):
            self.explainer.say("COUNCIL", "A raven shall carry a message forth.")
            value = self._expression()
            self._consume_bang_with_recovery()
            self.explainer.say("COUNCIL", "✓ The raven has been dispatched.")
            return ast.Raven(value=value)

        if self._match(TokenType.COUNCIL):
            self.explainer.say("COUNCIL", "The Small Council convenes to deliberate branching paths.")
            stmt = self._council_stmt()
            self.explainer.say("COUNCIL", "✓ The council's decree is sealed.")
            return stmt

        if self._match(TokenType.WHILE_WINTER):
            self.explainer.say("COUNCIL", "Winter approaches: a loop shall persist while conditions hold.")
            stmt = self._while_stmt()
            self.explainer.say("COUNCIL", "✓ The winter cycle is fortified.")
            return stmt

        if self._match(TokenType.FOR_EACH_HOUSE):
            self.explainer.say("COUNCIL", "The great houses march in order across the realm.")
            stmt = self._for_each_house_stmt()
            self.explainer.say("COUNCIL", "✓ The march of houses is decreed.")
            return stmt

        if self._match(TokenType.BREAK_CHAIN):
            self.explainer.say("COUNCIL", "The chain of command is broken; the loop shatters.")
            self._consume_bang_with_recovery()
            return ast.BreakChain()

        if self._match(TokenType.CONTINUE_MARCH):
            self.explainer.say("COUNCIL", "The march continues to the next chapter.")
            self._consume_bang_with_recovery()
            return ast.ContinueMarch()

        # Assignment: <identifier> claims <expr>!
        if self._check(TokenType.IDENTIFIER) and self._peek_next().type == TokenType.CLAIMS:
            self.explainer.say("COUNCIL", "A vassal declares their claim upon a treasury.")
            name = self._advance().lexeme
            self._consume(TokenType.CLAIMS, "Expected 'claims' assignment operator.")
            value = self._expression()
            self._consume_bang_with_recovery()
            self.explainer.say("COUNCIL", f"✓ {name!r} shall hold this wealth.")
            return ast.Assign(name=name, value=value)

        if self._peek().type == TokenType.EOF:
            return None

        t = self._peek()
        self.diags.fatal(f"Unexpected token {t.lexeme!r}.", filename=self.filename, line=t.line, col=t.col)
        return None

    def _var_decl(self, type_tok: Token) -> ast.VarDecl:
        type_name = _type_from_token(type_tok.type)
        name = self._consume(TokenType.IDENTIFIER, "Expected an identifier after datatype.").lexeme
        self._consume(TokenType.CLAIMS, "Expected 'claims' assignment operator.")
        init = self._expression()
        self._consume_bang_with_recovery()
        return ast.VarDecl(type_name=type_name, name=name, initializer=init)

    def _consume_bang_with_recovery(self) -> None:
        if self._match(TokenType.BANG):
            return
        # If the closing rune is missing, report a fatal syntax error instead of inserting one.
        t = self._peek()
        self.diags.fatal(
            f"Expected the sacred ending rune '!' to terminate the statement, but found {t.lexeme!r} instead.",
            filename=self.filename,
            line=t.line,
            col=t.col
        )
        raise ParsePanic()

    def _expression(self) -> ast.Expr:
        return self._comparison()

    def _comparison(self) -> ast.Expr:
        expr = self._term()
        while self._match(TokenType.EQUALS, TokenType.GREATER_THAN, TokenType.LESS_THAN):
            op = self._previous().lexeme
            right = self._term()
            expr = ast.Compare(expr, op, right)
        return expr

    def _term(self) -> ast.Expr:
        expr = self._factor()
        while self._match(TokenType.UNITE, TokenType.CLASH):
            op = self._previous().lexeme
            right = self._factor()
            expr = ast.Binary(expr, op, right)
        return expr

    def _factor(self) -> ast.Expr:
        expr = self._primary()
        while self._match(TokenType.FORGE, TokenType.DIVIDE_REALM):
            op = self._previous().lexeme
            right = self._primary()
            expr = ast.Binary(expr, op, right)
        return expr

    def _primary(self) -> ast.Expr:
        if self._match(TokenType.NUMBER):
            return ast.Literal(self._previous().literal)
        if self._match(TokenType.STRING):
            return ast.Literal(self._previous().literal)
        if self._match(TokenType.IDENTIFIER):
            return ast.Identifier(self._previous().lexeme)
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' to close grouped expression.")
            return expr

        t = self._peek()
        self.diags.fatal(
            f"Expected an expression (number, string, identifier, or parenthesized expression) "
            f"but found {t.lexeme!r}. Ensure your statement has valid syntax.",
            filename=self.filename,
            line=t.line,
            col=t.col
        )
        raise ParsePanic()

    def _council_stmt(self) -> ast.Council:
        # council <cond> then <block> (another_path <cond> then <block>)* (otherwise <block>)? end!
        branches: list[tuple[ast.Expr, ast.Block]] = []

        cond = self._expression()
        self._consume(TokenType.THEN, "Expected 'then' after council condition.")
        then_block = self._block_until({TokenType.ANOTHER_PATH, TokenType.OTHERWISE, TokenType.END})
        branches.append((cond, then_block))

        while self._match(TokenType.ANOTHER_PATH):
            c = self._expression()
            self._consume(TokenType.THEN, "Expected 'then' after another_path condition.")
            b = self._block_until({TokenType.ANOTHER_PATH, TokenType.OTHERWISE, TokenType.END})
            branches.append((c, b))

        otherwise_block: ast.Block | None = None
        if self._match(TokenType.OTHERWISE):
            otherwise_block = self._block_until({TokenType.END})

        self._consume(TokenType.END, "Expected 'end' to close council block.")
        self._consume_bang_with_recovery()
        return ast.Council(branches=branches, otherwise_block=otherwise_block)

    def _while_stmt(self) -> ast.WhileWinter:
        # while_winter <cond> then <block> end!
        cond = self._expression()
        self._consume(TokenType.THEN, "Expected 'then' after while_winter condition.")
        body = self._block_until({TokenType.END})
        self._consume(TokenType.END, "Expected 'end' to close while_winter block.")
        self._consume_bang_with_recovery()
        return ast.WhileWinter(condition=cond, body=body)

    def _for_each_house_stmt(self) -> ast.ForEachHouse:
        # for_each_house (coin|stag)? <name> claims <start> then <end> then <block> end!
        type_name = ast.TypeName.COIN
        if self._match(TokenType.COIN, TokenType.STAG):
            type_name = _type_from_token(self._previous().type)

        name = self._consume(TokenType.IDENTIFIER, "Expected an identifier after for_each_house.").lexeme
        self._consume(TokenType.CLAIMS, "Expected 'claims' after loop variable name.")
        start = self._expression()
        self._consume(TokenType.THEN, "Expected 'then' after loop start expression.")
        end = self._expression()
        self._consume(TokenType.THEN, "Expected 'then' after for_each_house range.")
        body = self._block_until({TokenType.END})
        self._consume(TokenType.END, "Expected 'end' to close for_each_house block.")
        self._consume_bang_with_recovery()
        return ast.ForEachHouse(type_name=type_name, name=name, start=start, end=end, body=body)

    def _block_until(self, end_tokens: set[TokenType]) -> ast.Block:
        statements: list[ast.Stmt] = []
        while not self._is_at_end() and self._peek().type not in end_tokens:
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
            else:
                self._synchronize()
        return ast.Block(statements=statements)

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        t = self._peek()
        self.diags.fatal(
            f"{message} Found {t.lexeme!r} instead.",
            filename=self.filename,
            line=t.line,
            col=t.col
        )
        raise ParsePanic()

    def _match(self, *types: TokenType) -> bool:
        for tt in types:
            if self._check(tt):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _peek_next(self) -> Token:
        if self.current + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + 1]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _synchronize(self) -> None:
        # Minimal recovery: advance to next bang or EOF.
        while not self._is_at_end() and not self._check(TokenType.BANG):
            self._advance()
        if self._match(TokenType.BANG):
            return


class ParsePanic(RuntimeError):
    pass


def _type_from_token(tt: TokenType) -> ast.TypeName:
    return {
        TokenType.COIN: ast.TypeName.COIN,
        TokenType.STAG: ast.TypeName.STAG,
        TokenType.ESSENCE: ast.TypeName.ESSENCE,
        TokenType.SCROLL: ast.TypeName.SCROLL,
        TokenType.OATH: ast.TypeName.OATH,
        TokenType.LEDGER: ast.TypeName.LEDGER,
    }.get(tt, ast.TypeName.UNKNOWN)

