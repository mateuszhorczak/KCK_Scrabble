from sys import maxsize
from tkinter import *
import tkinter as tk
from tkinter import ttk

from config.global_variables import GAME_INSTRUCTION, LETTER_VALUES


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


class BaseView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class MainView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.num_players = 2
        self.player_entries = []
        self.player_labels = []

        # Etykieta powitalna
        self.welcome_label = tk.Label(self, text="Witaj w grze Scrabble!", font=("Helvetica", 20))
        self.welcome_label.grid(row=1, column=1, columnspan=3, pady=20)

        # Kontener dla etykiet i pól wprowadzania
        self.players_container = tk.Frame(self)
        self.players_container.grid(row=2, column=1, columnspan=3)

        # Pola do wprowadzania nazw graczy i ich etykiety
        for i in range(self.num_players):
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

        self.num_players_label = tk.Label(self, text=str(self.num_players), font=("Helvetica", 16))
        self.num_players_label.grid(row=3, column=2, padx=20)

        self.increase_button = tk.Button(self, text="+", command=self.increase_players, font=("Helvetica", 16))
        self.increase_button.grid(row=3, column=3, padx=20)

        # Przycisk do przechodzenia do kolejnego ekranu
        self.help_button = ttk.Button(self, text="Pomoc", command=lambda: controller.show_frame(HelpBoardView))
        self.help_button.grid(row=4, column=1, columnspan=3, pady=10)
        self.next_button = tk.Button(self, text="Rozpocznij grę",
                                     command=lambda: controller.show_frame(ScrabbleBoardView), font=("Helvetica", 20))
        self.next_button.grid(row=5, column=1, columnspan=3, pady=20)

    def decrease_players(self):
        if self.num_players > 2:
            # Usuń ostatnie pole do wprowadzania
            entry_to_remove = self.player_entries.pop()
            entry_to_remove.destroy()

            # Usuń ostatnią etykietę
            label_to_remove = self.player_labels.pop()
            label_to_remove.destroy()

            self.num_players -= 1
            self.num_players_label.config(text=str(self.num_players))

    def increase_players(self):
        if self.num_players < 4:
            # Dodaj nowe pole do wprowadzania
            new_label = tk.Label(self.players_container, text=f"Gracz {self.num_players + 1}:", font=("Helvetica", 16))
            new_entry = tk.Entry(self.players_container, font=("Helvetica", 16))
            new_label.grid(row=self.num_players, column=0, padx=10, pady=10)
            new_entry.grid(row=self.num_players, column=1, padx=10, pady=10)
            self.player_labels.append(new_label)
            self.player_entries.append(new_entry)
            new_entry.bind("<Return>", lambda event, index=self.num_players: self.update_player_name(event, index))

            self.num_players += 1
            self.num_players_label.config(text=str(self.num_players))

    def update_player_name(self, event, index):
        # Zaktualizuj etykietę gracza po wciśnięciu Enter
        player_name = self.player_entries[index].get()
        self.player_labels[index].config(text=f"Gracz {index + 1}: {player_name}")

    def start_game(self):
        # Pobierz nazwy graczy z pól tekstowych
        player_names = [entry.get() for entry in self.player_entries]


class HelpBoardView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

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

        self.back_button = ttk.Button(self, text="Powrót", command=lambda: controller.show_frame(MainView))
        self.back_button.grid(row=4, column=1, columnspan=3, padx=10, pady=10)


class ScrabbleBoardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Przykładowe dane o planszy (15x15)
        self.board_data = [[' ' for _ in range(15)] for _ in range(15)]

        # Konfiguracja kolumn i wierszy planszy
        for i in range(15):
            self.grid_columnconfigure(i, minsize=30, weight=1, uniform="columns")
            self.grid_rowconfigure(i, minsize=30, weight=1, uniform="rows")

        # Numeracja siatki pól
        for i in range(15):
            for j in range(15):
                label = tk.Label(self, text=f"{i + 1} - {j + 1}", borderwidth=1, relief="solid", width=4, height=2,
                                 font=("Helvetica", 14))
                label.grid(row=i, column=j, sticky="nsew")

        # Informacje o rundzie i graczu
        self.round_label = tk.Label(self, text="Runda: 1, Gracz: 1", font=("Helvetica", 12))
        self.round_label.grid(row=15, column=0, columnspan=15, sticky="nsew")

        # Literki do przeciągania
        self.letters_container = tk.Frame(self)
        self.letters_container.grid(row=16, column=0, columnspan=15, sticky="nsew")

        # Przyciski
        self.confirm_button = ttk.Button(self, text="Zatwierdź ruch", command=lambda: self.controller.confirm_move)
        self.skip_button = ttk.Button(self, text="Pomiń turę", command=lambda: self.controller.skip_turn)
        self.pickup_button = ttk.Button(self, text="Podnieś swoje litery",
                                        command=lambda: self.controller.pickup_letters)
        self.end_game_button = ttk.Button(self, text="Zakończ grę", command=lambda: self.controller.end_game)

        self.confirm_button.grid(row=17, column=0, pady=5, sticky="nsew")
        self.skip_button.grid(row=17, column=1, pady=5, sticky="nsew")
        self.pickup_button.grid(row=17, column=2, pady=5, sticky="nsew")
        self.end_game_button.grid(row=17, column=3, pady=5, sticky="nsew")

    def update_round_label(self, round_number, player_number):
        self.round_label.config(text=f"Runda: {round_number}, Gracz: {player_number}")


# Kontroler (część, która obsługuje logikę gry)
class ScrabbleController:
    def __init__(self, root):
        self.root = root
        self.current_round = 1
        self.current_player = 1

        # Inicjalizacja widoku startowego
        self.start_view = MainView(root, self)
        self.start_view.grid(row=0, column=0, sticky="nsew")

        # Inicjalizacja widoku pomocy
        self.help_view = HelpBoardView(root, self)
        self.help_view.grid(row=0, column=0, sticky="nsew")

        # Inicjalizacja widoku planszy gry
        self.board_view = ScrabbleBoardView(root, self)
        self.board_view.grid(row=0, column=0, sticky="nsew")
        self.board_view.grid_remove()  # Ukryj planszę na początku

        # Ustawienie przycisków do zmiany widoku
        self.start_view.next_button.config(command=self.show_board)
        self.help_view.back_button.config(command=self.show_start)

    def show_start(self):
        self.board_view.grid_remove()
        self.start_view.grid()

    def show_board(self):
        self.start_view.grid_remove()
        self.board_view.grid()

    def confirm_move(self):
        # Logika dla zatwierdzenia ruchu
        pass

    def skip_turn(self):
        # Logika dla pominięcia tury
        pass

    def pickup_letters(self):
        # Logika dla podniesienia liter
        pass

    def end_game(self):
        # Logika dla zakończenia gry
        pass
