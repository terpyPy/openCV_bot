#!/usr/bin/python3
#
#  Author:      Cameron Kerley (terpyPY: https://github.com/terpyPy/Interactive-Conways-game)
#  Date:        6 June 2022
#  License:     MIT License
#
#  Disclosure:  This code is public domain. You can use it in any way you want.
#               However, i am scanning github repos for this code that does not include credit to me.
#               I have left some patterns in the naming convention and access methods
#               in this project making copy/pasted stolen code easy to parse and find.
#

import sys
import time
# from random import shuffle
from tile import Tile
import locate
# from grid import Grid
import pygame
import pygame.display
import pygame.event
import pygame.mouse
from gameSettings import Settings


# openCV bot vision client
class botVisual:
    def __init__(self) -> None:
        # init game and create screen game resource
        self.npcVal = float
        self.degree = int
        self.frame = None
        self.startTime = time.time()
        self.runTime = self.startTime
        pygame.init()
        pygame.display.set_caption("RSBot Visualizer - TerpyPy")
        # n for number of ui elements
        self.n = 4
        
        # this is our default window size
        screeWidth, screenHight = (820,590)
        self.screen = pygame.display.set_mode((screeWidth, screenHight))
        
        #collect settings from gameSettings.py
        self.settings = Settings(self.n,(screeWidth, screenHight))
        self.framePath = self.settings.get_temp_path()
        self.screen_rect = self.screen.get_rect()
        
        # fill the screen with the background color & set the clock
        self.screen.fill(self.settings.bg_color)
        self.clock = pygame.time.Clock()
        
        # load the init frame by creating a new tile object
        self.loadImg('temp.bmp')

        
    def loadImg(self, img) -> None:
        """create a new tile object and load the image, making the video feed window & window console line.

        Args:
            img (str): the name of the image to load, path is handled by the tile class
        """
        self.screenShot = Tile(self.screen, self.screen_rect, (0, 0), self.settings, noPad=True, img=img, noScale=True)
        self.screenShot.textWindow.set_font_size(15)
        self.screenShot.textWindow.y = 575
       
        
    def draw(self) -> None:
        """draw the screen and update the display"""
        self.screen.fill(self.settings.bg_color)
        self.screenShot.blitme_pixel_array()
        pygame.display.flip()
      
    def event_loop(self, eventKey) -> None:
        if eventKey == pygame.K_q:
            pygame.quit()
            sys.exit()
        elif eventKey == pygame.K_p:
            self.npcVal = float(input("Enter npc search confidence: "))
            
        elif eventKey == pygame.K_r:
            self.degree = int(input("rotation degree: "))
             
    def main(self) -> None:
        # get the init for the bot to run
        degree = 90
        npcPath, hpPath, olvPotPath, imgName, imgNameHP, self.npcVal, self.healthVal = locate.locate_init()
        clickTime = time.time() - self.runTime
        while True:
            # get the current frame from the bot
            self.runTime = (time.time() - self.startTime)# soo is runtime in seconds
            msg, self.frame, clickTime = locate.main_UI(npcPath, 
                                        hpPath,      
                                        olvPotPath, 
                                        imgName, 
                                        imgNameHP, 
                                        self.npcVal, 
                                        self.healthVal,
                                        self.runTime,
                                        self.startTime, 
                                        clickTime)
            
            self.screenShot.set_msg(msg)
            self.screenShot.usePixelArr(self.frame, degree=degree)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == pygame.KEYDOWN:
                    self.event_loop(event.key)
            
            self.draw()
            
        # self.clock.tick(25)
                      
if __name__ == '__main__':
    # create a new botVisual object and run the main loop
    x=botVisual()
    x.main()
    print('done')
    # end of bot visualizer program.
