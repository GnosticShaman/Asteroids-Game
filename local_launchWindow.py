import arcade
import math
import random
import time
from arcade.gui import UIManager, UIInputBox, UIFlatButton

#Modifications: removed main from this file and to guiWindow.py
#import guiWindow

_width = 960
_height = 540
_offScreenBuffer = 50
shipSpeed = 10
angleSpeed = 5
laserSpeed = 15

# https://arcade.academy/resources.html#resources-images-space-shooter
possibleAsteroidType = [":resources:images/space_shooter/meteorGrey_big1.png",
                        ":resources:images/space_shooter/meteorGrey_big2.png",
                        ":resources:images/space_shooter/meteorGrey_big3.png",
                        ":resources:images/space_shooter/meteorGrey_big4.png"]

class mainMenuButton(UIFlatButton):
    def __init__(self):
        super().__init__(
            'Main Menu',
            center_x=480,
            center_y=_height / 2,
            width=200,
            height=40
        )
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
        #switch to game window
        mainMenuView = guiWindow.gameUI()
        mainMenuView.setUp()
        main_view.ui_manager.purge_ui_elements()
        window.show_view(mainMenuView)

class retryButton(UIFlatButton):
    def __init__(self):
        super().__init__(
            'Retry',
            center_x=480,
            center_y=_height / 4,
            width=200,
            height=40
        )
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
        print("Reset the game")

''' Working on game over screen. Trying to add
    an input box that will accept the player's
    name to add to highscores db, a main menu
    button, and a retry button '''
class gameover(arcade.View):
    def __init__(self, win: arcade.Window):
        super().__init__()
        self.window = win
        self.ui_manager = UIManager(self.window)
        '''self.nameInput = UIInputBox(width=300, height=100,
                               center_x=100, center_y=100)'''
        self.mainMenu = mainMenuButton()
        self.retry = retryButton()
        self.ui_manager.add_ui_element(self.mainMenu)
        self.ui_manager.add_ui_element(self.retry)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("GAME OVER", _width / 2, (3 * _height) / 4,
                         arcade.color.WHITE, 30,
                         anchor_x="center", anchor_y="center")
        #self.mainMenuButton.render()


class pause(arcade.View):
    def __init__(self, gameView):
        super().__init__()
        self.game_view = gameView

    # def on_show(self):
    #     arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text("PAUSED", 5, 500, arcade.color.WHITE, 18)

        ship = self.game_view.shipSprite
        asteroid = self.game_view.asteroidList
        powerup = self.game_view.powerupList

        ship.draw()
        asteroid.draw()
        powerup.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)


class ship(arcade.Sprite):
    def __init__(self, imageSource, scale):
        super().__init__(imageSource, scale)
        self.speed = 0
        self.powerupsTimeList = []

    def update(self):
        radAngles = math.radians(self.angle)

        self.angle += self.change_angle
        self.center_x += -self.speed * math.sin(radAngles)
        self.center_y += self.speed * math.cos(radAngles)

        self.checkPowerups()

        # Like the og game if you go all the way to any of
        # sides you will wrapp around to the opposite side
        if self.right < 0:
            self.left = _width
        if self.left > _width:
            self.right = 0
        if self.top > _height:
            self.bottom = 0
        if self.bottom < 0:
            self.top = _height

    ''' Add a powerup to the ship's stats
        and begin timing for when to remove it '''
    def getPowerup(self, powerup, expireTime):
        tmpExpTime = time.time() + expireTime
        self.powerupsTimeList.append([tmpExpTime, powerup])
        print("Got powerup +" + str(powerup.increaseSpeed) + " to speed. Exp: " + str(tmpExpTime))

    ''' Remove a powerup
        This is its own function to
        allow for easier creation of
        more powerups '''
    def losePowerup(self, powerup):
        self.speed -= powerup.increaseSpeed

    ''' To be called whenever the ship updates
        Checks if any powerups have expired and
        if so, then remove them '''
    def checkPowerups(self):
        for p in self.powerupsTimeList:
            if p[0] <= time.time():
                #self.losePowerup(p[1])
                print("Lost powerup +" + str(p[1].increaseSpeed) + " to speed.")
                self.powerupsTimeList.remove(p)

