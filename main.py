from view.gui_view import ScrabbleApp as appGUI
from view.tui_view import ScrabbleApp as appTUI

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None


def start_application(use_gui):
    if use_gui:
        app = appGUI()
        app.mainloop()
    else:
        app = appTUI()
        app.run()


def run_with_gui():
    root = tk.Tk()
    root.title("Scrabble Game - Wybór interfejsu")
    root.geometry("400x200")

    style = ttk.Style()
    style.configure("TButton", padding=10, font=("Helvetica", 12), background="darkolivegreen2",
                    foreground="darkolivegreen4")

    def start_gui():
        root.destroy()
        start_application(True)

    def start_tui():
        root.destroy()
        start_application(False)

    ttk.Button(root, text="Uruchom interfejs tekstowy", command=start_tui, style="TButton").pack(pady=10)
    ttk.Button(root, text="Uruchom interfejs graficzny", command=start_gui, style="TButton").pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    if tk:
        run_with_gui()
    else:
        print("Biblioteka tkinter nie jest dostępna. Uruchamiam interfejs tekstowy.")
        start_application(False)
