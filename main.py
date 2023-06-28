from db.database import UserSystem
from ui.start_window import *

def main():
    user_system = UserSystem()
    start_window = StartWindow(user_system)
    start_window.run()

if __name__ == "__main__":
    main()
