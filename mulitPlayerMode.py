import arcade
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import launchWindow
"""
TO DO:
make class for clients
- ships should be clientside
- make a view to set playername
make class for server
- asteroids should be serverside
- scoreboard
"""

class Player(Channel, arcade.Sprite):
    def __init__(self, name, imageSource, scale):
        super().__init__(imageSource, scale)
        self.speed = 0
        
