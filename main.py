from random import shuffle
from typing import Any

from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import var, reactive
from textual.screen import Screen
from textual.validation import Validator, ValidationResult
from textual.widget import Widget
from textual.widgets import Footer, Header, Button, Digits, Static, RichLog, Input, Label, Pretty

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


class Letter:
    def __init__(self, y, x, value):
        self.y = y
        self.x = x
        self.value = value

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def get_value(self):
        return self.value


class Tile:
    def __init__(self, letter):
        self.letter = letter.upper()
        if self.letter in LETTER_VALUES:
            self.score = LETTER_VALUES[self.letter]
        else:
            self.score = 0

    def get_letter(self):
        return self.letter

    def get_score(self):
        return self.score


class Bag:
    def __init__(self):
        self.bag = []
        self.initialize_bag()

    def add_to_bag(self, tile, quantity):
        for i in range(quantity):
            self.bag.append(tile)

    def initialize_bag(self):
        global LETTER_VALUES
        self.add_to_bag(Tile("A"), 9)
        self.add_to_bag(Tile("B"), 2)
        self.add_to_bag(Tile("C"), 2)
        self.add_to_bag(Tile("D"), 4)
        self.add_to_bag(Tile("E"), 12)
        self.add_to_bag(Tile("F"), 2)
        self.add_to_bag(Tile("G"), 3)
        self.add_to_bag(Tile("H"), 2)
        self.add_to_bag(Tile("I"), 9)
        self.add_to_bag(Tile("J"), 1)
        self.add_to_bag(Tile("K"), 1)
        self.add_to_bag(Tile("L"), 4)
        self.add_to_bag(Tile("M"), 3)
        self.add_to_bag(Tile("N"), 6)
        self.add_to_bag(Tile("O"), 8)
        self.add_to_bag(Tile("P"), 2)
        self.add_to_bag(Tile("Q"), 1)
        self.add_to_bag(Tile("R"), 6)
        self.add_to_bag(Tile("S"), 4)
        self.add_to_bag(Tile("T"), 6)
        self.add_to_bag(Tile("U"), 4)
        self.add_to_bag(Tile("V"), 2)
        self.add_to_bag(Tile("W"), 2)
        self.add_to_bag(Tile("X"), 1)
        self.add_to_bag(Tile("Y"), 2)
        self.add_to_bag(Tile("Z"), 2)
        shuffle(self.bag)

    def take_from_bag(self):
        # Removes a tile from the bag and returns it to the user. This is used for replenishing the rack.
        return self.bag.pop()

    def get_remaining_tiles(self):
        # Returns the number of tiles left in the bag.
        return len(self.bag)


class Rack:
    """
    Creates each player's 'dock', or 'hand'. Allows players to add, remove and replenish the number of tiles in their hand.
    """

    def __init__(self, bag):
        # Initializes the player's rack/hand. Takes the bag from which the racks tiles will come as an argument.
        self.rack = []
        self.bag = bag
        self.initialize()

    def add_to_rack(self):
        # Takes a tile from the bag and adds it to the player's rack.
        self.rack.append(self.bag.take_from_bag())

    def initialize(self):
        # Adds the initial 7 tiles to the player's hand.
        for i in range(7):
            self.add_to_rack()

    def get_rack_str(self):
        # Displays the user's rack in string form.
        return ", ".join(str(item.get_letter()) for item in self.rack)

    def get_rack_arr(self):
        # Returns the rack as an array of tile instances
        return self.rack

    def get_letters_from_rack_arr(self):
        # Return the letters in array
        arr = []
        for item in self.rack:
            arr.append(item.get_letter())
        return arr

    def append_letter(self, tile):
        self.rack.append(tile)

    def remove_from_rack(self, tile):
        # Removes a tile from the rack (for example, when a tile is being played).
        self.rack.remove(tile)

    def get_rack_length(self):
        # Returns the number of tiles left in the rack.
        return len(self.rack)

    def replenish_rack(self):
        # Adds tiles to the rack after a turn such that the rack will have 7 tiles (assuming a proper number of tiles in the bag).
        while self.get_rack_length() < 7 and self.bag.get_remaining_tiles() > 0:
            self.add_to_rack()


