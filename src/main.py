import cv2
import os
import joker
from constants import root_dir, templates_dir, final_cards_dir, cards_input_dir


def main():
    # root_dir = r'D:\_Guy\PDNs\cards'
    j = joker.JokerToolbox(templates_dir, final_cards_dir)
    j.clear_output_dir()
    for dir_name, template_name in zip(['adventure', 'enemies', 'characters', 'spells', 'supporters', 'tools'],
                                       ['adventure', 'enemy', 'character', 'spell', 'supporter', 'tool']):
        dir_path = cards_input_dir + '\\' + dir_name
        print(dir_path)
        # j.edit_dir(dir_path, template_name)
        j.regenerate_dir(dir_path, template_name)
    for printout in j.make_printouts(j.output_dir, 3, 3, 0.15):
        joker.show_img(printout)
    print('done')
    return


if __name__ == '__main__':
    main()
