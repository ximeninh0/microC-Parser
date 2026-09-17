import enum

class State(enum.Enum):
    START = 0
    IN_IDENTIFIER = 1
    IN_INT = 2
    IN_STRING = 3
    IN_STRING_ESCAPE = 4
    IN_STRING_END = 5
    
    IN_ASSIGN = 6          # =
    IN_EQUAL_EQUAL = 7     # ==
    IN_EXCLAMATION = 8     # !
    IN_NOT_EQUAL = 9       # !=
    IN_LESS = 10           # <
    IN_LESS_EQUAL = 11     # <=
    IN_GREATER = 12        # >
    IN_GREATER_EQUAL = 13  # >=
    IN_AMPERSAND = 14      # &
    IN_LOGICAL_AND = 15    # &&
    IN_PIPE = 16           # |
    IN_LOGICAL_OR = 17     # ||
    
    IN_PLUS = 18
    IN_MINUS = 19
    IN_STAR = 20
    IN_SLASH = 72
    IN_PERCENT = 21
    IN_OPN_PAREN = 22
    IN_CLS_PAREN = 23
    IN_OPN_BRACE = 24
    IN_CLS_BRACE = 25
    IN_COMMA = 26
    IN_SCOLON = 27

    ELSE_1 = 28
    ELSE_2 = 29
    ELSE_3 = 30
    ELSE_4 = 31

    RETURN_1 = 32
    RETURN_2 = 33
    RETURN_3 = 34
    RETURN_4 = 35
    RETURN_5 = 36
   #RETURN_6 = '36'(está no final com outro número)

    WHILE_1 = 37
    WHILE_2 = 38
    WHILE_3 = 39
    WHILE_4 = 40
    WHILE_5 = 41

    PRINT_1 = 42
    PRINT_2 = 43
    PRINT_3 = 44
    PRINT_4 = 45
    PRINT_5 = 46

    FALSE_1 = 47
    FALSE_2 = 48
    FALSE_3 = 49
    FALSE_4 = 50
    FALSE_5 = 51

    TRUE_1 = 52
    TRUE_2 = 53
    TRUE_3 = 54
    TRUE_4 = 55

    VOID_1 = 56
    VOID_2 = 57
    VOID_3 = 58
    VOID_4 = 59

    BOOL_1 = 60
    BOOL_2 = 61
    BOOL_3 = 62
    BOOL_4 = 63

    IN_I = 64
    IF_2 = 65

    INT_1 = 66
    INT_2 = 67
    INT_3 = 68

    # ENTER_1 = 69
    # ENTER_2 = 70

    SE = 71

    WS = 73
    RETURN_6 = 74

    COMMENT_2_TYPE_STAR = 75
    COMMENT_3_TYPE_STAR = 76
    COMMENT_4_TYPE_STAR = 77

    COMMENT_2_TYPE_SLASH = 78
    COMMENT_3_TYPE_SLASH = 79

    ERROR = -1
    LEXER_ERROR = -2


class CharClass(enum.Enum):
    LETTER = 0
    DIGIT = 1

    EQUAL = 2
    LESS = 3
    GREATER = 4
    NOT = 5
    SPACE = 6

    PLUS = 7
    MINUS = 8
    STAR = 9
    SLASH = 10
    PERCENT = 19

    QUOTE = 11

    OPN_PAREN = 12
    OPN_BRACE = 13
    CLS_PAREN = 14
    CLS_BRACE = 15

    INV_SLASH = 16

    AMPERSAND = 17
    PIPE = 18

    LETTER_I = 20
    LETTER_F = 21
    LETTER_W = 22
    LETTER_H = 23
    LETTER_L = 24
    LETTER_E = 25
    LETTER_R = 26
    LETTER_T = 27
    LETTER_U = 28
    LETTER_N = 29
    LETTER_V = 30
    LETTER_O = 31
    LETTER_D = 32
    LETTER_A = 33
    LETTER_S = 34
    LETTER_B = 35
    LETTER_P = 36

    SCOLON = 39
    COMMA = 40

    NEW_LINE = 41

