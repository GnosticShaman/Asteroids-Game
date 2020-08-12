import arcade
import math
import random
import guiWindow
import launchWindow
from time import sleep
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from PodSixNet.Connection import connection

_width = 960
_height = 540
_frame = "Asteroids Server"
_offScreenBuffer = 50
shipSpeed = 10
angleSpeed = 5
laserSpeed = 15

# https://arcade.academy/resources.html#resources-images-space-shooter
possibleAsteroidType = [":resources:images/space_shooter/meteorGrey_big1.png",
                        ":resources:images/space_shooter/meteorGrey_big2.png",
                        ":resources:images/space_shooter/meteorGrey_big3.png",
                        ":resources:images/space_shooter/meteorGrey_big4.png"]

def encode_sprite(sprite):
    return (sprite.filename, sprite.scale, sprite.center_x, sprite.center_y, sprite.angle)

def decode_sprite(sprite_tuple):
    return arcade.Sprite(sprite_tuple[0], sprite_tuple[1], center_x=sprite_tuple[2], center_y=sprite_tuple[3], angle=sprite_tuple[4])

class Player(launchWindow.ship):
    def __init__(self, name):
        super().__init__("Assets/bluecarrier.png", .125)
        self.filename = "Assets/bluecarrier.png"
        self.scale = 0.125
        self.username = str(name)
        self.lives = 3
        self.score = 0
        self.center_x = _width // 2
        self.center_y = _height // 2

    def draw(self):
        super().draw()
        arcade.draw_text(self.username, self.center_x-25, self.center_y+30, arcade.color.WHITE, 14, width=200)

class asteroidsChannel(Channel):
    def Network_on_key_press(self, data):
        print("test")
        print(data)
        self._server.updateShip(data['name'], data['ship'][2], data['ship'][3], data['ship'][4])

    def Network_on_key_release(self, data):
        self._server.updateShip(data['name'], data['ship'][2], data['ship'][3], data['ship'][4])

    def Network_add_player(self, data):
        print("append ship")
        temp_player = Player(data['name'])
        temp_player.center_x = data['ship'][2]
        temp_player.center_y = data['ship'][3]
        temp_player.angle = data['ship'][4]
        self._server.playerList.append(temp_player)

    def Network_disconnected(self, data):
        self._server.DelPlayer(self)

    def Network_remove_player(self, data):
        self._server.RemoveSprite(data['name'])


class asteroidsServer(Server, arcade.View):
    channelClass = asteroidsChannel
    def __init__(self, host, port):
        arcade.View.__init__(self)
        arcade.set_background_color(arcade.csscolor.INDIGO)
        self.playerList = None
        self.laserList = None
        self.asetroidList = None
        self.channelList = []
        self.phyEngine = []
        self.fireSound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hitsound = arcade.load_sound(":resources:sounds/hit3.wav")
        self.asteroidCount = 6
        self.threshold = 3
        Server.__init__(self, localaddr=(host, port))

    def Connected(self, channel, addr):
        print("Player connected")
        self.AddPlayer(channel)

    def Disconnected(self, channel, addr):
        self.DelPlayer(channel)

    def AddPlayer(self, player):
        print("New Player" + str(player.addr))
        self.channelList.append(player)

    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        self.channelList.remove(player)

    def RemoveSprite(self, name):
        for i in self.playerList:
            if i.username == name:
                i.remove_from_sprite_lists()

    def SendToAll(self, data):
        [p.Send(data) for p in self.playerList]

    def addAsteroids(self, count):
        for i in range(0, count):
            asteroidSprite = launchWindow.asteroid(possibleAsteroidType[random.randrange(4)], .5)

            asteroidSprite.center_x = random.randrange(0, _height)
            asteroidSprite.center_y = random.randrange(0, _width)

            asteroidSprite.change_x = random.random() * 2
            asteroidSprite.change_y = random.random() * 2

            asteroidSprite.change_angle = math.radians(random.random())
            self.asteroidList.append(asteroidSprite)

    def setUp(self):
        self.playerList = arcade.SpriteList()
        # This is empty right now but when it's populated
        # the ship will crash into the asteroid Sprites
        self.asteroidList = arcade.SpriteList()
        self.laserList = arcade.SpriteList()
        self.powerupList = arcade.SpriteList()
        for x in range(4):
            powerupSprite = launchWindow.powerup("Assets/powerup.png", 1)
            powerupSprite.center_x = _width / (x + 1)
            powerupSprite.center_y = _width / (x + 1)
            self.powerupList.append(powerupSprite)

        self.laserList = arcade.SpriteList()

        self.addAsteroids(self.asteroidCount)

        # The second param makes it so that the first element pass through it
        # so for this we need to asteroids to overlap the ship so we have a
        # collision
        for i in self.playerList:
            self.phyEngine.append(arcade.PhysicsEngineSimple(i, arcade.SpriteList()))

    def on_update(self, delta_time):
        self.playerList.update()
        self.laserList.update()
        self.asteroidList.update()
        self.powerupList.update()
        if len(self.phyEngine) != 0:
            [i.update() for i in self.phyEngine]

        if len(self.asteroidList) <= self.threshold:
            # Don't know how we should make the game increasingly
            # more difficult, but this does just that
            self.threshold += 1
            self.asteroidCount += self.asteroidCount // 2
            self.addAsteroids(self.asteroidCount)

        for player in self.playerList:
            getPow = arcade.check_for_collision_with_list(player, self.powerupList)
            for hitPow in getPow:
                player.getPowerup(hitPow, 5)
                hitPow.remove_from_sprite_lists()

        for player in self.playerList:
            for rock in self.asteroidList:
                rockHits = arcade.check_for_collision_with_list(player, self.asteroidList)

                if len(rockHits) > 0:
                    if player.lives > 0:
                        rockHits[0].remove_from_sprite_lists()
                        player.lives -= 1

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
        ast_list = []
        las_list = []
        pwo_list = []
        for i in self.asteroidList.sprite_list:
            ast_list.append(encode_sprite(i))
        for i in self.laserList.sprite_list:
            las_list.append(encode_sprite(i))
        for i in self.powerupList.sprite_list:
            pwo_list.append(encode_sprite(i))
        for i in range(0, len(self.channelList)):
            self.channelList[i].Send({"action":"get_states", "asteroids":ast_list, "lasers":las_list, "powerups":pwo_list})
        self.Pump()

    def updateShip(self, name, x_val, y_val, angle):
        for i in self.playerList:
            if i.username == name:
                i.center_x = x_val
                i.center_y = y_val
                i.angle = angle

    def on_draw(self):
        arcade.start_render()
        [i.draw() for i in self.playerList]
        self.asteroidList.draw()
        self.powerupList.draw()
        self.laserList.draw()

if __name__ == "__main__":
    window = arcade.Window(_width, _height, _frame)
    idk = asteroidsServer("192.168.1.9", 2000)
    idk.setUp()
    window.show_view(idk)
    arcade.run()
