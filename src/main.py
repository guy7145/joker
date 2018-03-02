import cv2
import os

import joker

if __name__ == '__main__':
    j = joker.JokerToolbox(r'D:\_Guy\PDNs\cards\templates', r'D:\_Guy\PDNs\cards\final cards')
    # j.edit_dir(r'D:\_Guy\PDNs\cards\images\characters', 'character')
    for d, t in zip(['characters', 'enemies', 'spells', 'supporters', 'tools'],
                    ['character', 'enemy', 'spell', 'supporter', 'tool']):
        j.clear_output_dir()
        print(d)
        j.regenerate_dir(r'D:\_Guy\PDNs\cards\images\{}'.format(d), t)
        print('printable...')
        ps = j.make_printables(r'D:\_Guy\PDNs\cards\final cards', row_size=3, column_size=3, resize=0.1)
        for i, printable in enumerate(ps):
            cv2.imwrite(os.path.join(r'D:\_Guy\PDNs\cards\print', '{}{}.png'.format(d, i + 1)), printable)
    print('done')
    # j.make_printable(r'D:\_Guy\PDNs\cards\final cards', row_size=3, column_size=3, resize=0.3)
