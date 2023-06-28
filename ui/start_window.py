from tkinter import *
from utility.message_box import messagebox
from db.database import UserSystem

from game.logic import GameLogic
from ui.game_ui import GameUI



# 滑鼠事件
class ButtonAnimation:
    def set_button_animation(self, button):
        button.bind("<Enter>", self.on_button_enter)
        button.bind("<Leave>", self.on_button_leave)
    def on_button_enter(self, event):
        event.widget.config(bg="lightblue")

    def on_button_leave(self, event):
        event.widget.config(bg="SystemButtonFace")



class StartWindow(ButtonAnimation):
    def __init__(self, user_system: UserSystem):
        self.user_system = user_system

        self.window = Tk()
        self.window.title("Select Mode")
        self.window.geometry("250x200")

        self.offline_button = Button(self.window, text="Offline", command=self.show_options_window("offline"))
        self.offline_button.pack(fill='both', expand=True)
        self.set_button_animation(self.offline_button)

        self.online_button = Button(self.window, text="Online", command=self.show_options_window("online"))
        self.online_button.pack(fill='both', expand=True)
        self.set_button_animation(self.online_button)

        self.window.bind("<Tab>", self.on_tab_pressed)
        self.window.bind("<Return>", self.on_enter_pressed)

        self.current_button = None
    def on_enter_pressed(self, event):
        if self.current_button:
            self.current_button.invoke()

    def on_tab_pressed(self, event):
        if self.offline_button == self.current_button:
            self.online_button.focus_set()
            self.current_button = self.online_button
        else:
            self.offline_button.focus_set()
            self.current_button = self.offline_button

    def show_options_window(self, mode):
        def show_options():
            self.window.destroy()
            options_window = OptionsWindow(self.user_system, mode)
            options_window.run()
        return show_options

    def run(self):
        self.window.mainloop()

class OptionsWindow(ButtonAnimation):
    def __init__(self, user_system: UserSystem, mode):
        self.window = Tk()
        self.window.title(f"{mode.capitalize()} Options")
        self.window.geometry("250x200")

        self.mode = mode

        self.username_label = Label(self.window, text="Username")
        self.username_label.pack()
        self.username_entry = Entry(self.window)
        self.username_entry.pack()

        self.password_label = Label(self.window, text="Password")
        self.password_label.pack()
        self.password_entry = Entry(self.window, show="*")
        self.password_entry.pack()

        self.login_button = Button(self.window, text="Login", command=self.login)
        self.login_button.pack(pady=5)
        self.set_button_animation(self.login_button)

        self.register_button = Button(self.window, text="Register", command=self.register)
        self.register_button.pack(pady=5)
        self.set_button_animation(self.register_button)

        if not self.mode == "online":
            self.play_button = Button(self.window, text="Play", command=self.game_start)
            self.play_button.pack(pady=5)
            self.set_button_animation(self.play_button)

        self.user_system = user_system
        self.user = None

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_system.login(username, password):
            self.user = username
            self.window.destroy()
            game = GameLogic()
            game_state = self.user_system.load_game_state(self.user) if not self.mode else None
            ui = GameUI(self.user_system, game, self.user, game_state, online_mode=self.mode == "online")
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
        ui = GameUI(self.user_system, game, online_mode=self.mode == "online")
        ui.start()

    def run(self):
        self.window.mainloop()
        return self.user
