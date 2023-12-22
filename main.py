from view.gui_view import ScrabbleStartGui as appGUI
from view.tui_view import ScrabbleApp as appTUI

from tkinter import *
from tkinter import ttk
import tkinter as tk

tui = False

if __name__ == "__main__":
    if tui:
        app = appTUI()
        app.run()
    else:
        # Tutaj utwórz kontroler dla swojej aplikacji

        # Utwórz główne okno
        root = tk.Tk()
        views_stack = []

        # Przekaż kontroler do GUI
        app = appGUI(root)

        # Uruchom główną pętlę
        root.mainloop()
