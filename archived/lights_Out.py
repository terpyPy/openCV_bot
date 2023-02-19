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
#  Description: pygame version of Conway's Game of Life and a puzzle game the uses
#               the neighbor adjacency rule to invert the colors of the tiles,
#               with the goal to turn off all tiles. finally a drawing on the board option,
#               to set custom starting board states.
#
import os
import time
from archived.boardStateDriver import boardState
from gameSettings import Settings
from deBugTiles import tileWindow
import sys
import pygame
import pygame.display
import pygame.event
import pygame.mouse
from tile import txt_curser
import pygame_textinput


class LightsOutGame:
    # over all class to manage the game
    def __init__(self, N: int) -> object:
        # init game and create screen game resource
        pygame.init()
        self.isDebugActivity = False
        # N is either NxN grid or *args is a list of modifiers
        self.N = N
        self.newLine = None
        # init the UI, N is passed to size the list comprehension,
        # was written to allow rebuilding the game in any NxN grid
        self.create_board_UI()
        #
        self.menuKeys = self.settings.menuKeys
        self.pauseKeys = self.settings.pauseKeys
        self.option = 'new_rules'
        # init the UI, N is passed to size the list comprehension,
        # was written to allow rebuilding the game in any NxN grid
        # self.create_board_UI()
        # this library makes having user type box easy, not good
        resourcPath = os.path.join(
            os.environ.get("_MEIPASS2", os.path.abspath(".")), 'images\\freesansbold.ttf')
        self.textinput = pygame_textinput.TextInputVisualizer(
            font_object=pygame.font.Font(resourcPath, 20))
        
        # set the clock for pygame this will be used to synchronize
        # the game with the framerate of the display
        self.clock = pygame.time.Clock()

    def create_board_UI(self, *args):
        # this makes bsdrive
        """TODO: make all this functions dependent on this function take *args 
        this allows for proper board size creation in window & on the fly reshaping."""
        # make screen surface
        self.screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("lights out")
        self.settings = Settings(
            self.N,
            screen=(self.screen.get_rect(
            ).center[0], self.screen.get_rect().center[1]),
            isGlobal=True)
        
        # init the grid drawn over each tile
        self.board = txt_curser(self)
        print(self.board.tileArray[0][0].get_img_size())
        option1_cords = (self.N+5, self.N//2)
        option2_cords = (self.N//2, self.N+5)
        self.new_rules_button = self.board.make_Tile(option1_cords)
        self.FPS_option_button = self.board.make_Tile(option2_cords)
        
        # passing self gives the Tile obj a current instance of the state
        self.driver = boardState(self)

        x, y, img_size = self.board.getTextXY()
        self.texWincord1 = x-(img_size)
        self.texWincord2 = y+img_size

    def windPrompt(self):
        '''should use the logic applied in this function 
        to enter custom & random board sizes and shapes'''
        if self.textinput.value.isdigit():
            self.N = int(self.textinput.value)
            del self.board
            del self.driver
            del self.new_rules_button
            # self.driver.resetDriver()
            self.create_board_UI()
        self.textinput.value = ''
        self.driver.mode = 'start'


    def _check_events(self):
        events = pygame.event.get()
        # wiki for this module said this is the way soo, give the text box ALL the events?
        # no way thats a good idea long term.
        if pygame.MOUSEBUTTONDOWN or pygame.KEYDOWN in events:
            self.textinput.update(events)
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #
                    x, y = event.pos
                    # soo im just lazy and this works fine, for future,
                    # just compare the len(lst-1) before returning it, try returning -1,-1 on error
                    # try:
                    i, j = self._get_button_click(x, y)
                    if i != None:
                        self.driver.boardLogic((i, j))

                elif event.type == pygame.KEYDOWN:
                    # if key is pressed check its mapping to its options,
                    self._menu_Keys(event.key)

    def _get_button_click(self, x, y):
        tile_view = self.board.tileArray
        # check if a menu button was clicked
        if self.new_rules_button.rect_in.collidepoint(x, y):
            self.option = 'new_rules'
            return (None, None)
        elif self.FPS_option_button.rect_in.collidepoint(x, y):
            self.option = 'fps_option'
            return (None, None)
        # check the board click.
        for i in range(self.N):
            for j in range(self.N):
                # find the location that the click was on a valid tile
                if tile_view[i][j].rect.collidepoint(x, y):
                    print(x, y, (i, j))
                    # return the correct tile location in the array
                    return (i, j)
                elif tile_view[i][(i+j) % self.N].rect.collidepoint(x, y):
                    print(r'came from (i+j)%self.N', x, y, (i, (i+j) % self.N))
                    # return the correct tile location in the array
                    return (i, (i+j) % self.N)
                elif tile_view[j][i].rect.collidepoint(x, y):
                    print('came from j i', x, y, (j, i))
                    # return the correct tile location in the array
                    return (j, i)
                elif tile_view[j][j].rect.collidepoint(x, y):
                    print('came from j j', x, y, (j, j))
                    # return the correct tile location in the array
                    return (j, j)
        return (None, None)

    def _menu_Keys(self, eventKey: int):
        # check if a key is pressed and change the mode accordingly
        #
        # q to quit while running
        if eventKey == pygame.K_q:
            sys.exit()
            
        # check menu keys.
        elif eventKey in self.menuKeys.keys():
            self.driver.mode = self.menuKeySwitcher(eventKey, self.driver.mode)
            if self.driver.mode != 'nGame':
                self.driver.clearBoard()
                # clear the cursor box for user input, cannot be done in draw function
                self.textinput.value = ''
                print(self.driver.mode)
                # return
        
        # control start screen ui events here.
        if self.driver.mode == 'start':
            # if key press return build new UI of its size.
            if eventKey == pygame.K_RETURN:
                self.windPrompt()
                return

        # toggle's that can be read while running the game
        elif self.driver.mode in ['run', 'nGame', 'draw']:
            # if the game is running, then the board state can be frozen
            if eventKey in self.pauseKeys.keys():
                self.driver.isPause = self.pauseFunc(eventKey)
                return
            # toggle colors on and off
            elif eventKey == pygame.K_c:
                self.driver.isMulticolor = self.toggleColors()
                print(
                    f'Debug_option-is-Multicolor_:-{self.driver.isMulticolor}')
                # return
            # toggle debug mode on and off
            elif eventKey == pygame.K_d:
                self.isDebugActivity = not self.isDebugActivity
                print(f'Debug_option-node-ACTIVITY_:-{self.isDebugActivity}')
                # return

    def menuKeySwitcher(self, event, mode):
        # take the event key and return the correct menu option
        menuOption = self.menuKeys.get(event)
        if menuOption:
            return menuOption
        else:
            return mode

    def toggleColors(self):
        #
        # clear the cursor box for user input, cannot be done in draw function
        self.textinput.value = ''
        if self.driver.isMulticolor:
            return False
        else:
            return True

    def pauseFunc(self, event):
        # clear the cursor box for user input, cannot be done in draw function
        pausePrompt = 'PAUSED:-- Change Rule\'s: 3 integers > 9.'
        if event == pygame.K_a:
            self.new_rules_button.set_msg(pausePrompt)
            self.FPS_option_button.set_msg('fps setting(default:5)')
            
            self.textinput.value = ''
            print(f'paused_simulation-KEYPRESS_a: {not self.driver.isPause}')
            return not self.driver.isPause
       
        # functionality for changing conway's game rules from pause state
        elif event == pygame.K_RETURN:
            # unpack the flags used to change the rules, and unpause the game
            # bypass is -2 as the event as its not a plausible option from user 
            BYPASS_EVENT, OFF_PAUSE = self.pauseKeys.get(event)
            
            # try:
            if ','  in self.textinput.value and self.option == 'new_rules':
                rulesFromUser = self.textinput.value.split(',')
                print(f" current rule {self.driver.rules} changed to {rulesFromUser}")
                self.driver.boardLogic(BYPASS_EVENT, rulesFromUser)
                self.newLine = None
                print(f'paused_simulation-CHANGED_RULES: {OFF_PAUSE}')
                return OFF_PAUSE
            
            elif self.option == 'fps_option':
                self.settings.animation_FPS = int(self.textinput.value)
                print(f'paused_simulation-CHANGED_FPS: {OFF_PAUSE}')
                return OFF_PAUSE
            
            else:
                self.addedText = (f'invalid input: {self.textinput.value}')
                self.newLine = tileWindow(self, 
                                     self.addedText, 
                                     0, 
                                     0)
                
                
                self.textinput.value = ''
                print(f'paused_simulation-INVALID_INPUT: {not OFF_PAUSE}')
                return not OFF_PAUSE
    

    def _update_screen(self):
        # redraw screen surface ea loop
        self.screen.fill(self.settings.bg_color)
        for i in range(self.N):

            for j in range(self.N):
                # draw the tiles & grid on top of the screen as a group.
                self.board.drawTile(i, j)

        # draw text input if correct option,
        # this handles the text input for the user to change the grid size.
        if self.driver.getMode() == 'start':
            self.new_rules_button.blitme(True)
            self.new_rules_button.set_msg('enter NxN grid to make:')
            self.screen.blit(self.textinput.surface,
                             (self.new_rules_button.rect_in.x,
                              self.new_rules_button.rect_in.y)
                             )
            self.clock.tick(15)
        # handle the idle state of the game when paused.
        elif self.driver.isPause:
            self.new_rules_button.blitme(True)
            self.FPS_option_button.blitme(True)
            # draw the text input for the user to change the rules.
            if self.option == 'new_rules':
                cursorCords = (self.new_rules_button.rect_in.x,
                              self.new_rules_button.rect_in.y)
                self.screen.blit(self.textinput.surface,
                                cursorCords
                                )
            # draw the text input for the user to change the FPS.
            elif self.option == 'fps_option':
                cursorCords = (self.FPS_option_button.rect_in.x,
                              self.FPS_option_button.rect_in.y)
                self.screen.blit(self.textinput.surface,
                                cursorCords
                                )
            # draw the text input for invalid input from user.
            if self.newLine:
                self.newLine.x_txt = self.new_rules_button.rect_in.x
                self.newLine.y_txt = self.new_rules_button.rect_in.y+30
                self.newLine.blitme_txt(self.addedText)
               
            self.clock.tick(10)
        else:
            self.clock.tick(self.settings.animation_FPS)
        # TODO: add a new fps option for the pause menu. will require key press to switch cursor position to this option.
        # make most recent drawn screen appear
        pygame.display.flip()

    def run_game(self):
        # this is the event loop for the UI,
        # 1) chose the play type
        # 2) check the events, ie button press on keyboard and the window
        # 3) draw the result of listening to the event or driver logic execution
        while True:
            # 1
            if self.settings.mode == 'start':
                self.driver.boardLogic(-2)
            # 2
            self._check_events()
            # 3
            self._update_screen()
            # 4
            # if self.driver.isWin:
            #     time.sleep(1.2)
            #     self.driver.clearBoard()
            #     self.driver.isWin = False

if __name__ == '__main__':
    # create a new game instance
    startNum = input('NxN grid to make: ')
    state = LightsOutGame(int(startNum))
    state.run_game()
