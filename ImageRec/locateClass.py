# packages
from os import getcwd, walk
import sys
import time
from random import randint
import cv2
import pytesseract
import numpy as np
import pandas as pd
import pyautogui as pg
from pygetwindow import getWindowsWithTitle

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class Locate:
    def __init__(self, startTime, preset=None, combat=True, trialNum=1) -> None:
        self.kills = 0
        self.tokensThisRun = 0
        self.imgDirPath = getcwd() + '\\images\\'
        self.imgList = self._walk_Img_Dir(self.imgDirPath)
        self.startTime = startTime
        self.imgName = '%'
        if combat:
            self._combat_init(preset)
        else:
            self.dayPointer = f'day{trialNum}'
            self._find_init()

    def _find_init(self):
        # load the images used for item detection for pos monitor bot
        self.resourceFrame = pd.read_csv('pos_files.csv')
        self.resources = self.resourceFrame['pos_img'].apply(
            lambda x: self.imgDirPath + x).to_numpy()
        self.boxLabels = ['item found', 'price found']

    def _combat_init(self, preset):
        # load the images used for item detection in combat
        self.resourceFrame = pd.read_csv('item_files.csv')
        # format the data frame with the image directory path and convert to numpy array
        resources = self.resourceFrame['resource_img'].apply(
            lambda x: self.imgDirPath + x).to_numpy()
        # currently bound to 4 items/hp images we are looking for
        self.olvPotPath, self.specialAttackPath, self.myHPPath, self.healItemPath = resources[
            0:4]

        self.inKill = False
        self.npc = None

        if preset == None:
            self.imgName = input("Enter image name for npc: ")
            self.imgNameHP = input("Enter image name for npc health: ")
            self.confidenceInput = input(
                "Enter 2 confidence values comma separated (0.00, 0.00): ")
            self.npcConfidence, self.hpConfidence = np.array(
                self.confidenceInput.split(',')).astype(float)
        else:
            self.presetList = pd.read_csv('presets.csv')
            preset = self.presetList.loc[self.presetList['name'] == preset]
            # check if preset exists
            if preset.empty:
                exit('Preset not found')
            # get the row from the preset list with the name
            self.imgName, self.imgNameHP, self.npcConfidence, self.hpConfidence = preset.iloc[0, 1:5].to_numpy(
            )

        # validate the image names
        if self._check_Img_name(self.imgList, self.imgName, self.imgNameHP):
            self.npcPath = self.imgDirPath+self.imgName
            self.hpPath = self.imgDirPath+self.imgNameHP
        else:
            sys.exit()

    def getConfidence(self):
        return float(self.npcConfidence), float(self.hpConfidence)

    def _walk_Img_Dir(self, path):
        # walk the image directory and return a list of images
        imgList = []
        # probably a better way to do this, using os like this is unsafe.
        for root, dirs, files in walk(path):
            for file in files:
                imgList.append(file)
        print(imgList)
        return imgList

    def _check_Img_name(self, imageList, *imgNames):
        """from a list of images found in the image directory, check if the image(s)
        exists in the list. returns true if all images are found, false if not.

        Args:
            imageList (list): list of images found in the image directory
            *imgNames (str| iterable[str]): image name(s) to check

        Returns:
            bool: True if all images are found, false if not.
        """
        # check the image name
        #
        for imgName in imgNames:
            if imgName not in imageList:
                print(f'Image {imgName} not found')
                return False
            else:
                print(f'Image {imgName} found')
                continue
        return True

    def drawBox(self, img, left, top, w, h, region, color=(0, 0, 255), thickness=2, label='None'):
        """draw a box on the image, this is used to show the location of the object
        found in the image. uses full screen coordinates inputs, and converts to
        image coordinates. returns nothing, image is modified in place.

        Args:
            img (Mat): the image to draw the box on
            left (float): cord representing the y cord of the top left corner of the box
            top (float): cord representing the x cord of the top left corner of the box
            w (int): width of box to draw
            h (int): height of box to draw
            region (iterable): iterable of floats for target window, [left, top, width, height]
            color (tuple, optional): box line color. Defaults to (0, 0, 255).
            thickness (int, optional):box line thickness. Defaults to 2.
            label (str, optional): text to display above box. Defaults to 'None'.
        """
        # transform the cords to image coordinates thats start at 0,0 for top left of image
        # draw a bounding box on the image
        if left > region[0]:
            left -= region[0]
        else:
            left = left % region[0]

        if top > region[1]:
            top -= region[1]
        else:
            top = top % region[1]
        # not the top left of the screen
        cv2.rectangle(
            img,
            (left, top),
            (left + (w % region[2]), top + (h % region[3])),
            color,
            thickness
        )
        cv2.putText(img, label, (left, top-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    def saveImgTemp(self, img):
        """capture the numpy array with boxes drawn and format to uint8.
        this is in memory and not saved to disk. returns the Mat object suitable
        to be displayed in a pygame window.

        Args:
            img (Mat): numpy array of the image with boxes drawn on it

        Returns:
            Mat: numpy array of the image with boxes drawn on it in uint8 format
        """
        return img.astype('uint8')
        # cv2.imwrite(imgDirPath+'temp.bmp', img)

    def getGameWindow(self):
        """find the game window, this wll be the screen shot region.

        Returns:
            list: [left, top, width, height] of the game window
        """
        # find the game window, this wll be the screen shot region.
        gameWindow = getWindowsWithTitle('Simplicity+')[0]
        return [gameWindow.left, gameWindow.top, gameWindow.width, gameWindow.height]

    def delOldImg(self, *imgs):
        # delete the old image
        for img in imgs:
            del img

    def getCurrentTime(self):
        # get the current time
        return time.time() - self.startTime

    def setLastLocation(self, location):
        self.lastLocation = location

    def drawLastDetect(self, screenshot, gameWindowReg):
        self.drawBox(screenshot,
                     self.lastLocation[0],
                     self.lastLocation[1],
                     self.lastLocation[2],
                     self.lastLocation[3],
                     gameWindowReg,
                     color=(50, 255, 0),
                     label='showing last location')

    def drawInBattle(self, screenshot, gameWindowReg, hp):
        if self.inKill:
            self.kills += 1
            self.tokensThisRun += randint(15, 50)
            self.inKill = False

        #
        # draw rectangle around the object, normalize coordinates to game window.
        # achieved by bounding box as if game window is the whole screen
        self.drawBox(screenshot, hp.left, hp.top, hp.width, hp.height, gameWindowReg,
                     color=(0, 255, 0), label=self.imgNameHP)
        # if we have npc in window, find and click
        # msg = findAllAndDraw(npc, screenshot, gameWindowReg, imgName)
        self.debounceFrame = self.runTime - self.botTime
        if self.debounceFrame > 0.3:
            # print(f'debounce: {self.debounce}')
            self.npc = pg.locateOnScreen(
                self.npcPath, confidence=self.npcConfidence, region=gameWindowReg, grayscale=True)
            self.botTime = self.getCurrentTime()
            if self.npc:
                self.setLastLocation(
                    [self.npc.left, self.npc.top, self.npc.width, self.npc.height])
                self.drawLastDetect(screenshot, gameWindowReg)
            else:
                self.drawLastDetect(screenshot, gameWindowReg)
        else:
            self.drawLastDetect(screenshot, gameWindowReg)

    def pos_UI(self, state,debug=False):
        # unpack the state of the bot from ui loop
        # TODO: to thread this, we need to pass the state as a queue, or decouple the ui from the bot resources
        self.msg = state.msg
        gameWindowReg = self.getGameWindow()
        self.runTime = state.runTime
        self.botTime = state.clickTime
        self.debounceClick = self.runTime - self.botTime
        #
        # this is actually the confidence for price loc in this case
        self.npcConfidence = state.npcVal
        # take screenshot of game window, this is the frame we will draw on
        screenshot = pg.screenshot(region=gameWindowReg,)
        # convert to numpy array for opencv and pytesseract post processing
        screenshot = np.array(screenshot)
        # get the item unit image
        price_in_bills = self.resources[-1]
        # init an array to hold the found items boxes called item, of size len(self.resources)
        foundItem = [list()] * (self.resources.shape[0] - 1)
        # locate and draw boxes for all images in self.resources using enumerate to get index
        
        for i, img in enumerate(self.resources[:-1]):
            # find the item in the screenshot add to foundItem array
            foundItem[i] = pg.locateOnScreen(
                img, confidence=0.625, region=gameWindowReg, grayscale=False)
        # for any item found, draw a box around it and its price
        for i, item in enumerate(foundItem):
            if item:
                # find the price of the item
                price = pg.locateOnScreen(price_in_bills,
                                        confidence=self.npcConfidence,
                                        region=foundItem[i],
                                        grayscale=False)
                # draw the box around the item
                itemId = self.resources[i].split('\\')[-1]
                self.drawBox(screenshot, item.left, item.top, item.width, item.height, gameWindowReg,
                            color=(0, 255, 0), label=itemId)
                state.frame = self.saveImgTemp(screenshot)
                # draw the box around the price
                if price:
                    # read the price from the image
                    pad = 52
                    priceImg = pg.screenshot(region=(
                        price.left,
                        price.top-6,
                        price.width-pad,
                        price.height+10))

                    # process the image to make it easier to read
                    # convert to numpy array for opencv and pytesseract post processing, like screenshot
                    priceImg = np.array(priceImg)
                    # priceImg = cv2.cvtColor(priceImg, cv2.COLOR_BGR2GRAY)
                    # enlarge the image to make it easier to read
                    priceImg = cv2.resize(
                        priceImg, (80,80), fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    # cv2.imshow('price', priceImg)
                    priceText = pytesseract.image_to_string(
                        priceImg).replace('\n', '')[:-1]
                    
                    df = self.resourceFrame
                    # init a list of conditions to check if the price is found for the first time for this item each day
                    conditions = [df.loc[i, self.dayPointer] == 0,
                                df.loc[i, 'pos_img'] == itemId,
                                priceText != '']
                    # add the price to resources dataframe such that day 1 price is updated once per item found, on the corresponding row
                    if conditions.count(True) == len(conditions):
                        df.loc[i, self.dayPointer] = priceText
                    state.msg = priceText
                    self.drawBox(screenshot,
                                price.left,
                                price.top-6,
                                price.width-pad,
                                price.height+10,
                                gameWindowReg,
                                color=(0, 200, 55), 
                                label='price found')
                    state.frame = self.saveImgTemp(screenshot)
            else:    
                state.frame = self.saveImgTemp(screenshot) 
                # print(priceText)
            
            # save current frame as np array

    def main_UI_combat(self, state):
        self.msg = state.msg
        gameWindowReg = self.getGameWindow()
        self.npcConfidence = state.npcVal
        self.hpConfidence = state.healthVal
        self.runTime = state.runTime
        self.botTime = state.clickTime

        #
        hp = pg.locateOnScreen(self.hpPath,
                               confidence=self.hpConfidence,
                               region=gameWindowReg,
                               grayscale=True)
        #
        # take screenshot of game window, this is the frame we will draw on
        screenshot = pg.screenshot(region=gameWindowReg,)
        screenshot = np.array(screenshot)

        self.debounceClick = self.runTime - self.botTime
        state.msg = 'searching for npc'

        if (hp is None):
            # draw rectangle around the object & click it.
            if self.debounceClick > 2.75:

                self.npc = pg.locateOnScreen(self.npcPath,
                                             confidence=self.npcConfidence,
                                             region=gameWindowReg,
                                             grayscale=True)
                if self.npc:

                    click = pg.center((self.npc.left, self.npc.top, self.npc.width,
                                       self.npc.height))
                    pg.moveTo(click, duration=0.15)
                    pg.click(click)
                    self.inKill = True
                    self.setLastLocation(
                        [self.npc.left, self.npc.top, self.npc.width, self.npc.height])

                    state.clickTime = self.getCurrentTime()
                    self.drawBox(screenshot,
                                 self.npc.left,
                                 self.npc.top,
                                 self.npc.width,
                                 self.npc.height,
                                 gameWindowReg,
                                 color=(0, 255, 0),
                                 label=self.imgName)
                    state.msg = 'clicking npc'
            else:
                state.msg = 'debounce: failed'

        elif hp:
            # take a screenshot to store locally later
            state.msg = 'hp in window, displaying bot view...'
            self.drawInBattle(screenshot, gameWindowReg, hp)

        if int(self.runTime) % 63 >= 62:
            print('checking for potion...')

            ovlPotion = pg.locateOnScreen(
                self.olvPotPath, confidence=0.65, region=gameWindowReg, grayscale=True)
            if ovlPotion is not None:
                # print('found overload potion!')

                self.drawBox(screenshot,
                             ovlPotion.left,
                             ovlPotion.top, ovlPotion.width,
                             ovlPotion.height,
                             gameWindowReg,
                             color=(100, 255, 0),
                             label='overload potion')

                x = pg.center((ovlPotion.left, ovlPotion.top,
                               ovlPotion.width, ovlPotion.height))
                pg.moveTo(x, duration=0.1)
                pg.click(x)
                del x
                state.msg = 'found overload potion! using it'

        if float(self.runTime) % 37 >= 35.3:
            specialAttack = pg.locateOnScreen(
                self.specialAttackPath, confidence=0.65, region=gameWindowReg)
            if specialAttack is not None:
                # print('found special attack!')

                self.drawBox(screenshot,
                             specialAttack.left,
                             specialAttack.top, specialAttack.width,
                             specialAttack.height,
                             gameWindowReg,
                             color=(100, 255, 0),
                             label='special attack')

                x = pg.center((specialAttack.left, specialAttack.top,
                               specialAttack.width, specialAttack.height))
                pg.moveTo(x, duration=0.1)
                pg.click(x)
                del x
                state.msg = 'found special attack! using it'

        if float(self.runTime) % 12 >= 8.5:

            if pg.locateOnScreen(self.myHPPath, confidence=0.763, region=gameWindowReg) is not None:

                heal = pg.locateOnScreen(
                    self.healItemPath, confidence=0.62, region=gameWindowReg)
                if heal is not None:
                    # print('found heal!')

                    self.drawBox(screenshot,
                                 heal.left,
                                 heal.top, heal.width,
                                 heal.height,
                                 gameWindowReg,
                                 color=(100, 255, 0),
                                 label='heal')

                    x = pg.center((heal.left, heal.top,
                                   heal.width, heal.height))
                    pg.moveTo(x, duration=0.12)
                    pg.click(x)
                    del x
                    state.msg = 'found heal! using it'
                else:
                    state.msg = 'no heal found'

        state.frame = self.saveImgTemp(screenshot)
        # del locals for next loop
        # self.delOldImg(screenshot, gameWindowReg, hp, screenshot)
        # return self.msg, frame, self.botTime


if __name__ == '__main__':
    # give the usage if run as main
    print(f'{__name__} RUN as __main__, this module is not meant to be run directly' +
          f'\nhandles-: "IMAGE" resources for openCV!!!')
