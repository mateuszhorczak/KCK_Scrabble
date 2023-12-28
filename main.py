from view.gui_view import ScrabbleApp as appGUI
from view.tui_view import ScrabbleApp as appTUI

from tkinter import *
from tkinter import ttk
import tkinter as tk

tui = True

if __name__ == "__main__":
    if tui:
        app = appTUI()
        app.run()
    else:
        app = appGUI()
        app.mainloop()