class Player:
    """
    Creates an instance of a player. Initializes the player's rack, and allows you to set/get a player name.
    """

    def __init__(self, bag):
        # Intializes a player instance. Creates the player's rack by creating an instance of that class.
        # Takes the bag as an argument, in order to create the rack.
        self.name = ""
        self.rack = Rack(bag)
        self.score = 0

    def set_name(self, name):
        # Sets the player's name.
        self.name = name

    def get_name(self):
        # Gets the player's name.
        return self.name

    def get_rack_str(self):
        # Returns the player's rack.
        return self.rack.get_rack_str()

    def get_rack_arr(self):
        # Returns the player's rack in the form of an array.
        return self.rack.get_rack_arr()

    def get_letters_from_rack_arr(self):
        # Returns the player's letters in array
        return self.rack.get_letters_from_rack_arr()

    def append_letter(self, tile):
        return self.rack.append_letter(tile)

    def increase_score(self, increase):
        # Increases the player's score by a certain amount. Takes the increase (int) as an argument and adds it to the score.
        self.score += increase

    def get_score(self):
        # Returns the player's score
        return self.score


class Board:
    """
    Creates the scrabble board.
    """

    def __init__(self):
        # Creates a 2-dimensional array that will serve as the board.
        self.board = [[None for i in range(15)] for j in range(15)]

    def get_board_array(self):
        # Returns the 2-dimensional board array.
        return self.board


class Word:
    def __init__(self, player, word, used_other_word):
        self.word = word.upper()
        self.player = player
        self.used_other_word = used_other_word

    def check_words(self):
        global DICTIONARY
        if DICTIONARY is None:
            DICTIONARY = open("dic.txt").read().splitlines()

        """If word not in dictionary"""
        if self.word not in DICTIONARY:
            return False

        """If player use other word to create his word"""
        if not self.used_other_word and ROUND_NUMBER != 1:
            return False

        if ROUND_NUMBER == 1:
            contains_start_field = False
            for letter in ACTUAL_WORD_WITH_COORDS:
                if letter.get_x() == 7 and letter.get_y() == 7:
                    contains_start_field = True

            """If word contains start field (8, 8)"""
            if not contains_start_field:
                return False

        return True

    def calculate_word_score(self):
        global LETTER_VALUES, TRIPLE_WORD_SCORE, DOUBLE_WORD_SCORE, TRIPLE_LETTER_SCORE, DOUBLE_LETTER_SCORE
        word_score = 0

        """"""

        """If letter place in letter premium spot"""
        for letter in ACTUAL_WORD_WITH_COORDS:
            if (letter.get_y(), letter.get_x()) in TRIPLE_LETTER_SCORE:
                word_score += LETTER_VALUES[letter.get_value()] * 3

            elif (letter.get_y(), letter.get_x()) in DOUBLE_LETTER_SCORE:
                word_score += LETTER_VALUES[letter.get_value()] * 2

            else:
                word_score += LETTER_VALUES[letter.get_value()]

        """If letter place in word premium spot"""
        for letter in ACTUAL_WORD_WITH_COORDS:
            if (letter.get_y(), letter.get_x()) in TRIPLE_WORD_SCORE:
                word_score *= 3

            if (letter.get_y(), letter.get_x()) in DOUBLE_WORD_SCORE:
                word_score *= 2

        self.player.increase_score(word_score)
        return word_score


def get_player_index():
    player_index = ROUND_NUMBER - 1
    while True:
        if player_index < len(PLAYERS):
            break
        else:
            player_index -= len(PLAYERS)
    return player_index


def start_game():
    """Function that start the game"""
    global PLAYERS, NUMBER_OF_PLAYERS, PLAYERS_NICKNAMES, BOARD, BAG
    BOARD = Board()
    BAG = Bag()
    for i in range(NUMBER_OF_PLAYERS):
        PLAYERS.append(Player(BAG))
        PLAYERS[i].set_name(PLAYERS_NICKNAMES[i])


