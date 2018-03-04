import cv2
import os
import joker


def main():
    root_dir = '.\\cards'
    j = joker.JokerToolbox(root_dir + r'\templates', root_dir + r'\final cards')
    for d, t in zip(['characters', 'enemies', 'spells', 'supporters', 'tools'],
                    ['character', 'enemy', 'spell', 'supporter', 'tool']):
        print(root_dir + r'\images' + '\\' + d)
        j.edit_dir(root_dir + r'\images' + '\\' + d, t)
        print('done')
    return


if __name__ == '__main__':
    main()
