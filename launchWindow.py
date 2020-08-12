import arcade
import math
import random
import time

#Modifications: removed main from this file and to guiWindow.py
import guiWindow
import gameoverWindow

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
        self.filename = imageSource
        self.scale = scale

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
        super().__init__(imageSource, scale)
        self.filename = imageSource
        self.scale = scale

    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))

class spawnSystem(object):
    def __init__(self):
        self.enemyStages = []
        self.powerupStages = []
        self.currentLevel = 0
        self.maxNumEnemies = 10
        self.curNumEnemies = self.maxNumEnemies
        self.shouldSpawn = True
        self.noMoreEnemies = False

        ''' I know manually creating things is bad,
            but this seemed like the best way to
            balance the spawn system '''
        ''' Stage 1 '''
        self.enemyStages.append(self.createLevel(5, 0, 0))
        self.powerupStages.append(self.createPowers(1, 2))
        ''' Stage 2 '''
        self.enemyStages.append(self.createLevel(7, 4, 0))
        self.powerupStages.append(self.createPowers(1, 2))
        ''' Stage 3'''
        self.enemyStages.append(self.createLevel(10, 4, 3))
        self.powerupStages.append(self.createPowers(1, 3))
        ''' Stage 4 '''
        self.enemyStages.append(self.createLevel(10, 6, 5))
        self.powerupStages.append(self.createPowers(2, 4))
        ''' Stage 5 '''
        self.enemyStages.append(self.createLevel(14, 8, 7))
        self.powerupStages.append(self.createPowers(2, 4))
        ''' Stage 6 '''
        self.enemyStages.append(self.createLevel(10, 10, 10))
        self.powerupStages.append(self.createPowers(3, 4))
        ''' Stage 7 '''
        self.enemyStages.append(self.createLevel(10, 15, 13))
        self.powerupStages.append(self.createPowers(3, 5))
        ''' Stage 8 '''
        self.enemyStages.append(self.createLevel(13, 18, 18))
        self.powerupStages.append(self.createPowers(4, 5))
        ''' Stage 9 '''
        self.enemyStages.append(self.createLevel(5, 23, 22))
        self.powerupStages.append(self.createPowers(5, 5))
        ''' Stage 10 '''
        self.enemyStages.append(self.createLevel(2, 26, 24))
        self.powerupStages.append(self.createPowers(5, 5))

        ''' Get the current enemies and powerups '''
        self.currentEnemies = self.enemyStages[self.currentLevel]
        self.currentPowers = self.powerupStages[self.currentLevel]

        ''' Print info for debugging '''
        print("----")
        print("Current level " + str(self.currentLevel + 1))
        print("Number of Enemies (" + str(len(self.currentEnemies)) + ")")
        print("Number of Powers (" + str(len(self.currentPowers)) + ")")
        print("----")

    ''' Returns an array of enemies
        that is a subset of the entire
        level. Used to make the enemies
        spawn in over time and not all
        at once '''
    def getLevelEnemies(self):
        if self.currentLevel == 9 and not self.shouldSpawn:
            return arcade.SpriteList()
        else:
            tmpStageEnemies = arcade.SpriteList()
            i = 0

            ''' Go through current enemy list and
                add enemies on to the temporary
                list until either the max number
                of enemies is added or the level
                list is empty '''
            for e in self.currentEnemies:
                if i < self.maxNumEnemies:
                    tmpStageEnemies.append(e)
                    i += 1

            ''' This is the amount of enemies
                we added '''
            self.curNumEnemies = i

            ''' If we didn't add any enemies, then
                go to the next level '''
            if self.curNumEnemies == 0:
                self.shouldSpawn = self.nextLevel()
                tmpStageEnemies = self.getLevelEnemies()
                self.curNumEnemies = self.maxNumEnemies

            ''' Return the new list of enemies '''
            return tmpStageEnemies

    def nextLevel(self):
        ''' Check to make sure we're not
            at the last level '''
        if self.currentLevel < 9:
            ''' Increment the level and update
                the current enemies/powers lists '''
            self.currentLevel += 1
            self.currentEnemies = self.enemyStages[self.currentLevel]
            self.currentPowers = self.powerupStages[self.currentLevel]

            ''' Printing for debugging '''
            print("----")
            print("Current level " + str(self.currentLevel + 1))
            print("Number of Enemies (" + str(len(self.currentEnemies)) + ")")
            print("Number of Powers (" + str(len(self.currentPowers)) + ")")
            print("----")
            return True
        else:
            ''' Printing for debugging '''
            print("Game is over here")
            return False

    ''' Will choose between 3 powerups
        randomly. Only able to choose 1-up
        once. Returns the list of powerups
        for that level '''
    def createPowers(self, lowCount, highCount):
        powerOptions = ["Speed", "Bullets", "1-up"]
        powerRanges = 3
        tmpList = []
        amount = random.randrange(lowCount, highCount + 1)
        for i in range(amount):
            randomPower = random.randrange(powerRanges)
            if randomPower == 2:
                powerRanges = 2
            tmpList.append(powerOptions[randomPower])
        return tmpList

    ''' Creates a list of asteroid sprites for
        a level using 3 different speed amounts.
        Returns the final list of enemies '''
    def createLevel(self, cSlow, cMed, cFast):
        tmpList = arcade.SpriteList()
        negativeOptions = [-1, 1]
        for i in range(cSlow):
            randNegative = negativeOptions[random.randrange(0, 2)]
            tmpList.append(self.addAsteroidsSpawner(randNegative * 0.5))
        for i in range(cMed):
            randNegative = negativeOptions[random.randrange(0, 2)]
            tmpList.append(self.addAsteroidsSpawner(randNegative * 1.5))
        for i in range(cFast):
            randNegative = negativeOptions[random.randrange(0, 2)]
            tmpList.append(self.addAsteroidsSpawner(randNegative * 2.5))
        return tmpList

    ''' Creates one asteroid for the spawner using a
        given speed '''
    def addAsteroidsSpawner(self, speed):
        ''' Choose a random sprite '''
        asteroidSprite = asteroid(possibleAsteroidType[random.randrange(4)], .5)

        ''' Create a safe zone around the player where asteroids
            can't spawn '''
        safeBoxDims = 100
        spawnCoordsY = [[0, _height / 2 - safeBoxDims], [_height / 2 + safeBoxDims, _height]]
        chosenY = spawnCoordsY[random.randrange(0, 2)]
        spawnCoordsX = [[0, _width / 2 - safeBoxDims], [_width / 2 + safeBoxDims, _width]]
        chosenX = spawnCoordsX[random.randrange(0, 2)]

        ''' Spawn the asteroid somewhere randomly within
            its quadrant '''
        asteroidSprite.center_y = random.randrange(chosenY[0], chosenY[1])
        asteroidSprite.center_x = random.randrange(chosenX[0], chosenX[1])

        ''' Choose a random speed and angle'''
        asteroidSprite.change_x = (random.random() + 1) * speed
        asteroidSprite.change_y = (random.random() + 1) * speed
        asteroidSprite.change_angle = math.radians(random.random())

        ''' Return the sprite '''
        return asteroidSprite

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
        self.spawnSys = None

        self.fireSound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hitSound = arcade.load_sound(":resources:sounds/hit3.wav")

        self.lives = 1
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

        self.spawnSys = spawnSystem()

        self.shipSprite = ship("Assets/bluecarrier.png", .125)
        self.shipSprite.center_x = _width / 2
        self.shipSprite.center_y = _height / 2

        self.laserList = arcade.SpriteList()

        #self.addAsteroids(self.asteroidCount)
        self.asteroidList = self.spawnSys.getLevelEnemies()
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
        elif key == arcade.key.S:
            self.shipSprite.speed = -adjShipSpeed

        if key == arcade.key.N:
            self.spawnSys.nextLevel()
            self.asteroidList = self.spawnSys.getLevelEnemies()
            self.gameOver = not self.spawnSys.shouldSpawn
            if self.spawnSys.currentLevel == 9:
                self.gameOver = True

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

        if self.lives == 0 or not self.spawnSys.shouldSpawn:
            self.gameOver = True
            ''' Draw game over screen '''
            gameOverScreen = gameoverWindow.gameover(self.score)
            self.window.show_view(gameOverScreen)

        '''if len(self.asteroidList) <= self.threshold:
            # Don't know how we should make the game increasingly
            # more difficult, but this does just that
            self.threshold += 1
            self.asteroidCount += self.asteroidCount // 2
            self.addAsteroids(self.asteroidCount)'''
        if self.spawnSys.curNumEnemies < self.spawnSys.maxNumEnemies:
                self.asteroidList = self.spawnSys.getLevelEnemies()

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
                    self.spawnSys.curNumEnemies -= 1
                    print("collision" + str(self.spawnSys.curNumEnemies))

        for laser in self.laserList:
            laserHit = arcade.check_for_collision_with_list(laser, self.asteroidList)

            # Delets that laser the asteroid that it hit
            for hit in laserHit:
                arcade.play_sound(self.hitSound)
                self.score += 100
                hit.remove_from_sprite_lists()
                laser.remove_from_sprite_lists()
                self.spawnSys.curNumEnemies -= 1
                print("laser" + str(self.spawnSys.curNumEnemies))

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