def turn(player):   # TODO check returns
    global ROUND_NUMBER, SKIPPED_TURNS, ACTUAL_WORD_WITH_COORDS, BOARD, BAG
    """if is true direction of word is horizontal, else direction is vertical"""
    direction_horizontal = True
    used_other_word = False
    word_to_play = ''

    if not ACTUAL_WORD_WITH_COORDS:
        return 0

    if (SKIPPED_TURNS < 6) or (player.rack.get_rack_length() == 0 and BAG.get_remaining_tiles() == 0):

        """if user place only one letter and attach to board letters"""
        if len(ACTUAL_WORD_WITH_COORDS) == 1:
            y = ACTUAL_WORD_WITH_COORDS[0].get_y()
            x = ACTUAL_WORD_WITH_COORDS[0].get_x()
            if_get_letter = False
            
            if y != 14 and not if_get_letter:
                if BOARD.get_board_array()[y + 1][x] is not None:
                    """If connect to the letter on the top"""
                    ACTUAL_WORD_WITH_COORDS.append(BOARD.get_board_array()[y + 1][x])
                    if_get_letter = True
            if y != 0 and not if_get_letter:
                if BOARD.get_board_array()[y - 1][x] is not None:
                    """If connect to the letter on the bottom"""
                    ACTUAL_WORD_WITH_COORDS.append(BOARD.get_board_array()[y - 1][x])
                    if_get_letter = True
            if x != 14 and not if_get_letter:
                if BOARD.get_board_array()[y][x + 1] is not None:
                    """If connect to the letter on the right"""
                    ACTUAL_WORD_WITH_COORDS.append(BOARD.get_board_array()[y][x + 1])
                    """If connect to the letter on the left"""
                    if_get_letter = True
            if x != 0 and not if_get_letter:
                if BOARD.get_board_array()[y][x - 1] is not None:
                    ACTUAL_WORD_WITH_COORDS.append(BOARD.get_board_array()[y][x - 1])
                    if_get_letter = True
            if not if_get_letter:
                """The letter doesn't connect with anything"""
                return 0
    

        if ACTUAL_WORD_WITH_COORDS[0].get_x() == ACTUAL_WORD_WITH_COORDS[1].get_x():
            direction_horizontal = False
        elif ACTUAL_WORD_WITH_COORDS[0].get_y() == ACTUAL_WORD_WITH_COORDS[1].get_y():
            direction_horizontal = True
        else:
            """not valid word"""
            return 0

        if direction_horizontal:
            """word in horizontal direction"""

            """Sort letters by x-coordinate"""
            ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_x())
            row_number = ACTUAL_WORD_WITH_COORDS[0].get_y()

            temp_actual_word_with_coords = ACTUAL_WORD_WITH_COORDS.copy()
            """Check if letters that user placed stand next to each other"""
            for l, letter_in_word in enumerate(temp_actual_word_with_coords):

                """if it is a last user letter"""
                if l == len(temp_actual_word_with_coords) - 1:
                    word_to_play += letter_in_word.get_value()

                elif letter_in_word.get_x() + 1 != ACTUAL_WORD_WITH_COORDS[l + 1].get_x():
                    """
                    If they are not next to each other, check if the user used a letter that is already on the board
                    """

                    index_before_break = letter_in_word.get_x()
                    index_after_break = temp_actual_word_with_coords[l + 1].get_x()

                    """Iterates over a break"""
                    break_letters = ''
                    for j in range(index_before_break + 1, index_after_break):

                        """Check if something place in break is between letters"""
                        if BOARD.get_board_array()[row_number][j] is not None:
                            break_letters += BOARD.get_board_array()[row_number][j].get_value()
                            ACTUAL_WORD_WITH_COORDS.append(
                                Letter(row_number, j, BOARD.get_board_array()[row_number][j].get_value())
                            )
                        else:
                            """Lack of continuity. INVALID WORD"""
                            return 0

                    """Combine user letters with letters on the board"""
                    new_word = word_to_play + break_letters + letter_in_word.get_value()
                    word_to_play = new_word
                    used_other_word = True


                    """letter is not last and dont have break, common case"""
                else:
                    word_to_play += letter_in_word.get_value()

            """Check if user used letters from board at start or end of his word"""
            first_coordinate = temp_actual_word_with_coords[0].get_x()
            last_coordinate = temp_actual_word_with_coords[-1].get_x()

            """if additional letter at start of his word"""
            i = 1
            if first_coordinate > 0:
                while True:
                    if BOARD.get_board_array()[row_number][first_coordinate - i] is not None:
                        word_to_play = BOARD.get_board_array()[row_number][first_coordinate - i].get_value() + word_to_play
                        ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                row_number,
                                first_coordinate - i,
                                BOARD.get_board_array()[row_number][first_coordinate - i].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break

            """If additional letter at end of his word"""
            i = 1
            if last_coordinate < 14:
                while True:
                    if BOARD.get_board_array()[row_number][last_coordinate + i] is not None:
                        word_to_play = word_to_play + BOARD.get_board_array()[row_number][last_coordinate + i].get_value()

                        ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                row_number,
                                last_coordinate + i,
                                BOARD.get_board_array()[row_number][last_coordinate + i].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break
                ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_x())

        else:
            """word in vertical direction"""

            """Sort letters by y-coordinate"""
            ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_y())
            col_number = ACTUAL_WORD_WITH_COORDS[0].get_x()

            temp_actual_word_with_coords = ACTUAL_WORD_WITH_COORDS.copy()
            """Check if letters that user placed stand next to each other"""
            for l, letter_in_word in enumerate(temp_actual_word_with_coords):

                """if it is a last user letter"""
                if l == len(temp_actual_word_with_coords) - 1:
                    word_to_play += letter_in_word.get_value()

                elif letter_in_word.get_y() + 1 != temp_actual_word_with_coords[l + 1].get_y():
                    """
                    If they are not next to each other, check if the user used a letter that is already on the board
                    """

                    index_before_break = letter_in_word.get_y()
                    index_after_break = temp_actual_word_with_coords[l + 1].get_y()

                    """Iterates over a break"""
                    break_letters = ''
                    for j in range(index_before_break + 1, index_after_break):

                        """Check if something place in break is between letters"""
                        if BOARD.get_board_array()[j][col_number] is not None:
                            break_letters += BOARD.get_board_array()[j][col_number].get_value()
                            ACTUAL_WORD_WITH_COORDS.append(
                                Letter(j, col_number, BOARD.get_board_array()[j][col_number].get_value())
                            )
                        else:
                            """Lack of continuity. INVALID WORD"""  # TODO check
                            return 0

                    """Combine user letters with letters on the board"""
                    new_word = word_to_play + break_letters + letter_in_word.get_value()
                    word_to_play = new_word
                    used_other_word = True


                    """letter is not last and dont have break, common case"""
                else:
                    word_to_play += letter_in_word.get_value()

            """Check if user used letters from board at start or end of his word"""
            first_coordinate = temp_actual_word_with_coords[0].get_y()
            last_coordinate = temp_actual_word_with_coords[-1].get_y()

            """if additional letter at start of his word"""
            i = 1
            if first_coordinate > 0:
                while True:
                    if BOARD.get_board_array()[first_coordinate - i][col_number] is not None:
                        word_to_play = BOARD.get_board_array()[first_coordinate - i][col_number].get_value() + word_to_play
                        ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                first_coordinate - i,
                                col_number,
                                BOARD.get_board_array()[first_coordinate - i][col_number].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break

            """If additional letter at end of his word"""
            i = 1
            if last_coordinate < 14:
                while True:
                    if BOARD.get_board_array()[last_coordinate + i][col_number] is not None:
                        word_to_play = word_to_play + BOARD.get_board_array()[last_coordinate + i][col_number].get_value()
                        ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                last_coordinate + i,
                                col_number,
                                BOARD.get_board_array()[last_coordinate + i][col_number].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break
            ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_y())

        """Initialize word"""
        word = Word(player, word_to_play, used_other_word)

        """If word is correct then points are added"""
        if word.check_words():
            word_score = word.calculate_word_score()
            return word_score
        return 0


