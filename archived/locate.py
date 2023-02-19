# packages
import sys
import time
import cv2
import numpy as np
import pyautogui as pg
from pygetwindow import getWindowsWithTitle
import os
# baseline confidence for object detection's
# terroHP.png, [terroHP.png, confidence=0.5]
# [nightsHP2.png, confidence=0.44] [nightBeast.png, confidence=0.54]
imgDirPath = 'D:\\2021code\\NumpyAnimation\\images\\'
def _walk_Img_Dir(path):
    # walk the image directory and return a list of images
    imgList = []
    for root, dirs, files in os.walk(path):
        for file in files:
            imgList.append(file)
    print(imgList)
    return imgList


def drawBox(img, left, top, w, h, region, color=(0, 0, 255), thickness=2, label='None'):
    # draw a bounding box on the image
    if left > region[0]:
        left -= region[0]
    else:
        left = left % region[0]

    if top > region[1]:
        top -= region[1]
    else:
        top = top % region[1]
        
    cv2.rectangle(
        img,
        (left, top),
        (left + (w % region[2]), top + (h % region[3])),
        color,
        thickness
    )
    cv2.putText(img, label, (left, top-5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def saveImgTemp(img):
    """capture the numpy array with boxes drawn and format to uint8

    Args:
        img (Mat): numpy array of the image with boxes drawn on it

    Returns:
        Mat: numpy array of the image with boxes drawn on it in uint8 format
    """
    return img.astype('uint8')
    # cv2.imwrite(imgDirPath+'temp.bmp', img)
    


def getGameWindow():
    """find the game window, this wll be the screen shot region.

    Returns:
        list: [left, top, width, height] of the game window
    """
    # find the game window, this wll be the screen shot region.
    gameWindow = getWindowsWithTitle('Simplicity+')[0]
    return [gameWindow.left, gameWindow.top, gameWindow.width, gameWindow.height]


def delOldImg(*imgs):
    # delete the old image
    for img in imgs:
        del img


def _check_Img_name(imageList,*imgNames):
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


def locate_init():
    imgList = _walk_Img_Dir(imgDirPath)
    
    olvPotPath = imgDirPath+'overloadPotion.png'
    # get image names to use for object detection
    imgName = input("Enter image name for npc: ")
    imgNameHP = input("Enter image name for npc health: ")
    confidenceInput = input("Enter 2 confidence values comma separated (0.00, 0.00): ")
    npcConfidence, hpConfidence = confidenceInput.split(',')
    # validate the image names
    if _check_Img_name(imgList, imgName, imgNameHP):
        npcPath = imgDirPath+imgName
        hpPath = imgDirPath+imgNameHP
    else:
        sys.exit()
    return npcPath, hpPath, olvPotPath, imgName, imgNameHP , float(npcConfidence), float(hpConfidence)

def findAllAndClick(detection,*args):
    frame, gameWindowReg, imgName = args
    lastFound = []
    for found in detection:
        # print('found npc!')
        drawBox(frame, found.left, found.top, found.width,
                found.height, gameWindowReg, label=imgName)
        lastFound.append(found)
    #
        # saveImgTemp(frame)
    if lastFound:
        click = pg.center((lastFound[0].left, lastFound[0].top, lastFound[0].width,
                lastFound[0].height))
        pg.moveTo(click, duration=0.45)
        pg.click(click)
            
            # del locals for next loop
        del click
    return 'found ' + imgName

def findAllAndDraw(detection,*args):
    frame, gameWindowReg, imgName = args
    
    for found in detection:
        # print('found npc!')
        drawBox(frame, found.left, found.top, found.width,
                found.height, gameWindowReg, label=imgName)
    return 'found ' + imgName

def main_UI(npcPath, hpPath, olvPotPath, imgName, imgNameHP, *args):
    msg = 'default'
    gameWindowReg = getGameWindow()
    npcConfidence, hpConfidence, runTime, startTime, lastClickTime = args
    
    #
    hp = pg.locateOnScreen(hpPath, confidence=hpConfidence, region=gameWindowReg, grayscale=True)
    #
    # take screenshot of game window, this is the frame we will draw on
    npc = np.ndarray((2,2))
    screenshot = pg.screenshot(region=gameWindowReg,)
    screenshot = np.array(screenshot)
    # frame = saveImgTemp(screenshot)
    # clickTime = (lastClickTime - startTime)
    clickTime = lastClickTime
    debounce = runTime - lastClickTime
    print(f'click: {clickTime} \nrunTime: {runTime} \n')
    
    if (hp is None):
    # draw rectangle around the object & click it.
        if debounce > 1.5:
            print(f'debounce: {debounce}')
            npc = pg.locateOnScreen(npcPath, confidence=npcConfidence, region=gameWindowReg, grayscale=True)
            if npc:
                clickTime = time.time() - startTime
                drawBox(screenshot, npc.left, npc.top, npc.width, npc.height, gameWindowReg, color=(0, 255, 0), label=imgName)
                click = pg.center((npc.left, npc.top, npc.width,
                npc.height))
                pg.moveTo(click, duration=0.25)
                pg.click(click)
        else:
            print(f'debounce: failed')
    else:
            # take a screenshot to store locally later
        msg = 'hp in window, displaying bot view...'
        
        # 
        # draw rectangle around the object, normalize coordinates to game window.
        # achieved by bounding box as if game window is the whole screen
        drawBox(screenshot, hp.left, hp.top, hp.width, hp.height, gameWindowReg,
                color=(0, 255, 0), label=imgNameHP)
        # if we have npc in window, find and click
        # msg = findAllAndDraw(npc, screenshot, gameWindowReg, imgName)
        npc = pg.locateOnScreen(npcPath, confidence=npcConfidence, region=gameWindowReg, grayscale=True)
        if npc:
            drawBox(screenshot, npc.left, npc.top, npc.width, npc.height, gameWindowReg, color=(0, 255, 0), label=imgName)
    
    if int(runTime)%400 >= 398:
        print('checking for potion...')
            
        ovlPotion = pg.locateOnScreen(
            olvPotPath, confidence=0.65, region=gameWindowReg, grayscale=True)
        if ovlPotion is not None:
            # print('found overload potion!')

            drawBox(screenshot,
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
            msg = 'found overload potion! using it'
            
    else:
        msg = 'found hp, waiting...'
        
    frame = saveImgTemp(screenshot)
    # del locals for next loop
    delOldImg(screenshot, gameWindowReg, hp, npc, screenshot)
    return msg, frame, clickTime

if __name__ == '__main__':
    # give the usage if run as main
    print(f'{__name__} RUN as __main__, this module is not meant to be run directly' + 
          f'\nhandles-: "{imgDirPath}" resources for openCV!!!')
