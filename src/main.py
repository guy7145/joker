import cv2
import os

import joker


def main():
    dir = '.\\cards'
    j = joker.JokerToolbox(dir + r'\templates', dir + r'\final cards')
    for d, t in zip(['characters', 'enemies', 'spells', 'supporters', 'tools'],
                    ['character', 'enemy', 'spell', 'supporter', 'tool']):
        print(dir + r'\images' + '\\' + d)
        j.edit_dir(dir + r'\images' + '\\' + d, t)
        print('done')
    return


if __name__ == '__main__':
    main()
