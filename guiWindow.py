import arcade
import multiplayerClient
import launchWindow
import arcade.gui
from arcade.gui import UIFlatButton, UIGhostFlatButton, UIManager
from arcade.gui.ui_style import UIStyle

#window properties
_width = 960
_height = 540
_frame = "Asteroids"

class SinglePlayerButton(UIFlatButton):
    def __init__(self, y_val, curWin, uiMan):
        super().__init__(
            'Single Player',
            center_x=480,
            center_y=y_val,
            width=200,
            height=40
        )
        self.curWindow = curWin
        self.ui_manager = uiMan
        #button colors, change them however you see fit
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
        #switch to game window
        gameView = launchWindow.asteroidsWindow()
        gameView.setUp()
        self.ui_manager.purge_ui_elements()
        self.curWindow.show_view(gameView)

class MultiPlayerButton(UIFlatButton):
    def __init__(self, y_val, curWin, uiMan):
        super().__init__(
            'Multi Player',
            center_x=480,
            center_y=y_val,
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
        gameView = multiplayerClient.ConnectScreen(window)
        self.ui_manager.purge_ui_elements()
        self.curWindow.show_view(gameView)

class gameUI(arcade.View):
    def __init__(self, win: arcade.Window):
        super().__init__()
        self.window = win
        self.ui_manager = UIManager(self.window)

    def setup(self):
        self.ui_manager.purge_ui_elements()
        #default style sheet
        UIStyle.default_style().set_class_attrs(
            'buttons',
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(135, 21, 25),
            bg_color_hover=(135, 21, 25),
            bg_color_press=(122, 21, 24),
            border_color=(135, 21, 25),
            border_color_hover=arcade.color.WHITE,
            border_color_press=arcade.color.WHITE
        )
        #add buttons to UI manager
        self.ui_manager.add_ui_element(SinglePlayerButton(self.window.height // 2, self.window, self.ui_manager))
        self.ui_manager.add_ui_element(MultiPlayerButton(self.window.height // 3, self.window, self.ui_manager))

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.csscolor.INDIGO)
        #renders title
        arcade.draw_text(
            "Asteroids",
            375,
            395,
            arcade.color.BLACK,
            40,
            align="center"
        )


    def on_show_view(self):
        self.setup()

if __name__ == '__main__':
    window = arcade.Window(_width, _height, _frame)
    main_view = gameUI(window)
    window.show_view(main_view)
    arcade.run()
