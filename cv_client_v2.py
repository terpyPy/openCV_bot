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
from tile import Tile, txt_curser
from ImageRec.locateClass import Locate
import pygame
import pygame.display
import pygame.event
import pygame.mouse
from gameSettings import Settings
from PySimpleGUI import popup_get_text


# openCV bot vision client
class botVisual:
    def __init__(self) -> None:
        # init game and create screen game resource
        self.npcVal = 0.5
        self.degree = int
        self.frame = None
        self.startTime = time.time()
        self.runTime = self.startTime
        pygame.init()
        pygame.display.set_caption("Visualizer - TerpyPy")
        # n for number of ui elements
        self.n = 4
        # collect settings from gameSettings.py
        self.settings = Settings(self.n, (820, 625))
        self.screen = pygame.display.set_mode((self.settings.screen_width,
                                               self.settings.screen_height))
        self.framePath = self.settings.get_temp_path()
        self.screen_rect = self.screen.get_rect()

        # fill the screen with the background color & set the clock
        self.screen.fill(self.settings.bg_color)
        self.clock = pygame.time.Clock()

        # load the init frame by creating a new tile object
        self._init_client('temp.bmp')


    def _init_client(self, img) -> None:
        """create a new tile object and load the image, making the video feed window & window console line.

        Args:
            img (str): the name of the image to load, path is handled by the tile class
        """
        # TODO: this is trash spaghetti code, I need to make a class for the ui elements and locations.
        self.screenShot = Tile(self.screen, self.screen_rect,
                               (0, 0), self.settings, img=img)
        self.screenShot.set_font_size(15)
        self.screenShot.rect_in.y = 0
        self.screenShot.y_txt = 575
        #
        self.cmd_line = txt_curser()
        #
        self.screenShot.blitme_pixel_array()
        self.screen.blit(self.cmd_line.get_surface(),
                         self.cmd_line.get_home_pos())
        pygame.display.flip()
        #
        self.DisplayTime = (410, 575)
        self.botTime = (610, 575)
        self.displayKills = (610, 550)
        self.displayNpcName = (410, 550)
        ele_cords = [self.DisplayTime, self.botTime,
                     self.displayKills, self.displayNpcName]
        self.UI_group = self.makeTiles(ele_cords)
        # get user choice for preset or trial number
        self.presetText = popup_get_text(
            'Enter npc name (cancel to specify respurces): ')
        if self.presetText == 'pos':
            getTrialNum = popup_get_text('Enter trial number: ')
            self.bot = Locate(self.startTime, combat=False,
                              trialNum=int(getTrialNum))
        else:
            self.bot = Locate(self.startTime, preset=self.presetText)
    
    def makeTiles(self, cord_arr, fontSize=12) -> list:
        """create a new tile object

        Args:
            numToMake (int): the number of tiles to make
            cord_arr (list): the list of cords to place the tiles
            fontSize (int, optional): the font size of the text. Defaults to 12.

        Returns:
            Entity list: a list of tile objects
        """
        UI_eles: list[Tile] = [0]*len(cord_arr)
        for i in range(len(cord_arr)):
            UI_eles[i] = Tile(self.screen, self.screen_rect,
                              (i+1, 0), self.settings)
            UI_eles[i].set_font_size(fontSize)
            UI_eles[i].set_cords_txt(cord_arr[i][0], cord_arr[i][1])

        return UI_eles

    def draw(self) -> None:
        """draw the screen and update the display"""
        self.screen.fill(self.settings.bg_color)
        #
        dtime = round(self.runTime, 3)
        btime = round(self.bot.debounceClick, 3)
        #
        DisplayMsg = 'runtime: ' + str(dtime)
        botTimeMsg = 'debouncing timer: ' + str(btime)
        displayKillsMsg = 'kills: ' + str(self.bot.kills)
        displayNpcNameMsg = 'npc: ' + str(self.bot.imgName)
        msgLst = [DisplayMsg, botTimeMsg, displayKillsMsg, displayNpcNameMsg]
        #
        for i, msg in enumerate(msgLst):
            tile: Tile = self.UI_group[i]
            tile.set_msg(msg)
            tile.blitme_pixel_array()

        self.screen.blit(self.cmd_line.get_surface(),
                            self.cmd_line.get_home_pos())
        self.screenShot.blitme_pixel_array()

        pygame.display.flip()

    def event_loop(self, eventKey,events) -> None:
        k = self.settings

        if eventKey == pygame.K_q:
            # self.bot.resourceFrame.to_csv('pos_files_test_3.csv')
            self.saveStats()
            pygame.quit()
            sys.exit()

        elif eventKey == pygame.K_p:
            self.msg =  "Enter npc search confidence: "
            self.cmd_line.textinput.value = ''
            k.isPause = not k.isPause
            events.clear()
            
        elif eventKey == pygame.K_s and k.isPause==False:
            # self.degree = int(input("rotation degree: "))
            save = popup_get_text("save stats? (y/n): ", default_text='y')
            if save.lower() == 'y':
                self.saveStats()
        elif eventKey == pygame.K_RETURN and k.isPause:
            
            self.npcVal = float(self.cmd_line.textinput.value)
            self.cmd_line.textinput.value = ''
            k.isPause = not k.isPause
            events.clear()

    def saveStats(self):
        """save the stats of the run to a file"""
        name = self.bot.imgName.replace('.png', '')
        with open('taskStats.txt', 'a') as f:
            # write the npc name, kills, and tokens time to the file
            f.write(f'npc: {name}  task time:{round(self.runTime,3)}\r\n')
        f.close()

    def main(self) -> None:
        # get the init for the bot to run
        self.msg = 'default'
        if not self.presetText == 'pos':
            self.npcVal, self.healthVal = self.bot.getConfidence()
        self.clickTime = 0.2
        while True:
            # check for events on keyboard
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    self.event_loop(event.key,events)
            if self.settings.isPause:
                self.cmd_line.textinput.update(events)
            # soo is runtime in seconds
            else:
                self.runTime = (time.time() - self.startTime)

                # get the frame from the bot, use the preset text to determine if the bot is in combat mode or not
                if self.presetText == 'pos':
                    self.bot.pos_UI(self)
                elif self.presetText != 'pos':
                    self.bot.main_UI_combat(self)

            self.screenShot.set_msg(self.msg)

            self.screenShot.usePixelArr(self.frame)
            self.draw()

        # self.clock.tick(25)


if __name__ == '__main__':
    # create a new botVisual object and run the main loop
    x = botVisual()
    x.main()
    print('done')
    # end of bot visualizer program.
