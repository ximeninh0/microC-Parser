from __future__ import annotations

from collections.abc import Sequence

from Lexer import Token, TokenKind
from ast_nodes import (
    Assignment,
    BinaryExpr,
    BinaryOperator,
    Block,
    BoolLiteral,
    CallExpr,
    CallStmt,
    Expr,
    FunctionDecl,
    IdentifierExpr,
    IfStmt,
    IntLiteral,
    Node,
    Parameter,
    PrintItem,
    Program,
    ReturnStmt,
    SourceSpan,
    Stmt,
    StringLiteral,
    TypeName,
    UnaryExpr,
    UnaryOperator,
    VarDecl,
    WhileStmt,
)


TYPE_START = {TokenKind.KW_INT, TokenKind.KW_BOOL, TokenKind.KW_VOID}
EXPRESSION_START = {
    TokenKind.IDENTIFIER,
    TokenKind.INT_LITERAL,
    TokenKind.KW_FALSE,
    TokenKind.KW_TRUE,
    TokenKind.LEFT_PAREN,
    TokenKind.LOGICAL_NOT,
    TokenKind.MINUS,
}
STATEMENT_START = TYPE_START | {
    TokenKind.IDENTIFIER,
    TokenKind.KW_IF,
    TokenKind.KW_WHILE,
    TokenKind.KW_RETURN,
    TokenKind.KW_PRINT,
    TokenKind.LEFT_BRACE,
}


TYPE_BY_TOKEN = {
    TokenKind.KW_INT: TypeName.INT,
    TokenKind.KW_BOOL: TypeName.BOOL,
    TokenKind.KW_VOID: TypeName.VOID,
}


class ParserError(Exception):
    def __init__(self, token: Token, expected: set[TokenKind]):
        self.token = token
        self.expected = frozenset(expected)
        super().__init__()

    @property
    def line(self) -> int:
        return self.token.line

    @property
    def column(self) -> int:
        return self.token.column

    def __str__(self) -> str:
        names = ", ".join(kind.name for kind in sorted(
            self.expected,
            key=lambda kind: kind.value,
        ))
        return (
            f"erro sintático em {self.line}:{self.column}: esperado {{{names}}}, "
            f"encontrado {self.token.kind.name} ({self.token.lexeme!r})"
        )


class Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = list(tokens)
        if not self.tokens:
            raise ValueError("a sequência de tokens deve terminar em EOF")
        if self.tokens[-1].kind is not TokenKind.EOF:
            raise ValueError("o último token deve ser EOF")
        if any(token.kind is TokenKind.EOF for token in self.tokens[:-1]):
            raise ValueError("EOF deve aparecer uma única vez, no final")
        self.current = 0

    # Espiada, isso daqui náo avança e nem retorna erro, só o token do cursor
    def peek(self, offset: int = 0) -> Token:
        index = min(self.current + offset, len(self.tokens) - 1)
        return self.tokens[index]

    # Esse aqui retorna se é ou não o token, não consome
    def check(self, kind: TokenKind) -> bool:
        return self.peek().kind is kind

    # Consome o token, move o cursor
    def advance(self) -> Token:
        token = self.peek()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token

    # Vê se bate com o token, não gera erro se der ruim e consome 
    def match(self, *kinds: TokenKind) -> Token | None:
        if self.peek().kind in kinds:
            return self.advance()
        return None

    # Consome, se não for o token retorna erro
    def expect(self, kinds: TokenKind | set[TokenKind]) -> Token:
        expected = kinds if isinstance(kinds, set) else {kinds}
        token = self.peek()
        if token.kind not in expected:
            raise ParserError(token, set(expected))
        return self.advance()

    @staticmethod
    def _token_span(token: Token) -> SourceSpan:
        return SourceSpan(
            token.line,
            token.column,
            token.line,
            token.column + len(token.lexeme),
        )

    @staticmethod
    def _start(value: Token | Node) -> tuple[int, int]:
        if isinstance(value, Node):
            return value.span.start_line, value.span.start_column
        return value.line, value.column

    @staticmethod
    def _end(value: Token | Node) -> tuple[int, int]:
        if isinstance(value, Node):
            return value.span.end_line, value.span.end_column
        return value.line, value.column + len(value.lexeme)

    @classmethod
    def _span(cls, first: Token | Node, last: Token | Node) -> SourceSpan:
        start_line, start_column = cls._start(first)
        end_line, end_column = cls._end(last)
        return SourceSpan(start_line, start_column, end_line, end_column)

    def parse(self) -> Program:
        return self.parse_program()

    # program ::= function* EOF
    def parse_program(self) -> Program:
        start = self.peek()
        functions: list[FunctionDecl] = []
        while self.peek().kind in TYPE_START:
            functions.append(self.parse_function())
        eof = self.expect(TokenKind.EOF)
        return Program(functions, span=self._span(start, eof))

    # function ::= type IDENTIFIER ... block
    def parse_function(self) -> FunctionDecl:
        start = self.peek()
        return_type = self.parse_type()
        name = self.expect(TokenKind.IDENTIFIER)
        self.expect(TokenKind.LEFT_PAREN)
        parameters = (
            self.parse_parameter_list()
            if self.peek().kind in TYPE_START
            else []
        )
        self.expect(TokenKind.RIGHT_PAREN)
        body = self.parse_block()
        return FunctionDecl(
            return_type,
            name.lexeme,
            parameters,
            body,
            span=self._span(start, body),
        )

    # type ::= KW_INT | KW_BOOL | KW_VOID
    def parse_type(self) -> TypeName: # int bool void
        token = self.expect(TYPE_START)
        return TYPE_BY_TOKEN[token.kind]

    def parse_parameter_list(self) -> list[Parameter]:
        start = self.parse_parameter()
        
        parameters = []
        parameters.append(start)

        while self.match(TokenKind.COMMA):
            parameter = self.parse_parameter()
            parameters.append(parameter)

        return parameters

    def parse_parameter(self) -> Parameter:
        start = self.peek()
        param_type = self.parse_type()
        name = self.expect(TokenKind.IDENTIFIER)
        
        return Parameter(param_type, name.lexeme, span = self._span(start,name))

    def parse_block(self) -> Block:
        start = self.expect(TokenKind.LEFT_BRACE)
        statements: list[Stmt] = []

        while not self.check(TokenKind.RIGHT_BRACE) and not self.check(TokenKind.EOF):
            statements.append(self.parse_statement())

        end = self.expect(TokenKind.RIGHT_BRACE)
        return Block(statements, span=self._span(start, end))

    def parse_statement(self) -> Stmt:
        start = self.peek()

        if start.kind in TYPE_START:
            self.parse_declaration()
        elif start.kind is TokenKind.IDENTIFIER:
            self.parse_id_or_call_statement()
        elif start.kind is TokenKind.KW_IF:
            self.parse_if_statement()
        elif start.kind is TokenKind.KW_WHILE:
            self.parse_while_statement()
        elif start.kind is TokenKind.KW_RETURN:
            self.parse_return_statement()
        elif start.kind is TokenKind.KW_PRINT:
            self.parse_print_statement()
        elif start.kind is TokenKind.LEFT_BRACE:
            self.parse_block()
        else:
            raise ParserError(start, STATEMENT_START)

    def parse_id_or_call_statement(self) -> Stmt:
        start = self.expect(TokenKind.IDENTIFIER)

        if self.match(TokenKind.ASSIGN): # x = 10;
            expression = self.parse_expression()
            semicolon = self.expect(TokenKind.SEMICOLON)
            target = IdentifierExpr(start.lexeme, span=self._span(start, semicolon))
            return Assignment(target, expression, span=self._span(start, semicolon))

        elif self.match(TokenKind.LEFT_PAREN): # funcao(argumento);
            arguments = self.parse_arguments()
            rightParen = self.expect(TokenKind.RIGHT_PAREN)
            expression = CallExpr(start.lexeme, arguments, span=self._span(start, rightParen))
            semicolon = self.expect(TokenKind.SEMICOLON)
            return CallStmt(expression, span=self._span(start, semicolon))
        
        else:
            raise ParserError(self.peek(),[TokenKind.ASSIGN, TokenKind.LEFT_PAREN])
            
    def parse_declaration(self) -> Stmt:
        start = self.peek()
        varType = self.parse_type()
        name = self.expect(TokenKind.IDENTIFIER)
        expression = None
        if self.match(TokenKind.ASSIGN):
            expression = self.parse_expression()
        semicolon = self.expect(TokenKind.SEMICOLON)
        return VarDecl(varType, name.lexeme, expression, span=self._span(start, semicolon))

    def parse_if_statement(self) -> Stmt:
        start = self.expect(TokenKind.KW_IF)
        self.expect(TokenKind.LEFT_PAREN)
        condition = self.parse_expression()
        self.expect(TokenKind.RIGHT_PAREN)
        block = self.parse_block()
        elseBlock = None
        if self.match(TokenKind.KW_ELSE):
            elseBlock = self.parse_block()
        return IfStmt(condition, block, elseBlock, span=self._span(start, elseBlock or block))

    def parse_while_statement(self) -> Stmt:
        start = self.expect(TokenKind.KW_WHILE)
        self.expect(TokenKind.LEFT_PAREN)
        condition = self.parse_expression()
        self.expect(TokenKind.RIGHT_PAREN)
        block = self.parse_block()
        return WhileStmt(condition, block, span=self._span(start, block))

    def parse_return_statement(self) -> Stmt:
        start = self.expect(TokenKind.KW_RETURN)
        value = None
        if not self.check(TokenKind.SEMICOLON):
            value = self.parse_expression()
        semicolon = self.expect(TokenKind.SEMICOLON)
        return ReturnStmt(value, span=self._span(start, semicolon))

    def parse_print_statement(self) -> Stmt:
        raise NotImplementedError("implemente print_statement")

    def parse_print_item(self) -> PrintItem:
        raise NotImplementedError("implemente print_item")

    def parse_string_literals(self) -> StringLiteral:
        raise NotImplementedError("implemente string_literals")

    def parse_expression(self) -> Expr:
        return self.parse_logical_or() # checar gramática!

    def parse_logical_or(self) -> Expr:
        first = self.parse_logical_and()

        while self.match(TokenKind.LOGICAL_OR):
            second = self.parse_logical_and()
            first = BinaryExpr(BinaryOperator.LOGICAL_OR, first, second, span=self._span(first, second))
        return first

    def parse_logical_and(self) -> Expr:
        first = self.parse_equality()

        while self.match(TokenKind.LOGICAL_AND):
            second = self.parse_equality()
            first = BinaryExpr(BinaryOperator.LOGICAL_AND, first, second, span=self._span(first, second))
        return first

    def parse_equality(self) -> Expr:
        first = self.parse_relational()

        while token := self.match(TokenKind.EQUAL_EQUAL, TokenKind.NOT_EQUAL):
            operator = BinaryOperator.EQUAL if token.kind is TokenKind.EQUAL_EQUAL else BinaryOperator.NOT_EQUAL
            second = self.parse_relational()
            first = BinaryExpr(operator, first, second, span=self._span(first, second))
        return first

    def parse_relational(self) -> Expr:
        first = self.parse_additive()

        while token := self.match(TokenKind.LESS, TokenKind.LESS_EQUAL, TokenKind.GREATER, TokenKind.GREATER_EQUAL):
            match token.kind:
                case TokenKind.LESS:           operator = BinaryOperator.LESS
                case TokenKind.LESS_EQUAL:     operator = BinaryOperator.LESS_EQUAL
                case TokenKind.GREATER:        operator = BinaryOperator.GREATER
                case _:                        operator = BinaryOperator.GREATER_EQUAL
            second = self.parse_additive()
            first = BinaryExpr(operator, first, second, span=self._span(first, second))
        return first

    def parse_additive(self) -> Expr:
        first = self.parse_multiplicative()

        while token := self.match(TokenKind.PLUS, TokenKind.MINUS):
            operator = BinaryOperator.ADD if token.kind is TokenKind.PLUS else BinaryOperator.SUBTRACT
            second = self.parse_multiplicative()
            first = BinaryExpr(operator, first, second, span=self._span(first, second))
        return first

    def parse_multiplicative(self) -> Expr:
        first = self.parse_unary()

        while token := self.match(TokenKind.STAR, TokenKind.SLASH, TokenKind.PERCENT):
            match token.kind:
                case TokenKind.STAR:    operator = BinaryOperator.MULTIPLY
                case TokenKind.SLASH:   operator = BinaryOperator.DIVIDE
                case _:                 operator = BinaryOperator.REMAINDER
            second = self.parse_unary()
            first = BinaryExpr(operator, first, second, span=self._span(first, second))
        return first

    def parse_unary(self) -> Expr:
        if token := self.match(TokenKind.LOGICAL_NOT, TokenKind.MINUS):
            operator = UnaryOperator.NOT if token.kind is TokenKind.LOGICAL_NOT else UnaryOperator.NEGATE
            operand = self.parse_unary()
            return UnaryExpr(operator, operand, span=self._span(token, operand))
        return self.parse_primary()


    def parse_primary(self) -> Expr:
        # primary ::= LEFT_PAREN expression RIGHT_PAREN
        #   | IDENTIFIER (LEFT_PAREN arguments RIGHT_PAREN)?
        #   | INT_LITERAL
        #   | KW_TRUE
        #   | KW_FALSE
        if self.match(TokenKind.LEFT_PAREN):
            expr = self.parse_expression()
            self.expect(TokenKind.RIGHT_PAREN)
            return expr

        if id_token := self.match(TokenKind.IDENTIFIER):
            if self.match(TokenKind.LEFT_PAREN):
                args = self.parse_arguments()
                right = self.expect(TokenKind.RIGHT_PAREN)
                return CallExpr(id_token.lexeme, args, span=self._span(id_token, right))
            return IdentifierExpr(id_token.lexeme, span=self._token_span(id_token))

        if int_token := self.match(TokenKind.INT_LITERAL):
            return IntLiteral(int(int_token.lexeme), span=self._token_span(int_token))

        if true_token := self.match(TokenKind.KW_TRUE):
            return BoolLiteral(True, span=self._token_span(true_token))

        if false_token := self.match(TokenKind.KW_FALSE):
            return BoolLiteral(False, span=self._token_span(false_token))

        raise ParserError(self.peek(), {TokenKind.LEFT_PAREN, TokenKind.IDENTIFIER, TokenKind.INT_LITERAL, TokenKind.KW_TRUE, TokenKind.KW_FALSE})

    def parse_arguments(self) -> list[Expr]:
        arguments = []

        if not self.check(TokenKind.RIGHT_PAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenKind.COMMA):
                arguments.append(self.parse_expression())

        return arguments
