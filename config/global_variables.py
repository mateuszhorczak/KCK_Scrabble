ACTUAL_LETTER = ' '

"""default number of players is 2, but can increase to 4 in app"""
NUMBER_OF_PLAYERS = 2
PLAYERS = []
PLAYERS_NICKNAMES = ['', '', '', '']
ROUND_NUMBER = 1
SKIPPED_TURNS = 0
ACTUAL_WORD_WITH_COORDS = []
PLAYED_WORDS = []
BOARD = None
BAG = None
DICTIONARY = None

LETTER_VALUES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1, "J": 8, "K": 5, "L": 1,
    "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1, "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8,
    "Y": 4, "Z": 10
}

TRIPLE_WORD_SCORE = [
    (0, 0), (7, 0), (14, 0), (0, 7), (14, 7), (0, 14), (7, 14), (14, 14), (7, 7)
]
DOUBLE_WORD_SCORE = [
    (1, 1), (2, 2), (3, 3), (4, 4), (1, 13), (2, 12), (3, 11), (4, 10), (13, 1), (12, 2), (11, 3), (10, 4), (13, 13),
    (12, 12), (11, 11), (10, 10)
]
TRIPLE_LETTER_SCORE = [
    (1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)
]
DOUBLE_LETTER_SCORE = [
    (0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2),
    (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)
]