class IsANumberOfPlayers(Validator):
    """Check if the char is a number of players"""

    def validate(self, value: str) -> ValidationResult:
        if value in {"2", "3", "4"}:
            return self.success()
        else:
            return self.failure()


class GameCell(Button):
    """Single field"""

    class Pressed(Button.Pressed):
        def __init__(self):
            super().__init__()

    @staticmethod
    def at(row: int, col: int) -> str:
        return f"p{row}-{col}"

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.letter = ' '
        self.approved_round = 0
        self.player = ' '
        if (row, col) in TRIPLE_LETTER_SCORE:
            super().__init__(label=f"{self.letter} : 3L", id=self.at(row, col), variant='primary')
        elif (row, col) in DOUBLE_LETTER_SCORE:
            super().__init__(label=f"{self.letter} : 2L", id=self.at(row, col), variant='success')
        elif (row, col) in TRIPLE_WORD_SCORE:
            super().__init__(label=f"{self.letter} : 3W", id=self.at(row, col), variant='warning')
        elif (row, col) in DOUBLE_WORD_SCORE:
            super().__init__(label=f"{self.letter} : 2W", id=self.at(row, col), variant='error')
        else:
            super().__init__(label=self.letter, id=self.at(row, col), variant='default')


class GameGrid(Widget):
    """Display board"""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical(id="nav-left"):
            for i in range(15):
                yield Static(str(i + 1))
        with Horizontal(id="nav-top"):
            for i in range(15):
                yield Static(str(i + 1))
        for row in range(15):
            for col in range(15):
                yield GameCell(row, col)


