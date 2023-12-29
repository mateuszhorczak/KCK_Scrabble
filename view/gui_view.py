from tkinter import *
import tkinter as tk
from tkinter import ttk

from config.global_variables import GAME_INSTRUCTION, LETTER_VALUES, TRIPLE_LETTER_SCORE, DOUBLE_LETTER_SCORE, \
    DOUBLE_WORD_SCORE, TRIPLE_WORD_SCORE, ROUND_NUMBER
from config import global_variables as gv
from controller.controller import start_game, get_player_index


class ScrabbleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Scrabble Game")
        self.geometry("1980x1080")

        # creating a container
        container = tk.Frame(self)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (MainView, HelpBoardView, ScrabbleBoardView):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        container.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainView)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def confirm_move(self):
        # Logika dla zatwierdzenia ruchu
        gv.ROUND_NUMBER += 1
        self.frames[ScrabbleBoardView].update_round_label()
        pass

    def skip_turn(self):
        # Logika dla pominięcia tury
        gv.ROUND_NUMBER += 1
        self.frames[ScrabbleBoardView].update_round_label()
        pass

    def pickup_letters(self):
        # Logika dla podniesienia liter
        pass

    def end_game(self):
        # Logika dla zakończenia gry
        pass


class BaseView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class MainView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        gv.NUMBER_OF_PLAYERS = 2
        self.player_entries = []
        self.player_labels = []

        # Etykieta powitalna
        self.welcome_label = tk.Label(self, text="Witaj w grze Scrabble!", font=("Helvetica", 20))
        self.welcome_label.grid(row=1, column=1, columnspan=3, pady=20)

        # Kontener dla etykiet i pól wprowadzania
        self.players_container = tk.Frame(self)
        self.players_container.grid(row=2, column=1, columnspan=3)

        # Pola do wprowadzania nazw graczy i ich etykiety
        for i in range(gv.NUMBER_OF_PLAYERS):
            label = tk.Label(self.players_container, text=f"Gracz {i + 1}:", font=("Helvetica", 16))
            entry = tk.Entry(self.players_container, font=("Helvetica", 16))
            label.grid(row=i, column=0, padx=10, pady=10)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.player_labels.append(label)
            self.player_entries.append(entry)
            entry.bind("<Return>", lambda event, index=i: self.update_player_name(event, index))

        # Przyciski do zwiększania i zmniejszania liczby graczy
        self.decrease_button = tk.Button(self, text="-", command=self.decrease_players, font=("Helvetica", 16))
        self.decrease_button.grid(row=3, column=1, padx=20)

        self.num_players_label = tk.Label(self, text=str(gv.NUMBER_OF_PLAYERS), font=("Helvetica", 16))
        self.num_players_label.grid(row=3, column=2, padx=20)

        self.increase_button = tk.Button(self, text="+", command=self.increase_players, font=("Helvetica", 16))
        self.increase_button.grid(row=3, column=3, padx=20)

        # Przycisk do przechodzenia do kolejnego ekranu
        self.help_button = ttk.Button(self, text="Pomoc", command=lambda: self.controller.show_frame(HelpBoardView))
        self.help_button.grid(row=4, column=1, columnspan=3, pady=10)
        self.next_button = tk.Button(self, text="Rozpocznij grę",
                                     command=lambda: [self.controller.show_frame(ScrabbleBoardView), start_game(),
                                                      self.controller.frames[ScrabbleBoardView].update_round_label()],
                                     font=("Helvetica", 20))
        self.next_button.grid(row=5, column=1, columnspan=3, pady=20)

    def decrease_players(self):
        if gv.NUMBER_OF_PLAYERS > 2:
            # Usuń ostatnie pole do wprowadzania
            entry_to_remove = self.player_entries.pop()
            entry_to_remove.destroy()

            # Usuń ostatnią etykietę
            label_to_remove = self.player_labels.pop()
            label_to_remove.destroy()

            gv.NUMBER_OF_PLAYERS -= 1
            gv.PLAYERS_NICKNAMES[gv.NUMBER_OF_PLAYERS] = ''
            self.num_players_label.config(text=str(gv.NUMBER_OF_PLAYERS))

    def increase_players(self):
        if gv.NUMBER_OF_PLAYERS < 4:
            # Dodaj nowe pole do wprowadzania
            new_label = tk.Label(self.players_container, text=f"Gracz {gv.NUMBER_OF_PLAYERS + 1}:",
                                 font=("Helvetica", 16))
            new_entry = tk.Entry(self.players_container, font=("Helvetica", 16))
            new_label.grid(row=gv.NUMBER_OF_PLAYERS, column=0, padx=10, pady=10)
            new_entry.grid(row=gv.NUMBER_OF_PLAYERS, column=1, padx=10, pady=10)
            self.player_labels.append(new_label)
            self.player_entries.append(new_entry)
            new_entry.bind("<Return>", lambda event, index=gv.NUMBER_OF_PLAYERS: self.update_player_name(event, index))

            gv.NUMBER_OF_PLAYERS += 1
            self.num_players_label.config(text=str(gv.NUMBER_OF_PLAYERS))

    def update_player_name(self, event, index):
        # Zaktualizuj etykietę gracza po wciśnięciu Enter
        player_name = self.player_entries[index].get()
        self.player_labels[index].config(text=f"Gracz {index + 1}: {player_name}")
        gv.PLAYERS_NICKNAMES[index] = player_name
        print(gv.PLAYERS_NICKNAMES)


