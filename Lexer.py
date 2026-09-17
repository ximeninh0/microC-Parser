from __future__ import annotations

from dataclasses import dataclass
import enum
from typing import Iterator

import helper
from state_table import state_table

class TokenKind(enum.Enum):
    """Classe já implementada: nomes e números não devem ser alterados."""

    EOF = -1

    IDENTIFIER = 1
    INT_LITERAL = 2
    STRING_LITERAL = 3

    KW_INT = 10
    KW_BOOL = 11
    KW_VOID = 12
    KW_TRUE = 13
    KW_FALSE = 14
    KW_IF = 15
    KW_ELSE = 16
    KW_WHILE = 17
    KW_RETURN = 18
    KW_PRINT = 19

    PLUS = 20
    MINUS = 21
    STAR = 22
    SLASH = 23
    PERCENT = 24
    LESS = 25
    LESS_EQUAL = 26
    GREATER = 27
    GREATER_EQUAL = 28
    EQUAL_EQUAL = 29
    NOT_EQUAL = 30
    LOGICAL_AND = 31
    LOGICAL_OR = 32
    LOGICAL_NOT = 33
    ASSIGN = 34

    LEFT_PAREN = 40
    RIGHT_PAREN = 41
    LEFT_BRACE = 42
    RIGHT_BRACE = 43
    COMMA = 44
    SEMICOLON = 45


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: int | str | bool | None
    line: int
    column: int

    def __str__(self) -> str:
        return (
            f"<{self.kind.value}, {self.kind.name}, {self.lexeme!r}, "
            f"{self.value!r}, {self.line}, {self.column}>"
        )

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"erro léxico em {self.line}:{self.column}: {self.message}"

