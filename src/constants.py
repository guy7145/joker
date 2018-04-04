from os import path

root_dir = r'.\cards'
templates_dir = path.join(root_dir, 'templates')
cards_input_dir = path.join(root_dir, 'images')
final_cards_dir = path.join(root_dir, 'final cards')

board_root_dir = path.join(root_dir, 'board')
board_tiles_input_dir = path.join(board_root_dir, 'tiles')
board_template_dir = path.join(board_root_dir, 'board_tile_template')

KEY_IMG_PATH = 'img_path'
KEY_IMG = 'img'
KEY_TITLE = 'title'
KEY_TEXT = 'text'
KEY_NB_INSTANCES_IN_DECK = '#'
KEY_STRENGTH = 'strength'
KEY_SKILL = 'skill'

KEY_RING_NUMBER = 'ring'

# BGR
AREA_COLOR_IMG = (210, 206, 255)
AREA_COLOR_TITLE = (231, 181, 255)
AREA_COLOR_TEXT = (153, 127, 255)
AREA_COLOR_STRENGTH = (142, 142, 255)
AREA_COLOR_SKILL = (255, 145, 209)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