class IsALetter(Validator):
    """Check if the char is a letter"""

    def validate(self, value: str) -> ValidationResult:
        player_index = get_player_index()
        if ((value.upper() in LETTER_VALUES.keys()
             and value.upper() in PLAYERS[player_index].get_letters_from_rack_arr())
                or value == ''):

            return self.success()
        else:
            return self.failure()


class IsANickname(Validator):
    """Check if the string can be a nickname"""

    def validate(self, value: str) -> ValidationResult:
        if len(value) > 2 and value != '   ':
            return self.success()
        else:
            return self.failure()


class LetterInput(Input):
    """Input used to enter letter in game"""

    def __init__(self):
        super().__init__(placeholder="Wpisz litere", validators=IsALetter(), validate_on=["submitted"])

    class LetterSubmitted(Input.Submitted):
        def __init__(self):
            super().__init__()


class InformationLabel(Widget):
    """Widget contains a Label and Input for display an information and enter a letter"""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label("runda: ")
                yield RoundNumberPretty(ROUND_NUMBER)
                yield Label("Gracz: ")
                yield PlayerNameLabelPretty(PLAYERS[0].name)
                yield Label("literki: ")
                yield UserLettersPretty(PLAYERS[0].get_rack_str())
            with Horizontal():
                yield LetterInput()
                yield Button(label="Zatwierdź ruch", variant="success", id="confirm_button")
                yield Button(label="Pomiń turę", variant="warning", id="pass_button")
                yield Button(label="Podnieś swoje litery", variant="primary", id="pick_up_letters")
                yield Button(label="Zakończ grę", variant="error", id="end_game")

    @on(Button.Pressed, "#confirm_button")
    def confirm_pressed(self, event: Button.Pressed):
        global ROUND_NUMBER, ACTUAL_WORD_WITH_COORDS, PLAYED_WORDS, PLAYERS
        word_score = turn(PLAYERS[get_player_index()])
        if word_score > 0:
            PLAYED_WORDS.append([ACTUAL_WORD_WITH_COORDS, PLAYERS[get_player_index()], word_score])
        else:
            self.clear_bad_letters()

        """Check if this is the last round"""
        self.if_end_game()

        """Reset word array"""
        ACTUAL_WORD_WITH_COORDS = []

        PLAYERS[get_player_index()].rack.replenish_rack()
        ROUND_NUMBER += 1
        self.query_one(RoundNumberPretty).update(ROUND_NUMBER)
        player_index = get_player_index()
        self.query_one(PlayerNameLabelPretty).update(PLAYERS[player_index].name)
        self.query_one(UserLettersPretty).update(PLAYERS[player_index].get_rack_str())

    @on(Button.Pressed, "#pass_button")
    def pass_pressed(self, event: Button.Pressed):
        global ROUND_NUMBER, SKIPPED_TURNS, ACTUAL_WORD_WITH_COORDS
        self.clear_bad_letters()
        ROUND_NUMBER += 1
        SKIPPED_TURNS += 1

        """Check if this is the last round"""
        self.if_end_game()

        """Reset word array"""
        ACTUAL_WORD_WITH_COORDS = []
        
        self.query_one(RoundNumberPretty).update(ROUND_NUMBER)
        player_index = get_player_index()
        self.query_one(PlayerNameLabelPretty).update(PLAYERS[player_index].name)
        self.query_one(UserLettersPretty).update(PLAYERS[player_index].get_rack_str())

    @on(Button.Pressed, "#pick_up_letters")
    def pick_up_pressed(self, event: Button.Pressed):
        self.clear_bad_letters()

    @on(Button.Pressed, "#end_game")
    def end_pressed(self, event: Button.Pressed):
        self.app.switch_screen("end_screen")

    def if_end_game(self):  # TODO check if works
        if not (SKIPPED_TURNS < 6) or (PLAYERS[get_player_index()].rack.get_rack_length() == 0 and BAG.get_remaining_tiles() == 0):
            self.app.switch_screen("end_screen")

    def clear_bad_letters(self):
        for row in range(15):
            for col in range(15):
                if self.app.query_one(f"#{GameCell.at(row, col)}").approved_round == ROUND_NUMBER:
                    PLAYERS[get_player_index()].rack.append_letter(Tile(BOARD.get_board_array()[row][col].get_value()))
                    BOARD.get_board_array()[row][col] = None
                    self.app.query_one(f"#{GameCell.at(row, col)}").letter = ' '
                    self.app.query_one(f"#{GameCell.at(row, col)}").approved_round = 0
                    self.app.query_one(f"#{GameCell.at(row, col)}").player = ' '

                    """change button label"""
                    if (row, col) in TRIPLE_LETTER_SCORE:
                        self.app.query_one(f"#{GameCell.at(row, col)}").label = " : 3L"
                    elif (row, col) in DOUBLE_LETTER_SCORE:
                        self.app.query_one(f"#{GameCell.at(row, col)}").label = " : 2L"
                    elif (row, col) in TRIPLE_WORD_SCORE:
                        self.app.query_one(f"#{GameCell.at(row, col)}").label = " : 3W"
                    elif (row, col) in DOUBLE_WORD_SCORE:
                        self.app.query_one(f"#{GameCell.at(row, col)}").label = " : 2W"
                    else:
                        self.app.query_one(f"#{GameCell.at(row, col)}").label = " "


