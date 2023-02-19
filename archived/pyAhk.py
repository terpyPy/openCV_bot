import pyautogui as pg
from pygetwindow import getWindowsWithTitle
import numpy as np
import pandas as pd
import PySimpleGUI as sg


def main(choiceList, vals):
    returnPos = pg.position()
    gameRegion = getWindowsWithTitle('Simplicity+')[0]
    # get the target window
    pg.click(gameRegion.left, gameRegion.top)
    pg.moveTo(returnPos)
    for i in choiceList:
        if i in presets['preset'].to_numpy(str):
            txt = presets.loc[presets['preset'] == i]['text'].to_numpy()[0]
            pg.typewrite(txt)
            pg.press('enter')
            # return to option selected
        if i == 'search':
            choice = vals.pop(0)
            # find the best match for the search
            txt = presets.loc[presets['preset'].str.contains(choice)]['text'].to_numpy()[0]
            pg.typewrite(txt)
            pg.press('enter')
            break
        else:
            print('invalid preset')
            
def buttons_from_array(array):
    result = [[sg.Button(f'{i}')for i in array]]
    # add an exit button
    result[0].append(sg.Button('exit'))
    return result

def add_search_listbox(ui, listbo):
    ui.append([
        [sg.Text('search a preset: ')],
        [sg.Button('search', bind_return_key=True),
         sg.InputText(do_not_clear=False, )],
        sg.Listbox(values=listbo, size=(43, 5), key='listbox',pad=(62,0),enable_events=True)
        ])
    return ui

if __name__ == '__main__':
    # get the presets from the csv file and make a gui for them
    presets = pd.read_csv('Ahk_presets.csv')
    # generate a gui to with n number of presets from the csv file
    layout = buttons_from_array(presets['preset'].to_numpy()[0:5])
    # add a text box to the gui, names listbox, and a search button
    layout = add_search_listbox(layout, presets['preset'][5:].to_list())
    # add a scrollable list of the presets to the gui excluding the first 5
    gameRegion = getWindowsWithTitle('Simplicity+')[0]
    window = sg.Window('presets', layout, location=(
        gameRegion.left+50, gameRegion.top-75))
    # driver code
    while True:
        events, values = window.Read()
        if events == 'exit':
            break
        if events == 'listbox':
            events = values['listbox'][0]
            main([events], values)
        else:
            main([events], values)