class laser(arcade.Sprite):
    def __init__(self, imageSource, scale):
        self.filename = imageSource
        self.scale = scale

    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))

class powerup(arcade.Sprite):
    ''' Currently pretty much a copy
        of the ship class '''
    def __init__(self, imageSource, scale):
        super().__init__(imageSource, scale)
        self.speed = (random.randrange(1, 5) / 4)
        self.increaseSpeed = 4
        self.filename = imageSource
        self.scale = scale

    def update(self):
        self.center_x += self.speed
        self.center_y += self.speed

        if self.right < 0:
            self.left = _width
        elif self.left > _width:
            self.right = 0
        if self.top < 0:
            self.bottom = _height
        elif self.bottom > _height:
            self.top = 0

class asteroid(arcade.Sprite):
    def __init__(self, imageSource, scale):
        super().__init__(imageSource, scale)
        self.filename = imageSource
        self.scale = scale

    def update(self):
        super().update()
        if self.right < -(_offScreenBuffer):
            self.left = _width + _offScreenBuffer

        if self.left > _width + _offScreenBuffer:
            self.right = -(_offScreenBuffer)

        if self.top > _height + _offScreenBuffer:
            self.bottom = -(_offScreenBuffer)

        if self.bottom < -(_offScreenBuffer):
            self.top = _height + _offScreenBuffer

