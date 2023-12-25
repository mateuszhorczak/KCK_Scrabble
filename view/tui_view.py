from controller.controller import get_player_index, turn, start_game
from model.model import Tile, Letter
from config import global_variables as gv
from config.global_variables import (TRIPLE_WORD_SCORE, DOUBLE_WORD_SCORE, TRIPLE_LETTER_SCORE, DOUBLE_LETTER_SCORE,
                                     LETTER_VALUES, GAME_INSTRUCTION)

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.validation import Validator, ValidationResult
from textual.widget import Widget
from textual.widgets import Footer, Header, Button, Static, Input, Label, Pretty

from typing import Any


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
             and value.upper() in gv.PLAYERS[player_index].get_letters_from_rack_arr())
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
                yield RoundNumberPretty(gv.ROUND_NUMBER)
                yield Label("Gracz: ")
                yield PlayerNameLabelPretty(gv.PLAYERS[0].name)
                yield Label("literki: ")
                yield UserLettersPretty(gv.PLAYERS[0].get_rack_str())
            with Horizontal():
                yield LetterInput()
                yield Button(label="Zatwierdź ruch", variant="success", id="confirm_button")
                yield Button(label="Pomiń turę", variant="warning", id="pass_button")
                yield Button(label="Podnieś swoje litery", variant="primary", id="pick_up_letters")
                yield Button(label="Zakończ grę", variant="error", id="end_game")

    @on(Button.Pressed, "#confirm_button")
    def confirm_pressed(self, event: Button.Pressed):
        word_score = turn(gv.PLAYERS[get_player_index()])

        if word_score > 0:
            gv.PLAYED_WORDS.append([gv.ACTUAL_WORD_WITH_COORDS, gv.PLAYERS[get_player_index()], word_score])
        else:
            self.clear_bad_letters()

        """Reset word array"""
        gv.ACTUAL_WORD_WITH_COORDS = []

        """Check if this is the last round"""
        self.if_end_game()

        gv.PLAYERS[get_player_index()].rack.replenish_rack()
        gv.ROUND_NUMBER += 1
        self.query_one(RoundNumberPretty).update(gv.ROUND_NUMBER)
        player_index = get_player_index()
        self.query_one(PlayerNameLabelPretty).update(gv.PLAYERS[player_index].name)
        self.query_one(UserLettersPretty).update(gv.PLAYERS[player_index].get_rack_str())

    @on(Button.Pressed, "#pass_button")
    def pass_pressed(self, event: Button.Pressed):
        self.clear_bad_letters()
        gv.ROUND_NUMBER += 1
        gv.SKIPPED_TURNS += 1

        """Check if this is the last round"""
        self.if_end_game()

        """Reset word array"""
        gv.ACTUAL_WORD_WITH_COORDS = []

        self.query_one(RoundNumberPretty).update(gv.ROUND_NUMBER)
        player_index = get_player_index()
        self.query_one(PlayerNameLabelPretty).update(gv.PLAYERS[player_index].name)
        self.query_one(UserLettersPretty).update(gv.PLAYERS[player_index].get_rack_str())

    @on(Button.Pressed, "#pick_up_letters")
    def pick_up_pressed(self, event: Button.Pressed):
        self.clear_bad_letters()

    @on(Button.Pressed, "#end_game")
    def end_pressed(self, event: Button.Pressed):
        self.app.switch_screen("end_screen")

    def if_end_game(self):
        if not (gv.SKIPPED_TURNS < 6) or (
                gv.PLAYERS[get_player_index()].rack.get_rack_length() == 0 and gv.BAG.get_remaining_tiles() == 0):
            self.app.switch_screen("end_screen")

    def clear_bad_letters(self):
        for row in range(15):
            for col in range(15):
                if self.app.query_one(f"#{GameCell.at(row, col)}").approved_round == gv.ROUND_NUMBER:
                    gv.PLAYERS[get_player_index()].rack.append_letter(
                        Tile(gv.BOARD.get_board_array()[row][col].get_value())
                    )
                    gv.BOARD.get_board_array()[row][col] = None
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
        self.player_number = player_number
        self.player_name = 'user' + str(self.player_number)
        gv.PLAYERS_NICKNAMES[self.player_number - 1] = self.player_name

    def compose(self) -> ComposeResult:
        with Horizontal(classes="userEnterNamePlace"):
            yield Label("Wpisz nazwe użytkownika: " + str(self.player_number))
            yield Input(placeholder="Nazwa gracza", id="player" + str(self.player_number), validators=IsANickname())
        yield PlayerNamePretty(self.player_name)

    def on_input_submitted(self, event: Input.Submitted):
        """Get number from input"""

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
                    gv.PLAYERS_NICKNAMES[self.player_number - 1] = self.player_name
                except:
                    pass


class EndScreen(Screen):
    """End screen"""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with ScrollableContainer(id="end_game_container"):
            with Vertical(id="score_view2"):
                for i, player in enumerate(gv.PLAYERS):
                    yield Static(str(player.name))
                    yield ScorePretty("Wynik: " + str(player.get_score()), "score" + str(i))

            with Vertical(id="word_view"):
                for word in gv.PLAYED_WORDS:
                    word_with_coords = word[0]
                    word_str = ''
                    for letter in word_with_coords:
                        word_str += letter.get_value()
                    player = word[1]
                    word_score = word[2]
                    yield Static(str(player.name) + " słowo: " + word_str + " wartość: " + str(word_score))


