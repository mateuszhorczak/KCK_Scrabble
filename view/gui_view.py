from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext

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
        for F in (ScrabbleStartGui, HelpBoardGui):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        container.grid(row=0, column=0, sticky="nsew")

        self.show_frame(ScrabbleStartGui)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class BaseView(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class ScrabbleStartGui(BaseView):
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
        self.help_button = ttk.Button(self, text="Pomoc", command=lambda: controller.show_frame(HelpBoardGui))
        self.help_button.grid(row=4, column=1, columnspan=3, pady=10)
        self.next_button = tk.Button(self, text="Rozpocznij grę", command=self.start_game, font=("Helvetica", 20))
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



class HelpBoardGui(BaseView):
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
            tk.Label(self.left_container, text=label_text, font="Helvetica 12 bold").grid(row=row, column=col * 2, padx=10, pady=10)

        # Przykładowe informacje w prawej części planszy
        self.info_label_right = tk.Label(self.right_container, text=GAME_INSTRUCTION, wraplength=1000, justify="left", font="Helvetica 16 bold")
        self.info_label_right.grid(row=0, column=0, padx=10, pady=10)

        self.back_button = ttk.Button(self, text="Powrót", command=lambda: controller.show_frame(ScrabbleStartGui))
        self.back_button.grid(row=4, column=1, columnspan=3, padx=10, pady=10)