final_states = {
    State.IN_IDENTIFIER,

    State.IN_INT,
    State.IN_STRING,

    State.IN_STRING_END,
    State.IN_ASSIGN,
    State.IN_EQUAL_EQUAL,
    State.IN_EXCLAMATION,
    State.IN_NOT_EQUAL,
    State.IN_LESS,
    State.IN_LESS_EQUAL,
    State.IN_GREATER,
    State.IN_GREATER_EQUAL,
    State.IN_LOGICAL_AND,
    State.IN_LOGICAL_OR,     
    State.IN_PLUS,
    State.IN_MINUS,
    State.IN_STAR,
    State.IN_SLASH,
    State.IN_PERCENT,
    State.IN_OPN_PAREN,
    State.IN_CLS_PAREN,
    State.IN_OPN_BRACE,
    State.IN_CLS_BRACE,
    State.IN_COMMA,
    State.IN_SCOLON,

    State.ELSE_1,
    State.ELSE_2,
    State.ELSE_3,
    State.ELSE_4,

    State.RETURN_1,
    State.RETURN_2,
    State.RETURN_3,
    State.RETURN_4,
    State.RETURN_5,
    State.RETURN_6,

    State.WHILE_1,
    State.WHILE_2,
    State.WHILE_3,
    State.WHILE_4,
    State.WHILE_5,

    State.PRINT_1,
    State.PRINT_2,
    State.PRINT_3,
    State.PRINT_4,
    State.PRINT_5,

    State.FALSE_1,
    State.FALSE_2,
    State.FALSE_3,
    State.FALSE_4,
    State.FALSE_5,

    State.TRUE_1,
    State.TRUE_2,
    State.TRUE_3,
    State.TRUE_4,

    State.VOID_1,
    State.VOID_2,
    State.VOID_3,
    State.VOID_4,

    State.BOOL_1,
    State.BOOL_2,
    State.BOOL_3,
    State.BOOL_4,

    State.IN_I,
    State.IF_2,

    State.INT_1,
    State.INT_2,
    State.INT_3,

    State.WS,

    State.COMMENT_4_TYPE_STAR,
    State.COMMENT_3_TYPE_SLASH,
    State.COMMENT_2_TYPE_SLASH

}

CHAR_CLASS_MAP = {
    "=": CharClass.EQUAL,
    "<": CharClass.LESS,
    ">": CharClass.GREATER,
    "!": CharClass.NOT,
    "+": CharClass.PLUS,
    "-": CharClass.MINUS,
    "*": CharClass.STAR,
    "/": CharClass.SLASH,
    "%": CharClass.PERCENT,
    '"': CharClass.QUOTE,
    "(": CharClass.OPN_PAREN,
    "{": CharClass.OPN_BRACE,
    ")": CharClass.CLS_PAREN,
    "}": CharClass.CLS_BRACE,
    " ": CharClass.SPACE,
    "&": CharClass.AMPERSAND,
    "|": CharClass.PIPE,
    ",": CharClass.COMMA,
    ";": CharClass.SCOLON,
    "i": CharClass.LETTER_I,
    "e": CharClass.LETTER_E,
    "f": CharClass.LETTER_F,
    "w": CharClass.LETTER_W,
    "h": CharClass.LETTER_H,
    "l": CharClass.LETTER_L,
    "r": CharClass.LETTER_R,
    "t": CharClass.LETTER_T,
    "u": CharClass.LETTER_U,
    "n": CharClass.LETTER_N,
    "v": CharClass.LETTER_V,
    "o": CharClass.LETTER_O,
    "d": CharClass.LETTER_D,
    "a": CharClass.LETTER_A,
    "s": CharClass.LETTER_S,
    "b": CharClass.LETTER_B,
    "p": CharClass.LETTER_P,
    ".": CharClass.LETTER,
    '\t': CharClass.SPACE,
    "\n": CharClass.NEW_LINE,
    "\\": CharClass.INV_SLASH
}