class ScoreBoard(Screen):
    """Score screen"""

    BINDINGS = [
        ("f3", "switch_screen('game')", "Back to game"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical(id="score_view"):
            for i, player in enumerate(gv.PLAYERS):
                yield Static(str(player.name))
                yield ScorePretty("Wynik: " + str(player.get_score()), "score" + str(i))
        yield Button(label="Odśwież wyniki", variant="primary", id="refresh_score")

    @on(Button.Pressed, "#refresh_score")
    def pass_pressed(self, event: Button.Pressed):
        for i, player in enumerate(gv.PLAYERS):
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
        with Horizontal(id="help_labels"):
            with Vertical(classes="letters_values"):
                yield Static("WARTOŚĆ LITER", classes="letter_and_values_tag")
                for i, (key, value) in enumerate(LETTER_VALUES.items()):
                    if i % 2 == 0:
                        if key == "Q":
                            next_key, next_value = list(LETTER_VALUES.items())[i + 1]
                            yield Static(f"{key} ma wartość: {value}        {next_key} ma wartość: {next_value}",
                                         classes="letter_and_values_tag")
                        else:
                            next_key, next_value = list(LETTER_VALUES.items())[i + 1]
                            yield Static(f"{key} ma wartość: {value}         {next_key} ma wartość: {next_value}",
                                         classes="letter_and_values_tag")
            with Vertical(id="description"):
                yield Pretty(GAME_INSTRUCTION, classes="letter_and_values_tag")


class GameScreen(Screen):
    """Main game screen"""

    BINDINGS = [
        ("f3", "switch_screen('score_board')", "Score screen"),
    ]

    def on_button_pressed(self, event: GameCell.Pressed):
        """Insert letter"""

        for row in range(15):
            for col in range(15):
                if event.button.id == GameCell.at(row, col):

                    if ((event.button.approved_round == 0 or event.button.approved_round == gv.ROUND_NUMBER)
                            and (event.button.player == ' '
                                 or event.button.player == gv.PLAYERS[get_player_index()].get_name())):

                        if event.button.letter == ' ' and gv.ACTUAL_LETTER != ' ':
                            """Add letter to empty field"""
                            user_letters = gv.PLAYERS[get_player_index()].rack.get_rack_arr()
                            for tile in user_letters:
                                if tile.get_letter() == gv.ACTUAL_LETTER:
                                    gv.PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                                    break

                            event.button.approved_round = gv.ROUND_NUMBER
                            event.button.player = gv.PLAYERS[get_player_index()].get_name()
                            event.button.letter = gv.ACTUAL_LETTER

                        elif event.button.letter != ' ' and gv.ACTUAL_LETTER == ' ':
                            """Remove letter to get empty field and get letter back"""
                            gv.PLAYERS[get_player_index()].rack.append_letter(Tile(event.button.letter))
                            event.button.approved_round = 0
                            event.button.player = ' '
                            event.button.letter = gv.ACTUAL_LETTER

                        elif event.button.letter != ' ' and gv.ACTUAL_LETTER != ' ':
                            """Replace letter other letter"""
                            user_letters = gv.PLAYERS[get_player_index()].rack.get_rack_arr()
                            for tile in user_letters:
                                if tile.get_letter() == gv.ACTUAL_LETTER:
                                    gv.PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                                    break
                            gv.PLAYERS[get_player_index()].rack.append_letter(Tile(event.button.letter))
                            event.button.letter = gv.ACTUAL_LETTER

                        else:
                            """Do nothing (space char to empty field)"""
                            event.button.letter = gv.ACTUAL_LETTER

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
                        if event.button.letter != ' ' and gv.BOARD.get_board_array()[row][col] is None:
                            gv.BOARD.get_board_array()[row][col] = Letter(row, col, event.button.letter)
                            gv.ACTUAL_WORD_WITH_COORDS.append(Letter(row, col, event.button.letter))
                        elif (event.button.letter != ' '
                              or (event.button.letter == ' ' and gv.BOARD.get_board_array()[row][col] is not None)):
                            gv.BOARD.get_board_array()[row][col] = None
                            gv.ACTUAL_WORD_WITH_COORDS.pop()
                        else:
                            pass

                        """reset letter after single insert to board"""
                        gv.ACTUAL_LETTER = ' '

    def on_input_submitted(self, event: LetterInput.Submitted):
        """Get letter from input"""

        if event.validation_result is not None:
            if not event.validation_result.is_valid:
                pass
            else:
                if event.input.value == '':
                    gv.ACTUAL_LETTER = ' '
                else:
                    gv.ACTUAL_LETTER = event.input.value[0].upper()

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

        if gv.NUMBER_OF_PLAYERS < 4:
            gv.NUMBER_OF_PLAYERS += 1
            new_nickname_place = NicknameInsertPlace(gv.NUMBER_OF_PLAYERS)
            self.query_one("#nicknamesPlaces").mount(new_nickname_place)
            new_nickname_place.scroll_visible()

    def action_remove_nickname_place(self) -> None:
        """Called to remove a nickname place."""

        if gv.NUMBER_OF_PLAYERS > 2:
            nickname_places = self.query("NicknameInsertPlace")
            gv.NUMBER_OF_PLAYERS = gv.NUMBER_OF_PLAYERS - 1
            if nickname_places:
                nickname_places.last().remove()
            gv.PLAYERS_NICKNAMES[gv.NUMBER_OF_PLAYERS] = ''


class ScrabbleApp(App):
    """Main app"""

    CSS_PATH = "../styles/scrabble.tcss"

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
