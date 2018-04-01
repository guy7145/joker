import cv2
import os
import joker


def main():
    # root_dir = r'D:\_Guy\PDNs\cards'
    root_dir = r'.\cards'

    j = joker.JokerToolbox(root_dir + r'\templates', root_dir + r'\final cards')
    j.clear_output_dir()
    for dir_name, template_name in zip(['adventure', 'enemies', 'characters', 'spells', 'supporters', 'tools'],
                                       ['adventure', 'enemy', 'character', 'spell', 'supporter', 'tool']):
        dir_path = root_dir + r'\images' + '\\' + dir_name
        print(dir_path)
        j.edit_dir(dir_path, template_name)

    # j.regenerate_dir(root_dir + r'\images' + '\\' + dir_name, template_name)
    # j.make_printouts(j.output_dir, 3, 3, 0.15)
    print('done')
    return


if __name__ == '__main__':
    main()
