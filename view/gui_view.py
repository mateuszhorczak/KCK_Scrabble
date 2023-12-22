from tkinter import *
import tkinter as tk
from tkinter import ttk


class BaseView(tk.Frame):
    def __init__(self, root, title):
        super().__init__(root)
        self.root = root
        self.root.title(title)
        self.root.geometry("800x600")
        self.pack()  # Dodane wywołanie pack() w konstruktorze

    def pack_widgets(self):
        pass


class ScrabbleStartGui(BaseView):
    def __init__(self, root):
        super().__init__(root, "Scrabble Game - Start Screen")
        self.num_players = 2
        self.player_entries = []
        self.player_labels = []

        # Etykieta powitalna
        self.welcome_label = tk.Label(self, text="Witaj w grze Scrabble!", font=("Helvetica", 20))
        self.welcome_label.pack(pady=20)

        # Kontener dla etykiet i pól wprowadzania
        self.players_container = tk.Frame(self)
        self.players_container.pack()

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
        self.decrease_button.pack(side=tk.LEFT, padx=20)

        self.num_players_label = tk.Label(self, text=str(self.num_players), font=("Helvetica", 16))
        self.num_players_label.pack(side=tk.LEFT, padx=20)

        self.increase_button = tk.Button(self, text="+", command=self.increase_players, font=("Helvetica", 16))
        self.increase_button.pack(side=tk.LEFT, padx=20)

        # Przycisk do przechodzenia do kolejnego ekranu
        self.next_button = tk.Button(self, text="Rozpocznij grę", command=self.start_game, font=("Helvetica", 20))
        self.next_button.pack(pady=20)

        self.pack_widgets()

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
    def __init__(self, root):
        super().__init__(root, "Scrabble Game - Help Board")

        # Wycentrowany label nagłówkowy
        self.header_label = tk.Label(self, text="Pomoc Scrabble", font=("Helvetica", 20))
        self.header_label.pack(pady=20)

        # Kontenery na informacje
        self.info_container_top = tk.Frame(self)
        self.info_container_bottom = tk.Frame(self)
        self.info_container_top.pack(expand=True, fill="both")
        self.info_container_bottom.pack(expand=True, fill="both")

        # Przykładowe informacje w górnej części planszy
        self.info_label_top = tk.Label(self.info_container_top, text="Tu będą informacje (cz. górna)")
        self.info_label_top.pack(expand=True, fill="both")

        # Przykładowe informacje w dolnej części planszy
        self.info_label_bottom = tk.Label(self.info_container_bottom, text="Tu będą informacje (cz. dolna)")
        self.info_label_bottom.pack(expand=True, fill="both")

        self.pack_widgets()

    def pack_widgets(self):
        pass  # Nie ma potrzeby dodatkowego pakowania elementów w tym widoku