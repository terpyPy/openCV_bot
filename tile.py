#!/usr/bin/python3
#  Version:     1.2 (Date: 6/24/2022)
#  Author:      Cameron Kerley (terpyPY: https://github.com/terpyPy/Interactive-Conways-game)
#  Date:        6 June 2022
#  License:     MIT License
#
#  description: This is the main file for what makes up the the full tile entity.
#               Manages the tile entity's and grid entity's as a group/collection in tileGroup class.
# ----------------------------------------------------------------------------------------------------------------------
#  Disclosure:  This code is public domain. You can use it in any way you want.
#               However, i am scanning github repos for this code that does not include credit to me.
#               I have left some patterns in the naming convention and access methods
#               in this project making copy/pasted stolen code easy to parse and find.
#
# in pygame the origin is (0,0) at the top lft of the screen.
# cords > 0 for col->right col,row
#   0___> +col and <= 1200
#   |
#   v +row and <= 800
import os
import pygame
import pygame.display
import pygame_textinput
from deBugTiles import tileWindow
from grid import Grid

class Tile(Grid, tileWindow):

    def __init__(self, screen: pygame.display, rect, cords, settings, noScale=True, noPad=True, img=None):
        """_summary_

        Args:
            screen (pygame.display): pygame surface to draw the obj.
            rect (pygame.rect): _description_
            cords (tuple): _description_
            settings (Settings): _description_
            noScale (bool, optional): _description_. Defaults to False.
            noPad (bool, optional): _description_. Defaults to False.
            img (str, optional): image to use for init. Defaults to None.
        """
        # init the tile and set its position
        Grid.__init__(self,screen, rect, cords, settings, noPad=noPad)
        if img is not None:
            resourcPath = os.path.join(
                os.environ.get("_MEIPASS2", os.path.abspath(".")), f'images\\{img}')
        else:
            resourcPath = os.path.join(
                os.environ.get("_MEIPASS2", os.path.abspath(".")), 'images\\tile.bmp')

        # init image sizes & padding inherited from from grid.
        if noScale is False:
            self.image = pygame.image.load(resourcPath)
            self.image = pygame.transform.scale(self.image,
                                                (int(self.scaleSize), int(self.scaleSize)))
        else:
            self.image = pygame.image.load(resourcPath)
        # get the image rect
        self.rect_in = self.image.get_rect()
        # set the tile's x position with the cords provided.
        self.setPad(cords)
        # this is default rgb color of the tile. it is white by default.
        self.Color = (250, 250, 250)
        # set node activity counter to .
        self.isEffected = 1
        
        tileWindow.__init__(self, screen, self.isEffected, self.rect_in.x, self.rect_in.y)
        # self.textWindow = tileWindow(
        #     self, self.isEffected, self.rect.x, self.rect.y)
        self.msg = 'default'
        
        if noScale:
            self.rect_in.y += 20
            self.rect_in.x += 2

    def get_color(self):
        return self.Color

    def set_color(self, color):
        self.Color = color

    def set_msg(self, msg):
        self.msg = msg
        self.set_font_size(int(self.fontSize))
    
    def set_text_cords(self, x, y):
        self.set_cords_txt(x, y)
        
    def change_img(self, img):
        # change the image of the tile from file.
        self.image = pygame.image.load(img)
        self.rect_in = self.image.get_rect()
        
    def usePixelArr(self, pixelArr, degree=90):
        # use the pixel array to change the image displayed on the tile. (read from memory NOT from file)
        self.image = pygame.surfarray.make_surface(pixelArr)
        self.image = pygame.transform.rotate(self.image, degree)
        self.image = pygame.transform.flip(self.image, False, True)
        
    def blitme_pixel_array(self):
        # draw the obj at its current location, used for pixel array representation of an image.
        self.screen.blit(self.image, (self.rect_in.x, self.rect_in.y))
        self.blitme_txt(self.msg)

class txt_curser:
    def __init__(self) -> None:
        resourcePath = os.path.join(
                            os.environ.get("_MEIPASS2", os.path.abspath(".")),'images\\freesansbold.ttf')
        self.font = pygame.font.Font(resourcePath, 11)
        self.textinput = pygame_textinput.TextInputVisualizer(font_object = self.font)
        self.cords = (2, 609)
    def get_surface(self):
        return self.textinput.surface
    
    def get_home_pos(self):
        return self.cords