class asteroidsWindow(arcade.View):
    def __init__(self):
        # Creates the window frame and sets the backgroudn color
        # Can change this to show a backround image instead
        super().__init__()
        arcade.set_background_color(arcade.csscolor.INDIGO)

        # Lists are used for movemetn and collisions
        self.shipList = None
        self.shipSprite = None
        self.laserList = None
        self.astroidList = None
        self.phyEngine = None
        self.fireSound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hitSound = arcade.load_sound(":resources:sounds/hit3.wav")
        self.lives = 3
        self.score = 0
        self.gameOver = False
        self.asteroidCount = 6
        self.threshold = 3

    def addAsteroids(self, count):
        for i in range(0, count):
            asteroidSprite = asteroid(possibleAsteroidType[random.randrange(4)], .5)

            asteroidSprite.center_x = random.randrange(0, _height)
            asteroidSprite.center_y = random.randrange(0, _width)

            asteroidSprite.change_x = random.random() * 2
            asteroidSprite.change_y = random.random() * 2

            asteroidSprite.change_angle = math.radians(random.random())
            self.asteroidList.append(asteroidSprite)

    def setUp(self):
        self.shipList = arcade.SpriteList()
        # This is empty right now but when it's populated
        # the ship will crash into the asteroid Sprites
        self.asteroidList = arcade.SpriteList()

        self.powerupList = arcade.SpriteList()
        for x in range(4):
            powerupSprite = powerup("Assets/powerup.png", 1)
            powerupSprite.center_x = _width / (x + 1)
            powerupSprite.center_y = _width / (x + 1)
            self.powerupList.append(powerupSprite)

        self.shipSprite = ship("Assets/bluecarrier.png", .125)
        self.shipSprite.center_x = _width / 2
        self.shipSprite.center_y = _height / 2

        self.laserList = arcade.SpriteList()

        self.addAsteroids(self.asteroidCount)
        self.shipList.append(self.shipSprite)

        # The second param makes it so that the first element pass through it
        # so for this we need to asteroids to overlap the ship so we have a
        # collision
        self.phyEngine = arcade.PhysicsEngineSimple(self.shipSprite, arcade.SpriteList())

    def on_draw(self):
        arcade.start_render()
        self.shipList.draw()
        self.laserList.draw()
        self.asteroidList.draw()
        self.powerupList.draw()

        score = "Score: {}".format(self.score)
        arcade.draw_text(score, 5, 500, arcade.color.WHITE, 18)

        lives = "Lives: {}".format(self.lives)
        arcade.draw_text(lives, 5, 475, arcade.color.WHITE, 18)

    def on_key_press(self, key, modifiers):
        ''' This is hacky but it works right now
            Adds the powerups to the ship speed
            because I can't access the shipSpeed
            var in the ship class '''
        adjShipSpeed = shipSpeed
        for x in self.shipSprite.powerupsTimeList:
            adjShipSpeed += x[1].increaseSpeed
        # Used to move the ship
        if key == arcade.key.W:
            self.shipSprite.speed = adjShipSpeed
            print(str(adjShipSpeed))
        elif key == arcade.key.S:
            self.shipSprite.speed = -adjShipSpeed
            print(str(adjShipSpeed))

        if key == arcade.key.SPACE:
            #Better but laser comes out side ways
            las = laser(":resources:images/space_shooter/laserBlue01.png", .5)

            las.change_x = -math.sin(math.radians(self.shipSprite.angle)) * laserSpeed
            las.change_y = math.cos(math.radians(self.shipSprite.angle)) * laserSpeed

            las.center_x = self.shipSprite.center_x
            las.center_y = self.shipSprite.center_y

            arcade.play_sound(self.fireSound)
            las.update()
            self.laserList.append(las)

        # Handles the rotation of the ship
        if key == arcade.key.A:
            self.shipSprite.change_angle = angleSpeed
        elif key == arcade.key.D:
            self.shipSprite.change_angle = -angleSpeed

        if key == arcade.key.ESCAPE:
            pauseGame = pause(self)
            self.window.show_view(pauseGame)

    def on_key_release(self, key, modifiers):
        # This should change to the the ship has momentum
        if key == arcade.key.W or key == arcade.key.S:
            self.shipSprite.speed = 0

        # Needed so that the ship doesn't just keep spinning
        if key == arcade.key.A or arcade.key.D:
            self.shipSprite.change_angle = 0

    def on_update(self, delta_time):
        self.shipList.update()
        self.laserList.update()
        self.asteroidList.update()
        self.phyEngine.update()
        self.powerupList.update()

        # Need to put ship collision here
        # Add check here to add more asteroids

        if self.lives == 0:
            self.gameOver = True
            ''' Draw game over screen '''
            gameOverScreen = gameover(self.window)
            self.window.show_view(gameOverScreen)

        if len(self.asteroidList) <= self.threshold:
            # Don't know how we should make the game increasingly
            # more difficult, but this does just that
            self.threshold += 1
            self.asteroidCount += self.asteroidCount // 2
            self.addAsteroids(self.asteroidCount)

        ''' Get the collisions between ship and powerups '''
        getPow = arcade.check_for_collision_with_list(self.shipSprite, self.powerupList)

        ''' For each collision add the powerup to
            the ship and remove it from the game '''
        for hitPow in getPow:
            self.shipList[0].getPowerup(hitPow, 5)
            hitPow.remove_from_sprite_lists()

        for rock in self.asteroidList:
            rockHits = arcade.check_for_collision_with_list(self.shipSprite, self.asteroidList)

            if len(rockHits) > 0:
                if self.lives > 0:
                    rockHits[0].remove_from_sprite_lists()
                    self.lives -= 1

        for laser in self.laserList:
            laserHit = arcade.check_for_collision_with_list(laser, self.asteroidList)

            # Delets that laser the asteroid that it hit
            for hit in laserHit:
                arcade.play_sound(self.hitSound)
                self.score += 100
                hit.remove_from_sprite_lists()
                laser.remove_from_sprite_lists()

            # This block will remove a laser once it has moved of
            # screen keeping our memory usage under control
            # print(len(self.laserList))
            if laser.right < 0:
                laser.remove_from_sprite_lists()
            if laser.left > _width:
                laser.remove_from_sprite_lists()
            if laser.top > _height:
                laser.remove_from_sprite_lists()
            if laser.bottom < 0:
                laser.remove_from_sprite_lists()
            # print(len(self.laserList))
