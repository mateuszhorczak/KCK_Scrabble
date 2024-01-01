from tkinter import *
import tkinter as tk
from tkinter import ttk

from config.global_variables import GAME_INSTRUCTION, LETTER_VALUES, TRIPLE_LETTER_SCORE, DOUBLE_LETTER_SCORE, \
    DOUBLE_WORD_SCORE, TRIPLE_WORD_SCORE, ROUND_NUMBER
from config import global_variables as gv
from controller.controller import start_game, get_player_index, turn
from model.model import Letter, Tile


class ScrabbleApp(tk.Tk):
    """Main app"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Scrabble Game")
        self.geometry("1980x1080")

        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initializing frames to an empty array
        self.frames = {}

        # Iterating through a tuple consisting of the different page layouts
        for F in (MainView, HelpBoardView, ScrabbleBoardView, EndGameView):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        container.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainView)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def confirm_move(self):
        """Approve movement"""

        word_score = turn(gv.PLAYERS[get_player_index()])
        if word_score > 0:
            gv.PLAYED_WORDS.append([gv.ACTUAL_WORD_WITH_COORDS, gv.PLAYERS[get_player_index()], word_score])
        else:
            self.pickup_letters()

        """Reset word array"""
        gv.ACTUAL_WORD_WITH_COORDS = []

        """Check if this is the last round"""
        self.if_end_game()

        gv.PLAYERS[get_player_index()].rack.replenish_rack()
        gv.ROUND_NUMBER += 1
        self.frames[ScrabbleBoardView].update_round_label()

    def skip_turn(self):
        """skip player turn"""
        gv.ROUND_NUMBER += 1
        gv.SKIPPED_TURNS += 1
        self.if_end_game()
        self.frames[ScrabbleBoardView].update_round_label()

    def pickup_letters(self):
        """Pickup letters from board to player rack"""
        for row in range(15):
            for col in range(15):
                """get reference to board field"""
                entry = self.frames[ScrabbleBoardView].grid_slaves(row=row + 1, column=col + 1)[0]
                if entry.approved_round == gv.ROUND_NUMBER:
                    entry.delete(0, tk.END)
                    gv.PLAYERS[get_player_index()].rack.append_letter(
                        Tile(gv.BOARD.get_board_array()[row][col].get_value())
                    )
                    gv.BOARD.get_board_array()[row][col] = None
                    entry.approved_round = None
                    entry.value = None
                    self.frames[ScrabbleBoardView].update_round_label()

    def end_game(self):
        """Switch to end game view"""
        self.show_frame(EndGameView)
        self.frames[EndGameView].update_scoreboard()
        self.update_idletasks()  # Odśwież interfejs użytkownika)

    def if_end_game(self):
        """Check if game is over"""
        if not (gv.SKIPPED_TURNS < 6) or (
                gv.PLAYERS[get_player_index()].rack.get_rack_length() == 0 and gv.BAG.get_remaining_tiles() == 0):
            self.end_game()


class BaseView(tk.Frame):
    """Base view from which other views inherit"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class MainView(BaseView):
    """Initial view"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        gv.NUMBER_OF_PLAYERS = 2
        self.player_entries = []
        self.player_labels = []

        # General container for all view content
        self.outer_container = tk.Frame(self, bg="#e6e6e6", padx=80, pady=40, relief="solid", borderwidth=2)
        self.outer_container.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome label
        self.welcome_label = tk.Label(self.outer_container, text="Witaj w grze Scrabble!", font=("Helvetica", 20),
                                      bg="#e6e6e6", fg="black")
        self.welcome_label.grid(row=0, column=0, columnspan=3, pady=20)

        # Container for labels and input fields
        self.players_container = tk.Frame(self.outer_container, bg="#f0f0f0", padx=20, pady=20, relief="solid",
                                          borderwidth=2)
        self.players_container.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Fields for entering player names and labels
        for i in range(gv.NUMBER_OF_PLAYERS):
            label = tk.Label(self.players_container, text=f"Gracz {i + 1}:", font=("Helvetica", 16), bg="#f0f0f0")
            entry = tk.Entry(self.players_container, font=("Helvetica", 16))
            label.grid(row=i, column=0, padx=10, pady=10, sticky="nsew")
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="nsew")
            self.player_labels.append(label)
            self.player_entries.append(entry)
            entry.bind("<Return>", lambda event, index=i: self.update_player_name(event, index))

        # Buttons to increase and decrease the number of players
        self.decrease_button = tk.Button(self.outer_container, text="-", command=self.decrease_players,
                                         font=("Helvetica", 16), bg="#c0c0c0", bd=2)
        self.decrease_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.num_players_label = tk.Label(self.outer_container, text=str(gv.NUMBER_OF_PLAYERS), font=("Helvetica", 16),
                                          bg="#e6e6e6")
        self.num_players_label.grid(row=2, column=1, padx=20, pady=(0, 10), sticky="nsew")

        self.increase_button = tk.Button(self.outer_container, text="+", command=self.increase_players,
                                         font=("Helvetica", 16), bg="#c0c0c0", bd=2)
        self.increase_button.grid(row=2, column=2, padx=20, pady=(0, 10), sticky="nsew")

        # Button to go to the help screen or game screen
        self.help_button = tk.Button(self.outer_container, text="Pomoc",
                                     command=lambda: self.controller.show_frame(HelpBoardView),
                                     font=("Helvetica", 20), bg="chartreuse2", fg="black", bd=2,
                                     highlightbackground="#32a852")
        self.help_button.grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")
        self.next_button = tk.Button(self.outer_container, text="Rozpocznij grę",
                                     command=lambda: [self.controller.show_frame(ScrabbleBoardView), start_game(),
                                                      self.controller.frames[ScrabbleBoardView].update_round_label()],
                                     font=("Helvetica", 20), bg="#4caf50", fg="white", bd=2,
                                     highlightbackground="#32a852")
        self.next_button.grid(row=4, column=0, columnspan=3, pady=20, sticky="nsew")

    def decrease_players(self):
        if gv.NUMBER_OF_PLAYERS > 2:
            # Delete the last input field
            entry_to_remove = self.player_entries.pop()
            entry_to_remove.destroy()

            # Remove the last label
            label_to_remove = self.player_labels.pop()
            label_to_remove.destroy()

            gv.NUMBER_OF_PLAYERS -= 1
            gv.PLAYERS_NICKNAMES[gv.NUMBER_OF_PLAYERS] = ''
            self.num_players_label.config(text=str(gv.NUMBER_OF_PLAYERS))

    def increase_players(self):
        if gv.NUMBER_OF_PLAYERS < 4:
            # Add a new input field
            new_label = tk.Label(self.players_container, text=f"Gracz {gv.NUMBER_OF_PLAYERS + 1}:",
                                 font=("Helvetica", 16), bg="#f0f0f0")
            new_entry = tk.Entry(self.players_container, font=("Helvetica", 16))
            new_label.grid(row=gv.NUMBER_OF_PLAYERS, column=0, padx=10, pady=10, sticky="nsew")
            new_entry.grid(row=gv.NUMBER_OF_PLAYERS, column=1, padx=10, pady=10, sticky="nsew")
            self.player_labels.append(new_label)
            self.player_entries.append(new_entry)
            new_entry.bind("<Return>", lambda event, index=gv.NUMBER_OF_PLAYERS: self.update_player_name(event, index))

            gv.NUMBER_OF_PLAYERS += 1
            self.num_players_label.config(text=str(gv.NUMBER_OF_PLAYERS))

    def update_player_name(self, event, index):
        # Update player tag after pressing Enter
        player_name = self.player_entries[index].get()
        self.player_labels[index].config(text=f"Gracz {index + 1}: {player_name}")
        gv.PLAYERS_NICKNAMES[index] = player_name


class HelpBoardView(BaseView):
    """Help view with information about game"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # A general container for all view content
        self.outer_container = tk.Frame(self, bg="#e6e6e6", padx=80, pady=40, relief="solid", borderwidth=2)
        self.outer_container.place(relx=0.5, rely=0.5, anchor="center")

        # Centered header label
        self.header_label = tk.Label(self.outer_container, text="Pomoc Scrabble", font=("Helvetica", 20), bg="#e6e6e6",
                                     fg="black")
        self.header_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="nsew")

        # Container for left and right parts
        self.left_container = tk.Frame(self.outer_container, bg="#f0f0f0", padx=20, pady=20, relief="solid",
                                       borderwidth=2)
        self.right_container = tk.Frame(self.outer_container, bg="#f0f0f0", padx=20, pady=20, relief="solid",
                                        borderwidth=2)
        self.left_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.right_container.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Information on the left side of the board
        self.info_label_left = tk.Label(self.left_container, text="WARTOŚĆ LITER", font="helvetica 12 bold",
                                        bg="#f0f0f0")
        self.info_label_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # iterate over pairs of letters and their values to print them
        for i, (key, value) in enumerate(LETTER_VALUES.items()):
            row = i // 2 + 1
            col = i % 2

            label_text = f"{key} ma wartość: {value}"
            (tk.Label(self.left_container, text=label_text, font="Helvetica 12 bold", bg="#f0f0f0")
             .grid(row=row, column=col * 2, padx=10, pady=10, sticky="nsew"))

        # Information on the left side of the board
        self.info_label_right = tk.Label(self.right_container, text=GAME_INSTRUCTION, wraplength=1000, justify="left",
                                         font="Helvetica 16 bold", bg="#f0f0f0")
        self.info_label_right.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.back_button = tk.Button(self.outer_container, text="Powrót",
                                     command=lambda: self.controller.show_frame(MainView),
                                     font=("Helvetica", 20), bg="#4caf50", fg="white", bd=2,
                                     highlightbackground="#32a852")
        self.back_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")


