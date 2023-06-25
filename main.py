from game.game_logic import GameLogic
from ui.game_ui import GameUI

def main():
    game = GameLogic()
    ui = GameUI(game)
    ui.start()

if __name__ == "__main__":
    main()