class UserLettersPretty(Pretty):
    """Field displaying user letters"""

    def __init__(self, object: Any):
        super().__init__(object)


class PlayerNameLabelPretty(Pretty):
    """Field displaying number of round"""

    def __init__(self, object: Any):
        super().__init__(object)


class RoundNumberPretty(Pretty):
    """Field displaying number of round"""

    def __init__(self, object: Any):
        super().__init__(object)


class PlayerNamePretty(Pretty):
    """Field displaying the entered username"""

    def __init__(self, object: Any):
        super().__init__(object)


class ScorePretty(Pretty):
    """Field displaying the score"""
    def __init__(self, object: Any, label):
        super().__init__(object, id=label)


class NicknameInsertPlace(Widget):
    """Container used to get single nickname from user"""

    def __init__(self, player_number):
        super().__init__()
        global PLAYERS_NICKNAMES
        self.player_number = player_number
        self.player_name = 'user' + str(self.player_number)
        PLAYERS_NICKNAMES[self.player_number - 1] = self.player_name

    def compose(self) -> ComposeResult:
        with Horizontal(classes="userEnterNamePlace"):
            yield Label("Wpisz nazwe użytkownika: " + str(self.player_number))
            yield Input(placeholder="Nazwa gracza", id="player" + str(self.player_number), validators=IsANickname())
        yield PlayerNamePretty(self.player_name)

    def on_input_submitted(self, event: Input.Submitted):
        """Get number from input"""

        global NUMBER_OF_PLAYERS, PLAYERS_NICKNAMES
        if event.validation_result is not None:
            if not event.validation_result.is_valid:
                pass
            else:
                if event.input.value == '':
                    self.player_name = 'user' + str(self.player_number)
                else:
                    self.player_name = event.input.value
                try:
                    self.query_one(PlayerNamePretty).update(self.player_name)
                    PLAYERS_NICKNAMES[self.player_number - 1] = self.player_name
                except:
                    pass