class Lexer:
    """Converte texto-fonte MicroC em uma sequência de tokens."""
    state = None
    input_position = 0
    last_final = None
    last_final_position = 0
    source = None
    line = 1
    column = 1

    returnToken = {
        helper.State.IN_IDENTIFIER : TokenKind.IDENTIFIER,

        helper.State.IN_INT : TokenKind.INT_LITERAL,
        helper.State.IN_STRING_END : TokenKind.STRING_LITERAL,

        helper.State.IN_ASSIGN : TokenKind.ASSIGN,
        helper.State.IN_EQUAL_EQUAL : TokenKind.EQUAL_EQUAL,
        helper.State.IN_EXCLAMATION : TokenKind.LOGICAL_NOT,
        helper.State.IN_NOT_EQUAL : TokenKind.NOT_EQUAL,
        helper.State.IN_LESS : TokenKind.LESS,
        helper.State.IN_LESS_EQUAL : TokenKind.LESS_EQUAL,
        helper.State.IN_GREATER : TokenKind.GREATER,
        helper.State.IN_GREATER_EQUAL : TokenKind.GREATER_EQUAL,
        helper.State.IN_LOGICAL_AND : TokenKind.LOGICAL_AND,
        helper.State.IN_LOGICAL_OR : TokenKind.LOGICAL_OR,     
        helper.State.IN_PLUS : TokenKind.PLUS,
        helper.State.IN_MINUS : TokenKind.MINUS,
        helper.State.IN_STAR : TokenKind.STAR,
        helper.State.IN_SLASH : TokenKind.SLASH,
        helper.State.IN_PERCENT : TokenKind.PERCENT,
        helper.State.IN_OPN_PAREN : TokenKind.LEFT_PAREN,
        helper.State.IN_CLS_PAREN : TokenKind.RIGHT_PAREN,
        helper.State.IN_OPN_BRACE : TokenKind.LEFT_BRACE,
        helper.State.IN_CLS_BRACE : TokenKind.RIGHT_BRACE,
        helper.State.IN_COMMA : TokenKind.COMMA,
        helper.State.IN_SCOLON : TokenKind.SEMICOLON,

        helper.State.ELSE_1 : TokenKind.IDENTIFIER,
        helper.State.ELSE_2 : TokenKind.IDENTIFIER,
        helper.State.ELSE_3 : TokenKind.IDENTIFIER,
        helper.State.ELSE_4 : TokenKind.KW_ELSE,

        helper.State.RETURN_1 : TokenKind.IDENTIFIER,
        helper.State.RETURN_2 : TokenKind.IDENTIFIER,
        helper.State.RETURN_3 : TokenKind.IDENTIFIER,
        helper.State.RETURN_4 : TokenKind.IDENTIFIER,
        helper.State.RETURN_5 : TokenKind.IDENTIFIER,
        helper.State.RETURN_6 : TokenKind.KW_RETURN,


        helper.State.WHILE_1 : TokenKind.IDENTIFIER,
        helper.State.WHILE_2 : TokenKind.IDENTIFIER,
        helper.State.WHILE_3 : TokenKind.IDENTIFIER,
        helper.State.WHILE_4 : TokenKind.IDENTIFIER,
        helper.State.WHILE_5 : TokenKind.KW_WHILE,

        helper.State.PRINT_1 : TokenKind.IDENTIFIER,
        helper.State.PRINT_2 : TokenKind.IDENTIFIER,
        helper.State.PRINT_3 : TokenKind.IDENTIFIER,
        helper.State.PRINT_4 : TokenKind.IDENTIFIER,
        helper.State.PRINT_5 : TokenKind.KW_PRINT,

        helper.State.FALSE_1 : TokenKind.IDENTIFIER,
        helper.State.FALSE_2 : TokenKind.IDENTIFIER,
        helper.State.FALSE_3 : TokenKind.IDENTIFIER,
        helper.State.FALSE_4 : TokenKind.IDENTIFIER,
        helper.State.FALSE_5 : TokenKind.KW_FALSE,

        helper.State.TRUE_1 : TokenKind.IDENTIFIER,
        helper.State.TRUE_2 : TokenKind.IDENTIFIER,
        helper.State.TRUE_3 : TokenKind.IDENTIFIER,
        helper.State.TRUE_4 : TokenKind.KW_TRUE,

        helper.State.VOID_1 : TokenKind.IDENTIFIER,
        helper.State.VOID_2 : TokenKind.IDENTIFIER,
        helper.State.VOID_3 : TokenKind.IDENTIFIER,
        helper.State.VOID_4 : TokenKind.KW_VOID,

        helper.State.BOOL_1 : TokenKind.IDENTIFIER,
        helper.State.BOOL_2 : TokenKind.IDENTIFIER,
        helper.State.BOOL_3 : TokenKind.IDENTIFIER,
        helper.State.BOOL_4 : TokenKind.KW_BOOL,

        helper.State.IN_I : TokenKind.IDENTIFIER,
        helper.State.IF_2 : TokenKind.KW_IF,

        helper.State.INT_1 : TokenKind.IDENTIFIER,
        helper.State.INT_2 : TokenKind.IDENTIFIER,
        helper.State.INT_3 : TokenKind.KW_INT,

        helper.State.WS : None,

        helper.State.COMMENT_4_TYPE_STAR : None,
        helper.State.COMMENT_3_TYPE_SLASH : None,
        helper.State.COMMENT_2_TYPE_SLASH : None
    }

    def rollback(self):
        self.state = helper.State.START
        self.input_position = self.last_final_position
        
    def __init__(self, source: str):
        self.source = source
        self.state = helper.State.START
        self.last_final_position = self.input_position

    def advance(self, c) -> None:
        if self.input_position < len(self.source):
            if c == helper.CharClass.NEW_LINE:
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.input_position += 1

    def classify(self, char: str) -> helper.CharClass | None:
        if not char.isascii():
            return None

        if (helper.CHAR_CLASS_MAP.get(char) is not None):
            return helper.CHAR_CLASS_MAP.get(char)

        if char.isalpha() or char == '_': return helper.CharClass.LETTER
        if char.isdigit(): return helper.CharClass.DIGIT

        raise LexerError(f"Caractere inválido: {char}", self.line, self.column)


    def tokens(self) -> Iterator[Token]:
        """Produza todos os tokens significativos e um único EOF ao final."""
        tokens = []
        while self.input_position < len(self.source):
            start_line = self.line
            start_column = self.column

            self.last_final = None
            self.last_final_position = self.input_position

            token_lexeme = ""
            token_value = None
            token_kind = None

            while self.state != helper.State.SE:
                
                if self.state in helper.final_states:
                    self.last_final = self.state
                    self.last_final_position = self.input_position

                if self.input_position >= len(self.source):
                    if self.state == helper.State.COMMENT_2_TYPE_STAR or self.state == helper.State.COMMENT_3_TYPE_STAR:
                        raise LexerError("Bloco de comentário não fechado", start_line, start_column)
                    if self.state == helper.State.IN_STRING or self.state == helper.State.IN_STRING_ESCAPE:
                        raise LexerError("String Aberta", start_line, start_column)
                    
                    self.state = helper.State.SE
                    break

                c = self.source[self.input_position]
                char_class = self.classify(c)

                if char_class not in state_table[self.state]:
                    self.state = helper.State.SE
                    break

                next_state = state_table[self.state][char_class]
                if next_state == helper.State.SE:
                    self.state = helper.State.SE
                    break

                if next_state == helper.State.LEXER_ERROR:
                    if self.state == helper.State.IN_STRING_ESCAPE:
                        raise LexerError("Escape Inválido!", self.line, self.column - 1)
                    else:
                        raise LexerError("Caractere Inválido!", self.line, self.column)

                self.state = next_state
                token_lexeme += c
                self.advance(c=char_class)

            self.rollback()

            if self.last_final is None:
                raise LexerError("Caractere inválido ou símbolo incompleto", start_line, start_column)

            token_kind = self.returnToken[self.last_final]
            if token_kind is not None:
                if token_kind == TokenKind.IDENTIFIER: token_value = token_lexeme
                elif token_kind == TokenKind.INT_LITERAL: token_value = int(token_lexeme)
                elif token_kind == TokenKind.STRING_LITERAL: 
                    raw_str = token_lexeme[1:-1]
                    token_value = (raw_str.replace(r'\n', '\n').replace(r'\t', '\t').replace(r'\"', '"').replace(r'\\', '\\'))
                elif token_kind == TokenKind.KW_TRUE: token_value = True
                elif token_kind == TokenKind.KW_FALSE: token_value = False
                else: token_value = None
                token = Token(token_kind,token_lexeme,token_value,start_line,start_column)
                tokens.append(token)

        #TODO: Check the need of this last verifications:
        if self.state == helper.State.COMMENT_2_TYPE_STAR or self.state == helper.State.COMMENT_3_TYPE_STAR:
            raise LexerError("Bloco de comentário não fechado", self.line,self.column)
        if self.state == helper.State.IN_STRING or self.state == helper.State.IN_STRING_ESCAPE:
            raise LexerError("String Aberta", self.line,self.column)
        tokens.append(Token(TokenKind.EOF,"",None,self.line,self.column))
        return tokens
        # yield  # mantém este método como gerador durante o desenvolvimento

    def scan(self) -> list[Token]:
        return list(self.tokens())
