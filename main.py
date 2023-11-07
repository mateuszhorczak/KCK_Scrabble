from random import shuffle

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import var, reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Button, Digits, Static, RichLog

BOARD = [[None for i in range(15)] for j in range(15)]

LETTER_VALUES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1, "J": 1, "K": 5, "L": 1,
    "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1, "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8,
    "Y": 4, "Z": 10, "#": 0
}

TRIPLE_WORD_SCORE = [(1, 1), (8, 1), (15, 1), (1, 8), (15, 8), (1, 15), (8, 15), (15, 15), (8, 8)]
DOUBLE_WORD_SCORE = [(2, 2), (3, 3), (4, 4), (5, 5), (2, 14), (3, 13), (4, 12), (5, 11), (14, 2), (13, 3), (12, 4),
                     (11, 5), (14, 14), (13, 13), (12, 12), (11, 11)]
TRIPLE_LETTER_SCORE = [(2, 6), (2, 10), (6, 2), (6, 6), (6, 10), (6, 14), (10, 2), (10, 6), (10, 10), (10, 14), (14, 6),
                       (14, 10)]
DOUBLE_LETTER_SCORE = [(1, 4), (1, 12), (3, 7), (3, 9), (4, 1), (4, 8), (4, 15), (7, 3), (7, 7), (7, 9), (7, 13),
                       (8, 4), (8, 12), (9, 3), (9, 7), (9, 9), (9, 13), (12, 1), (12, 8), (12, 15), (13, 7), (13, 9),
                       (15, 4), (15, 12)]


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
        # Creates the bag full of game tiles, and calls the initialize_bag() method,
        # which adds the default 100 tiles to the bag.
        # Takes no arguments.
        self.bag = []
        self.initialize_bag()

    def add_to_bag(self, tile, quantity):
        # Adds a certain quantity of a certain tile to the bag. Takes a tile and an integer quantity as arguments.
        for i in range(quantity):
            self.bag.append(tile)

    def initialize_bag(self):
        # Adds the intiial 100 tiles to the bag.
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
        self.add_to_bag(Tile("J"), 9)
        self.add_to_bag(Tile("K"), 1)
        self.add_to_bag(Tile("L"), 4)
        self.add_to_bag(Tile("M"), 2)
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
        self.add_to_bag(Tile("Z"), 1)
        self.add_to_bag(Tile("#"), 2)
        shuffle(self.bag)

    def take_from_bag(self):
        # Removes a tile from the bag and returns it to the user. This is used for replenishing the rack.
        return self.bag.pop()

    def get_remaining_tiles(self):
        # Returns the number of tiles left in the bag.
        return len(self.bag)


class GameCell(Button):
    """Individual playable cell in the game."""

    class Pressed(Button.Pressed):
        def __init__(self):
            super().__init__()

    @staticmethod
    def at(row: int, col: int) -> str:
        return f"p{row}-{col}"

    @staticmethod
    def cell_label(row: int, col: int) -> str:
        return f"{row}-{col}"

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.letter = ' '
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
    """The main playable grid of game cells."""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the game grid.

        Returns:
            ComposeResult: The result of composing the game grid.
        """
        for row in range(1, 16):
            for col in range(1, 16):
                yield GameCell(row, col)


class ScrabbleApp(App):
    CSS_PATH = "scrabble.tcss"

    TITLE = "SCRABBLE"

    """Shortcuts"""
    BINDINGS = [
        ('ctrl+d', 'toggle_dark_mode', 'Toggle dark mode'),
    ]

    def on_button_pressed(self, event: GameCell.Pressed):
        for row in range(1, 16):
            for col in range(1, 16):
                if event.button.id == GameCell.at(row, col):
                    event.button.letter = 'P'
                    # event.button.label = GameCell

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

    def compose(self):
        yield Header(show_clock=True)
        yield Footer()
        with ScrollableContainer(id='app-container'):
            with Vertical(id="nav-left"):
                yield Static("1")
                yield Static("2")
                yield Static("3")
                yield Static("4")
                yield Static("5")
                yield Static("6")
                yield Static("7")
                yield Static("8")
                yield Static("9")
                yield Static("10")
                yield Static("11")
                yield Static("12")
                yield Static("13")
                yield Static("14")
                yield Static("15")
            with Horizontal(id="nav-top"):
                yield Static("1")
                yield Static("2")
                yield Static("3")
                yield Static("4")
                yield Static("5")
                yield Static("6")
                yield Static("7")
                yield Static("8")
                yield Static("9")
                yield Static("10")
                yield Static("11")
                yield Static("12")
                yield Static("13")
                yield Static("14")
                yield Static("15")
            # yield GameCell(8, 8)
            yield GameGrid()

    def action_toggle_dark_mode(self):
        """Turn on / off dark mode"""
        self.dark = not self.dark


if __name__ == "__main__":
    ScrabbleApp().run()
