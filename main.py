from game.game_logic import GameLogic
from ui.game_ui import GameUI
from db.database import UserSystem
from ui.start_menu import LoginWindow

def main():
    user_system = UserSystem()
    login_window = LoginWindow(user_system)
    user = login_window.run()


if __name__ == "__main__":
    main()
