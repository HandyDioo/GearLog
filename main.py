import tkinter as tk
from database.db_manager import PengelolaDatabase
from ui.main_window import JendelaUtama

def utama():
    PengelolaDatabase()
    root = tk.Tk()
    app = JendelaUtama(root)
    root.mainloop()

if __name__ == "__main__":
    utama()