import arcade
from arcade.gui import UIManager, UIInputBox, UIFlatButton
import database

import guiWindow
import launchWindow

_width = 960
_height = 540

class mainMenuButton(UIFlatButton):
    def __init__(self, curWin, uiMan):
        super().__init__(
            'Main Menu',
            center_x=480,
            center_y=_height / 2 - 140,
            width=200,
            height=40
        )
        self.curWindow = curWin
        self.ui_manager = uiMan
        #button colors, set them to whatever
        self.set_style_attrs(
            font_color=arcade.color.BLACK,
            font_color_hover=arcade.color.BLACK,
            font_color_press=arcade.color.BLACK,
            bg_color=(128, 128, 128), #Gray
            bg_color_hover=(211, 211, 211), #Light Gray
            bg_color_press=(255, 255, 255), #White
            border_color=(64, 224, 208), #Turquoise
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )

    def on_click(self):
        mainMenuWindow = guiWindow.gameUI(self.curWindow)
        mainMenuWindow.setup()
        self.ui_manager.purge_ui_elements()
        self.curWindow.show_view(mainMenuWindow)


class retryButton(UIFlatButton):
    def __init__(self, curWin, uiMan):
        super().__init__(
            'Retry',
            center_x=480,
            center_y=_height / 2 - 80,
            width=200,
            height=40
        )
        self.curWindow = curWin
        self.ui_manager = uiMan
        #button colors, set them to whatever
        self.set_style_attrs(
            font_color=arcade.color.BLACK,
            font_color_hover=arcade.color.BLACK,
            font_color_press=arcade.color.BLACK,
            bg_color=(128, 128, 128), #Gray
            bg_color_hover=(211, 211, 211), #Light Gray
            bg_color_press=(255, 255, 255), #White
            border_color=(64, 224, 208), #Turquoise
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )

    def on_click(self):
        gameView = launchWindow.asteroidsWindow()
        gameView.setUp()
        self.ui_manager.purge_ui_elements()
        self.curWindow.show_view(gameView)

class submitButton(UIFlatButton):
    def __init__(self, curWin, uiMan, entryBox, s):
        super().__init__(
            'Submit Score',
            center_x=480,
            center_y=_height / 2 - 20,
            width=250,
            height=40
        )
        self.curWindow = curWin
        self.ui_manager = uiMan
        self.entry = entryBox
        self.score = s
        self.dbCon = database.db_connection()
        #button colors, set them to whatever
        self.set_style_attrs(
            font_color=arcade.color.BLACK,
            font_color_hover=arcade.color.BLACK,
            font_color_press=arcade.color.BLACK,
            bg_color=(128, 128, 128), #Gray
            bg_color_hover=(211, 211, 211), #Light Gray
            bg_color_press=(255, 255, 255), #White
            border_color=(64, 224, 208), #Turquoise
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )

    def on_click(self):
        print("Submitted score for " + self.entry.text + " as " + str(self.score))
        self.dbCon.insert_player(self.entry.text)
        self.dbCon.update_sp(self.entry.text, self.score)

''' Working on game over screen. Trying to add
    an input box that will accept the player's 
    name to add to highscores db, a main menu
    button, and a retry button '''
class gameover(arcade.View):
    def __init__(self, s):
        super().__init__()
        self.finScore = s
        self.nameInput = UIInputBox(width=300, height=50,
                               center_x=_width/2, center_y=_height/2 + 60)
        self.gameOverWindow = self.window
        self.gameOver_ui_manager = UIManager(self.gameOverWindow)
        self.mainMenu = mainMenuButton(self.window, self.gameOver_ui_manager)
        self.retry = retryButton(self.window, self.gameOver_ui_manager)
        self.submit = submitButton(self.window, self.gameOver_ui_manager, self.nameInput, self.finScore)

    def setup(self):
        self.gameOver_ui_manager.purge_ui_elements()
        self.gameOver_ui_manager.add_ui_element(self.mainMenu)
        self.gameOver_ui_manager.add_ui_element(self.retry)
        self.gameOver_ui_manager.add_ui_element(self.nameInput)
        self.gameOver_ui_manager.add_ui_element(self.submit)

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.csscolor.CRIMSON)
        arcade.draw_text("GAME OVER", _width / 2, _height - 40,
                         arcade.color.WHITE, 30,
                         anchor_x="center", anchor_y="center")
        arcade.draw_text("Final Score: " + str(self.finScore), _width / 2, _height - 100,
                         arcade.color.WHITE, 30,
                         anchor_x="center", anchor_y="center")

    def on_show_view(self):
        self.setup()