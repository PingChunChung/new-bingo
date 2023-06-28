
from tkinter import *
from utility.message_box import messagebox
from db.database import UserSystem

from game.game_logic import GameLogic
from ui.game_ui import GameUI

class LoginWindow:
    def __init__(self, user_system: UserSystem):
        self.window = Tk()
        self.window.title("Login or Register")
        self.window.geometry("250x200")

        self.username_label = Label(self.window, text="Username")
        self.username_label.pack()
        self.username_entry = Entry(self.window)
        self.username_entry.pack()

        self.password_label = Label(self.window, text="Password")
        self.password_label.pack()
        self.password_entry = Entry(self.window)
        self.password_entry.pack()

        self.login_button = Button(self.window, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = Button(self.window, text="Register", command=self.register)
        self.register_button.pack()

        self.play_button = Button(self.window, text="Play", command=self.game_start)
        self.play_button.pack()

        self.user_system = user_system
        self.user = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_system.login(username, password):
            self.user = username
            self.window.destroy()
            game = GameLogic()
            game_state = self.user_system.load_game_state(self.user)
            ui = GameUI(self.user_system, game, self.user, game_state)
            ui.start()
        else:
            messagebox.showinfo("Error", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_system.register(username, password):
            messagebox.showinfo("Success", "Registration successful, you can now log in")

        else:
            messagebox.showinfo("Error", "Username already exists")

    def game_start(self):
        self.window.destroy()
        game = GameLogic()
        ui = GameUI(self.user_system, game)
        ui.start()

    def run(self):
        self.window.mainloop()
        return self.user