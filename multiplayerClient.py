import arcade
import math
import time
import guiWindow
import multiplayerServer
import launchWindow
import arcade.gui
from arcade.gui import UIFlatButton, UIGhostFlatButton, UIManager
from arcade.gui.ui_style import UIStyle
from PodSixNet.Connection import connection, ConnectionListener

_width = 960
_height = 540
_offScreenBuffer = 50
shipSpeed = 10
angleSpeed = 5
laserSpeed = 15

class InputBoxButton(UIGhostFlatButton):
    def __init__(self, input_box, curWin, uiMan):
        super().__init__(
            'Enter Username',
            center_x=_width // 2,
            center_y=_height // 4,
            width=300,
            height=50
        )
        self.input_box = input_box
        self.curWindow = curWin
        self.ui_manager = uiMan
        #button colors, change them however you see fit
        self.set_style_attrs(
            font_color=arcade.csscolor.BLACK,
            font_color_hover=arcade.csscolor.BLACK,
            font_color_press=arcade.color.BLACK,
            bg_color=arcade.color.GREEN,
            bg_color_hover=arcade.color.LIME,
            bg_color_press=(255, 255, 255), #White
            border_color=(64, 224, 208), #Turquoise
            border_color_hover=arcade.color.BLACK,
            border_color_press=arcade.color.BLACK
        )

    def on_click(self):
        gameView = asteroidsClientWindow("192.168.1.9", 2000, self.input_box.text, self.curWindow)
        gameView.setUp()
        self.ui_manager.purge_ui_elements()
        self.curWindow.show_view(gameView)


class ConnectScreen(arcade.View):
    def __init__(self, win: arcade.Window):
        super().__init__()
        self.window = win
        self.ui_manager = UIManager(self.window)
        self.ui_manager.purge_ui_elements()
        ui_input_box = arcade.gui.UIInputBox(center_x=_width // 2,center_y=_height // 2,width=300)
        ui_input_box.text = ''
        ui_input_box.cursor_index = len(ui_input_box.text)
        self.ui_manager.add_ui_element(ui_input_box)
        self.ui_manager.add_ui_element(InputBoxButton(ui_input_box, self.window, self.ui_manager))

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.csscolor.INDIGO)


class asteroidsClientWindow(ConnectionListener, arcade.View):
    def __init__(self, host, port, name, curWin):
        self.Connect((host, port))
        #add stuff here
        arcade.View.__init__(self)
        arcade.set_background_color(arcade.csscolor.INDIGO)
        # Lists are used for movemetn and collisions
        self.current_player = multiplayerServer.Player(str(name))
        self.playerList = arcade.SpriteList()
        self.playerList.append(self.current_player)
        self.laserList = None
        self.asteroidList = None
        self.phyEngine = None
        self.fireSound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hitSound = arcade.load_sound(":resources:sounds/hit3.wav")
        self.gameOver = False
        self.asteroidCount = 6
        self.threshold = 3
        self.window = curWin

    def Loop(self):
        connection.Pump()
        self.Pump()

    def Network_get_states(self, data):
        print("get_states action satisfied")
        self.asteroidList = arcade.SpriteList()
        for i in data['asteroids']:
            temp_ast = launchWindow.asteroid(i[0], i[1])
            temp_ast.center_x = i[2]
            temp_ast.center_y = i[3]
            self.asteroidList.append(temp_ast)
        self.laserList = arcade.SpriteList()
        for i in data['lasers']:
            temp_las = launchWindow.laser(i[0], i[1])
            temp_las.center_x = i[2]
            temp_las.center_y = i[3]
            self.laserList.append(temp_las)
        self.powerupList = arcade.SpriteList()
        for i in data['powerups']:
            temp_pwu = launchWindow.powerup(i[0], i[1])
            temp_pwu.center_x = i[2]
            temp_pwu.center_y = i[3]
            self.powerupList.append(temp_pwu)
        #for i in data['powerups']:
        #self.playerList.sprite_list = arcade.SpriteList()
        #for i in data['players']:


    def setUp(self):
        self.Loop()
        self.asteroidList = arcade.SpriteList()
        self.powerupList = arcade.SpriteList()
        self.laserList = arcade.SpriteList()
        # The second param makes it so that the first element pass through it
        # so for this we need to asteroids to overlap the ship so we have a
        # collision
        self.phyEngine = arcade.PhysicsEngineSimple(self.current_player, arcade.SpriteList())
        temp = multiplayerServer.encode_sprite(self.current_player)
        connection.Send({"action":"add_player", "name":self.current_player.username, "ship":temp})

    def on_draw(self):
        arcade.start_render()
        self.playerList.draw()
        self.laserList.draw()
        self.asteroidList.draw()
        self.powerupList.draw()
        self.current_player.draw()
        score = "Score: {}".format(self.current_player.score)
        arcade.draw_text(score, 5, 500, arcade.color.WHITE, 18)
        lives = "Lives: {}".format(self.current_player.lives)
        arcade.draw_text(lives, 5, 475, arcade.color.WHITE, 18)

    def on_key_press(self, key, modifiers):
        ''' This is hacky but it works right now
            Adds the powerups to the ship speed
            because I can't access the shipSpeed
            var in the ship class '''
        adjShipSpeed = shipSpeed
        for x in self.current_player.powerupsTimeList:
            adjShipSpeed += x[1].increaseSpeed
        # Used to move the ship
        if key == arcade.key.ESCAPE:
            connection.Send({"action":"remove_player", "name":self.current_player.username})
            connection.Send({"action":"disconnected"})
        if key == arcade.key.W:
            self.current_player.speed = adjShipSpeed
            connection.Send({"action":"on_key_press", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})
        elif key == arcade.key.S:
            self.current_player.speed = -adjShipSpeed
            connection.Send({"action":"on_key_press", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})

        if key == arcade.key.SPACE:
            #Better but laser comes out side ways
            las = launchWindow.laser(":resources:images/space_shooter/laserBlue01.png", .5)

            las.change_x = -math.sin(math.radians(self.current_player.angle)) * laserSpeed
            las.change_y = math.cos(math.radians(self.current_player.angle)) * laserSpeed

            las.center_x = self.current_player.center_x
            las.center_y = self.current_player.center_y

            arcade.play_sound(self.fireSound)
            las.update()
            self.laserList.append(las)

        # Handles the rotation of the ship
        if key == arcade.key.A:
            self.current_player.change_angle = angleSpeed
            connection.Send({"action":"on_key_press", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})

        elif key == arcade.key.D:
            self.current_player.change_angle = -angleSpeed
            connection.Send({"action":"on_key_press", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})

        '''if key == arcade.key.ESCAPE:
            pauseGame = pause(self)
            self.window.show_view(pauseGame)'''

    def on_key_release(self, key, modifiers):
        # This should change to the the ship has momentum
        if key == arcade.key.W or key == arcade.key.S:
            self.current_player.speed = 0
            connection.Send({"action":"on_key_release", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})
            #self.Loop()

        # Needed so that the ship doesn't just keep spinning
        if key == arcade.key.A or arcade.key.D:
            self.current_player.change_angle = 0
            connection.Send({"action":"on_key_release", "ship":multiplayerServer.encode_sprite(self.current_player), "name":self.current_player.username})
            #self.Loop()

    def on_update(self, delta_time):
        self.playerList.update()
        self.laserList.update()
        self.Loop()
