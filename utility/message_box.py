import tkinter as tk
from tkinter import messagebox

def show_message(title: str, message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()