class EndScreen(Screen):
    """End screen"""
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical(id="score_view"):
            global PLAYED_WORDS
            for i, player in enumerate(PLAYERS):
                yield Static(str(player.name))
                yield ScorePretty("Wynik: " + str(player.get_score()), "score" + str(i))

        with Vertical(id="word_view"):
            for word in PLAYED_WORDS:
                word_with_coords = word[0]
                word_str = ''
                for letter in word_with_coords:
                    word_str += letter.get_value()
                player = word[1]
                word_score = word[2]
                yield Static(str(player.name) + " słowo: " + word_str + " wartość: " + str(word_score))

        # yield Button(label="Odśwież wyniki", variant="primary", id="refresh_score")

    # @on(Button.Pressed, "#refresh_score")
    # def pass_pressed(self, event: Button.Pressed):
    #     for i, player in enumerate(PLAYERS):
    #         self.query_one("#score" + str(i)).update("Wynik: " + str(player.get_score()))


class ScoreBoard(Screen):
    """Score screen"""

    BINDINGS = [
        ("f3", "switch_screen('game')", "Back to game"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical(id="score_view"):
            for i, player in enumerate(PLAYERS):
                yield Static(str(player.name))
                yield ScorePretty("Wynik: " + str(player.get_score()), "score" + str(i))
        yield Button(label="Odśwież wyniki", variant="primary", id="refresh_score")

    @on(Button.Pressed, "#refresh_score")
    def pass_pressed(self, event: Button.Pressed):
        for i, player in enumerate(PLAYERS):
            self.query_one("#score" + str(i)).update("Wynik: " + str(player.get_score()))


class HelpScreen(Screen):
    """Help screen"""

    BINDINGS = [
        ("escape", "app.pop_screen()", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical(classes="information_container"):
            yield Static("PLANSZA POMOCY", classes="information_tag")
        with Vertical(classes="letters_values"):
            yield Static("WARTOŚĆ LITER", classes="letter_and_values_tag")
            for key, value in LETTER_VALUES.items():
                yield Pretty(key + " ma wartość: " + str(value), classes="letter_and_values_tag")


class GameScreen(Screen):
    """Main game screen"""

    BINDINGS = [
        ("f3", "switch_screen('score_board')", "Score screen"),
    ]

    def on_button_pressed(self, event: GameCell.Pressed):
        """Insert letter"""
        global ACTUAL_LETTER

        for row in range(15):
            for col in range(15):
                if event.button.id == GameCell.at(row, col):

                    if ((event.button.approved_round == 0 or event.button.approved_round == ROUND_NUMBER)
                        and (event.button.player == ' '
                             or event.button.player == PLAYERS[get_player_index()].get_name())):

                        if event.button.letter == ' ' and ACTUAL_LETTER != ' ':
                            """Add letter to empty field"""
                            user_letters = PLAYERS[get_player_index()].rack.get_rack_arr()
                            for tile in user_letters:
                                if tile.get_letter() == ACTUAL_LETTER:
                                    PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                                    break

                            event.button.approved_round = ROUND_NUMBER
                            event.button.player = PLAYERS[get_player_index()].get_name()
                            event.button.letter = ACTUAL_LETTER

                        elif event.button.letter != ' ' and ACTUAL_LETTER == ' ':
                            """Remove letter to get empty field and get letter back"""
                            PLAYERS[get_player_index()].rack.append_letter(Tile(event.button.letter))
                            event.button.approved_round = 0
                            event.button.player = ' '
                            event.button.letter = ACTUAL_LETTER

                        elif event.button.letter != ' ' and ACTUAL_LETTER != ' ':
                            """Replace letter other letter"""
                            user_letters = PLAYERS[get_player_index()].rack.get_rack_arr()
                            for tile in user_letters:
                                if tile.get_letter() == ACTUAL_LETTER:
                                    PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                                    break
                            PLAYERS[get_player_index()].rack.append_letter(Tile(event.button.letter))
                            event.button.letter = ACTUAL_LETTER

                        else:
                            """Do nothing (space char to empty field)"""
                            event.button.letter = ACTUAL_LETTER

                        """change button label"""
                        if (row, col) in TRIPLE_LETTER_SCORE:
                            event.button.label = f"{event.button.letter} : 3L"
                        elif (row, col) in DOUBLE_LETTER_SCORE:
                            event.button.label = f"{event.button.letter} : 2L"
                        elif (row, col) in TRIPLE_WORD_SCORE:
                            event.button.label = f"{event.button.letter} : 3W"
                        elif (row, col) in DOUBLE_WORD_SCORE:
                            event.button.label = f"{event.button.letter} : 2W"
                        else:
                            event.button.label = event.button.letter

                        """insert letters to array board and actual word array"""
                        if event.button.letter != ' ' and BOARD.get_board_array()[row][col] is None:
                            BOARD.get_board_array()[row][col] = Letter(row, col, event.button.letter)
                            ACTUAL_WORD_WITH_COORDS.append(Letter(row, col, event.button.letter))
                        elif (event.button.letter != ' '
                              or (event.button.letter == ' ' and BOARD.get_board_array()[row][col] is not None)):
                            BOARD.get_board_array()[row][col] = None
                            ACTUAL_WORD_WITH_COORDS.pop()
                        else:
                            pass

                        """reset letter after single insert to board"""
                        ACTUAL_LETTER = ' '

    def on_input_submitted(self, event: LetterInput.Submitted):
        """Get letter from input"""

        global ACTUAL_LETTER
        if event.validation_result is not None:
            if not event.validation_result.is_valid:
                pass
            else:
                if event.input.value == '':
                    ACTUAL_LETTER = ' '
                else:
                    ACTUAL_LETTER = event.input.value[0].upper()

    def compose(self):
        yield Header(show_clock=True)
        yield Footer()
        with ScrollableContainer(id='app-container'):
            yield GameGrid()
            yield InformationLabel()
        start_game()


class MainScreen(Screen):
    """Initial screen"""

    BINDINGS = [
        ("f3", "switch_screen('game')", "Enter game"),
        ("f1", "add_nickname_place", "add user"),
        ("f2", "remove_nickname_place", "remove user"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical(classes="information_container"):
            yield Label("Witaj w grze Scrabble !", classes="information_tag")
            yield Label("Wpisz nazwy graczy w polach. Możesz dodać więcej graczy (od 2 do 4)",
                        classes="information_tag")
        yield ScrollableContainer(NicknameInsertPlace(1), NicknameInsertPlace(2), id="nicknamesPlaces")

    def action_add_nickname_place(self) -> None:
        """An action to add a nickname add for other player."""

        global NUMBER_OF_PLAYERS
        if NUMBER_OF_PLAYERS < 4:
            NUMBER_OF_PLAYERS += 1
            new_nickname_place = NicknameInsertPlace(NUMBER_OF_PLAYERS)
            self.query_one("#nicknamesPlaces").mount(new_nickname_place)
            new_nickname_place.scroll_visible()

    def action_remove_nickname_place(self) -> None:
        """Called to remove a nickname place."""

        global NUMBER_OF_PLAYERS, PLAYERS_NICKNAMES
        if NUMBER_OF_PLAYERS > 2:
            nickname_places = self.query("NicknameInsertPlace")
            NUMBER_OF_PLAYERS = NUMBER_OF_PLAYERS - 1
            if nickname_places:
                nickname_places.last().remove()
            PLAYERS_NICKNAMES[NUMBER_OF_PLAYERS] = ''


class ScrabbleApp(App):
    """Main app"""

    CSS_PATH = "scrabble.tcss"

    TITLE = "SCRABBLE"

    """SCREEN VIEWS"""
    SCREENS = {
        "help": HelpScreen(),
        "game": GameScreen(),
        "main_screen": MainScreen(),
        "score_board": ScoreBoard(),
        "end_screen": EndScreen(),
    }

    """Shortcuts"""
    BINDINGS = [
        ("ctrl+d", "toggle_dark_mode", "Toggle dark mode"),
        ("ctrl+c", "quit", "Quit"),
        ("f10", "push_screen('help')", "Help"),
    ]

    def on_mount(self):
        self.push_screen(MainScreen())

    def action_toggle_dark_mode(self):
        """Turn on / off dark mode"""
        self.dark = not self.dark


if __name__ == "__main__":
    app = ScrabbleApp()
    app.run()