class HelpBoardView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller

        # Wycentrowany label nagłówkowy
        self.header_label = tk.Label(self, text="Pomoc Scrabble", font=("Helvetica", 20))
        self.header_label.grid(row=1, column=1, columnspan=3, pady=20)

        # Kontener dla lewej i prawej części
        self.left_container = tk.Frame(self)
        self.right_container = tk.Frame(self)
        self.left_container.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.right_container.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

        # Przykładowe informacje w lewej części planszy
        self.info_label_left = tk.Label(self.left_container, text="WARTOŚĆ LITER", font="helvetica 12 bold")
        self.info_label_left.grid(row=0, column=0, padx=10, pady=10)

        # Iterujemy po parach liter i ich wartościach
        for i, (key, value) in enumerate(LETTER_VALUES.items()):
            # Oblicz współrzędne wiersza i kolumny dla etykiety
            row = i // 2 + 1
            col = i % 2

            # Tworzymy etykietę dla pary liter i ich wartości
            label_text = f"{key} ma wartość: {value}"
            tk.Label(self.left_container, text=label_text, font="Helvetica 12 bold").grid(row=row, column=col * 2,
                                                                                          padx=10, pady=10)

        # Przykładowe informacje w prawej części planszy
        self.info_label_right = tk.Label(self.right_container, text=GAME_INSTRUCTION, wraplength=1000, justify="left",
                                         font="Helvetica 16 bold")
        self.info_label_right.grid(row=0, column=0, padx=10, pady=10)

        self.back_button = ttk.Button(self, text="Powrót", command=lambda: self.controller.show_frame(MainView))
        self.back_button.grid(row=4, column=1, columnspan=3, padx=10, pady=10)


class ScrabbleBoardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.board_data = [[' ' for _ in range(15)] for _ in range(15)]

        # Konfiguracja kolumn i wierszy planszy
        for i in range(16):
            # Ustawienie mniejszej szerokości kolumny dla numeracji po lewej stronie
            if i == 0:
                self.grid_columnconfigure(i, minsize=20, weight=0)
            else:
                self.grid_columnconfigure(i, minsize=120, weight=1, uniform="columns")

            # Ustawienie mniejszej wysokosci wiersza dla numeracji wierszy po na górze
            if i == 0:
                self.grid_rowconfigure(i, minsize=10, weight=0)
            else:
                self.grid_rowconfigure(i, minsize=60, weight=1, uniform="rows")

        # Numeracja siatki pól
        for i in range(15):
            # Numeracja kolumn na górze
            (tk.Label(self, text=str(i + 1), fg="red", font="Helvetica 12 bold")
             .grid(row=0, column=i + 1, sticky="nsew"))

            # Numeracja wierszy po lewej stronie
            (tk.Label(self, text=str(i + 1), fg="red", font="Helvetica 12 bold")
             .grid(row=i + 1, column=0, sticky="nsew"))

            for j in range(15):
                if (i, j) in TRIPLE_LETTER_SCORE:
                    entry = PlaceholderEntry(self, placeholder="3L", bg="deepskyblue", justify="center",
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in DOUBLE_LETTER_SCORE:
                    entry = PlaceholderEntry(self, placeholder="2L", bg="palegreen", justify="center",
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in TRIPLE_WORD_SCORE:
                    entry = PlaceholderEntry(self, placeholder="3W", bg="gold1", justify="center",
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

                elif (i, j) in DOUBLE_WORD_SCORE:
                    entry = PlaceholderEntry(self, placeholder="2W", bg="hotpink", justify="center",
                                             font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")
                else:
                    entry = PlaceholderEntry(self, justify="center", font=("Helvetica", 12), width=2)
                    entry.grid(row=i + 1, column=j + 1, sticky="nsew")

        # Dodatkowa ramka dla informacji o grze
        self.information_frame = tk.Frame(self)
        self.information_frame.grid(row=16, column=0, columnspan=16, sticky="nsew")

        # Informacje o rundzie i graczu
        self.round_label = tk.Label(self.information_frame, text=f"Runda: {ROUND_NUMBER}, tura: ",
                                    font=("Helvetica", 12))
        self.round_label.grid(row=0, column=0, columnspan=5, sticky="nsew")
        print(gv.PLAYERS)

        # Literki
        self.letters_container = tk.Label(self.information_frame, text="Literki", font=("Helvetica", 12))
        self.letters_container.grid(row=0, column=6, columnspan=5, sticky="nsew")

        # Dodatkowa ramka dla przycisków
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.grid(row=17, column=0, columnspan=16, sticky="nsew")

        # Przyciski
        self.confirm_button = tk.Button(self.buttons_frame, text="Zatwierdź ruch",
                                        command=lambda: self.controller.confirm_move())
        self.skip_button = tk.Button(self.buttons_frame, text="Pomiń turę", command=lambda: self.controller.skip_turn())
        self.pickup_button = tk.Button(self.buttons_frame, text="Podnieś swoje litery",
                                       command=lambda: self.controller.pickup_letters())
        self.end_game_button = tk.Button(self.buttons_frame, text="Zakończ grę",
                                         command=lambda: self.controller.end_game())

        self.confirm_button.grid(row=0, column=0, pady=5, sticky="nsew")
        self.skip_button.grid(row=0, column=1, pady=5, sticky="nsew")
        self.pickup_button.grid(row=0, column=2, pady=5, sticky="nsew")
        self.end_game_button.grid(row=0, column=3, pady=5, sticky="nsew")

        self.confirm_button.configure(foreground="gray70", background="whitesmoke", font="Helvetica 12 bold", border=1,
                                      relief="solid")
        self.skip_button.configure(foreground="gray70", background="whitesmoke", font="Helvetica 12 bold", border=1,
                                   relief="solid")
        self.pickup_button.configure(foreground="gray70", background="whitesmoke", font="Helvetica 12 bold", border=1,
                                     relief="solid")
        self.end_game_button.configure(foreground="gray70", background="whitesmoke", font="Helvetica 12 bold", border=1,
                                       relief="solid")

    def update_round_label(self):
        index = get_player_index()
        self.round_label.config(text=f"Runda: {gv.ROUND_NUMBER}, Gracz: {gv.PLAYERS[index].get_name()}")


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def on_focus_out(self, event):
        if not self.get():
            self.put_placeholder()