class EndGameView(BaseView):
    """End game view"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # A general container for all view content
        self.outer_container = tk.Frame(self, bg="#e6e6e6", padx=80, pady=40, relief="solid", borderwidth=2)
        self.outer_container.place(relx=0.5, rely=0.5, anchor="center")

        # Centered header label
        self.header_label = tk.Label(self.outer_container, text="Koniec gry!", font=("Helvetica", 24), bg="#e6e6e6",
                                     fg="black")
        self.header_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="nsew")

        # A container for all your data
        self.container = tk.Frame(self.outer_container, bg="#f0f0f0", padx=20, pady=20, relief="solid", borderwidth=2)
        self.container.grid(row=1, column=0, sticky="nsew")

        # "Scoreboard" inscription
        self.info_label = tk.Label(self.container, text="Tabela wyników:", font="helvetica 16 bold", bg="#f0f0f0")
        self.info_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")

        # Additional field for displaying results
        self.scoreboard_label = tk.Label(self.container, text="", font="helvetica 14", bg="#f0f0f0")
        self.scoreboard_label.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        # Empty element to be centered vertically
        self.empty_label = tk.Label(self.container, text="", font=("Helvetica", 12), bg="#f0f0f0")
        self.empty_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

    def update_scoreboard(self):
        # Update player scores
        scoreboard_text = "\n".join([f"{player.name} : {player.get_score()}" for player in gv.PLAYERS])
        self.scoreboard_label.config(text=scoreboard_text)


class ScrabbleBoardView(tk.Frame):
    """Scrabble game view"""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.board_data = [[' ' for _ in range(15)] for _ in range(15)]

        # Configuration of the columns and rows of the board
        for i in range(16):
            # Reducing the column width for numbering on the left
            if i == 0:
                self.grid_columnconfigure(i, minsize=20, weight=0)
            else:
                self.grid_columnconfigure(i, minsize=120, weight=1, uniform="columns")

            # Reducing the row height for numbering on the top
            if i == 0:
                self.grid_rowconfigure(i, minsize=10, weight=0)
            else:
                self.grid_rowconfigure(i, minsize=60, weight=1, uniform="rows")

        # Field grid numbering
        for i in range(15):
            # Column numbering at the top
            (tk.Label(self, text=str(i + 1), fg="red", font="Helvetica 12 bold")
             .grid(row=0, column=i + 1, sticky="nsew"))

            # Row numbering on the left
            (tk.Label(self, text=str(i + 1), fg="red", font="Helvetica 12 bold")
             .grid(row=i + 1, column=0, sticky="nsew"))

            """Put field to game board"""
            for j in range(15):
                if (i, j) in TRIPLE_LETTER_SCORE:
                    entry = PlaceholderEntry(self, placeholder="3L", bg="deepskyblue", justify="center", row=i, col=j,
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in DOUBLE_LETTER_SCORE:
                    entry = PlaceholderEntry(self, placeholder="2L", bg="palegreen", justify="center", row=i, col=j,
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in TRIPLE_WORD_SCORE:
                    entry = PlaceholderEntry(self, placeholder="3W", bg="gold1", justify="center", row=i, col=j,
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in DOUBLE_WORD_SCORE:
                    entry = PlaceholderEntry(self, placeholder="2W", bg="hotpink", justify="center", row=i, col=j,
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")
                else:
                    entry = PlaceholderEntry(self, justify="center", font=("Helvetica", 12), width=2, row=i, col=j, )
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

        # Frame for game information
        self.information_frame = tk.Frame(self)
        self.information_frame.grid(row=16, column=5, columnspan=16, sticky="nsew")

        # Container for labels and buttons
        self.labels_buttons_container = tk.Frame(self.information_frame, bg="#f0f0f0", padx=20, pady=10, relief="solid",
                                                 borderwidth=2)
        self.labels_buttons_container.grid(row=0, column=0, sticky="nsew")

        # Labels with round number and letters
        self.round_label = tk.Label(self.labels_buttons_container, text=f"Runda: {ROUND_NUMBER}, tura: ",
                                    font=("Helvetica", 12), bg="#f0f0f0")
        self.round_label.grid(row=0, column=0, columnspan=1, sticky="nsew")

        self.letters_container = tk.Label(self.labels_buttons_container, text="Literki: ", font=("Helvetica", 12),
                                          bg="#f0f0f0")
        self.letters_container.grid(row=1, column=0, columnspan=1, sticky="nsew")

        # Interactive buttons
        self.confirm_button = tk.Button(self.labels_buttons_container, text="Zatwierdź ruch",
                                        command=lambda: self.controller.confirm_move(),
                                        font=("Helvetica", 12), bg="#4caf50", fg="white", bd=2, relief="solid",
                                        highlightbackground="#32a852")
        self.skip_button = tk.Button(self.labels_buttons_container, text="Pomiń turę",
                                     command=lambda: self.controller.skip_turn(),
                                     font=("Helvetica", 12), bg="#2196f3", fg="white", bd=2, relief="solid",
                                     highlightbackground="#1976d2")
        self.pickup_button = tk.Button(self.labels_buttons_container, text="Podnieś swoje litery",
                                       command=lambda: self.controller.pickup_letters(),
                                       font=("Helvetica", 12), bg="#ff9800", fg="white", bd=2, relief="solid",
                                       highlightbackground="#f57c00")
        self.end_game_button = tk.Button(self.labels_buttons_container, text="Zakończ grę",
                                         command=lambda: self.controller.end_game(),
                                         font=("Helvetica", 12), bg="#f44336", fg="white", bd=2, relief="solid",
                                         highlightbackground="#d32f2f")

        # Add spacing between buttons
        self.confirm_button.grid(row=0, column=1, pady=5, padx=(0, 5), sticky="nsew")
        self.skip_button.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")
        self.pickup_button.grid(row=0, column=3, pady=5, padx=5, sticky="nsew")
        self.end_game_button.grid(row=0, column=4, pady=5, padx=5, sticky="nsew")

    def update_round_label(self):
        index = get_player_index()
        self.round_label.config(text=f"Runda: {gv.ROUND_NUMBER}, Gracz: {gv.PLAYERS[index].get_name()}")
        self.letters_container.config(text=f"Literki: {gv.PLAYERS[index].get_rack_str()}")


class PlaceholderEntry(tk.Entry):
    """Single field of board"""

    def __init__(self, master=None, placeholder="", color='grey', row=0, col=0, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.parent = master
        self.placeholder = placeholder
        self.value = None
        self.approved_round = None
        self.row = row
        self.col = col
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<KeyRelease>", self.validate_input)

        self.put_placeholder()

    def put_placeholder(self):
        """put placeholder to entry - it's information about field"""
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def on_focus_in(self, event):
        """when focus in field remove the placeholder"""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def on_focus_out(self, event):
        """when stop focus in field insert the placeholder"""
        if not self.get():
            self.put_placeholder()

    def validate_input(self, event):
        """validate input letter to board"""
        if event.keysym != "BackSpace" and event.keysym.upper() not in LETTER_VALUES.keys():
            return
        if self.approved_round is not None and self.approved_round != gv.ROUND_NUMBER:
            if event.keysym == "BackSpace":
                self.insert(0, self.value)
            self.bell()
            self.delete(1, tk.END)
        entered_value = self.get().upper()
        if len(entered_value) > 1:
            value = entered_value[1]
        else:
            value = entered_value
        player_index = get_player_index()

        """if entry is empty or edit by user in this round"""
        if not self.approved_round or self.approved_round == gv.ROUND_NUMBER:
            """if incorrect letter"""
            if (entered_value and (
                    value not in LETTER_VALUES.keys()
                    or value not in gv.PLAYERS[player_index].get_letters_from_rack_arr()
            )):
                """if letter is incorrect but previous entered was correct then return previous correct letter"""
                if len(entered_value) > 1:
                    self.bell()
                    self.delete(1, tk.END)
                    value = entered_value[0]
                else:
                    """if letter is incorrect and entry was empty before"""
                    self.bell()
                    self.delete(0, tk.END)

            elif len(entered_value) == 0 and event.keysym == "BackSpace":
                """clear entry"""
                gv.BOARD.get_board_array()[self.row][self.col] = None
                gv.PLAYERS[get_player_index()].rack.append_letter(Tile(self.value))

                for l, letter in enumerate(gv.ACTUAL_WORD_WITH_COORDS):
                    if letter.get_x() == self.col and letter.get_y() == self.row:
                        gv.ACTUAL_WORD_WITH_COORDS.pop(l)
                self.value = None
                self.approved_round = None

            else:
                """if letter is correct then replace previous sign in entry if exist"""
                if len(entered_value) > 1:
                    self.delete(0)

                """if replace previous sign in entry"""
                if self.value is not None:
                    for l, letter in enumerate(gv.ACTUAL_WORD_WITH_COORDS):
                        if letter.get_x() == self.col and letter.get_y() == self.row:
                            gv.ACTUAL_WORD_WITH_COORDS.pop(l)
                    # break
                    gv.PLAYERS[get_player_index()].rack.append_letter(Tile(self.value))

                    user_letters = gv.PLAYERS[get_player_index()].rack.get_rack_arr()
                    for tile in user_letters:
                        if tile.get_letter() == value:
                            gv.PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                            break

                else:
                    """Add letter to empty field"""
                    user_letters = gv.PLAYERS[get_player_index()].rack.get_rack_arr()
                    for tile in user_letters:
                        if tile.get_letter() == value:
                            gv.PLAYERS[get_player_index()].rack.remove_from_rack(tile)
                            break

                self.approved_round = gv.ROUND_NUMBER
                self.value = value
                self.delete(0, tk.END)
                self.insert(0, self.value)
                gv.BOARD.get_board_array()[self.row][self.col] = Letter(self.row, self.col, self.value)
                gv.ACTUAL_WORD_WITH_COORDS.append(Letter(self.row, self.col, self.value))
        self.parent.controller.frames[ScrabbleBoardView].update_round_label()
