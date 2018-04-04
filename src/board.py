import json

import cv2
import numpy as np
from itertools import product, chain, repeat

from PIL import Image

import joker
from constants import KEY_TEXT, KEY_TITLE, KEY_IMG, KEY_RING_NUMBER, AREA_COLOR_IMG, AREA_COLOR_TITLE, AREA_COLOR_TEXT, \
    board_root_dir, board_tiles_input_dir, KEY_IMG_PATH
from gui import query_card_info
from templates import FONT_ARIAL, Template, Placeholder, FONT_STAM, TITLE_SIZE, ALIGN_CENTER, ALIGN_RIGHT, TEXT_SIZE, \
    BOARD_TILE_TEXT_SIZE
import itertools
import os


# region tiles
# region outer ring
tiberias_recruitment_office="tiberias_recruitment_office"
beit_shean="beit_shean"
katef_shaol="katef_shaol"
gilboa="gilboa"
house_guy_nurit="house_guy_nurit"
menta_gas_station="menta_gas_station"
pita_druzit="pita_druzit"
house_gal="house_gal"
school="school"
konetiket="konetiket"
kadima="kadima"
beit_noam="beit_noam"
afula="afula"
afula_beer_fair="afula_beer_fair"
house_omer="house_omer"
house_ron="house_ron"
court_ram_on="court_ram_on"
house_nitzan="house_nitzan"
pool_ram_on="pool_ram_on"
house_ido="house_ido"
synagogue="synagogue"
hospital="hospital"
house_guy_bh="house_guy_bh"
sahne="sahne"
kibutzim_river="kibutzim_river"
sea_of_galilea="sea_of_galilea"
# endregion
# region middle ring
bakum="bakum"
bahadim="bahadim"
bgu="bgu"
dorms="dorms"
coca="coca"
bus870="bus870"
nasa="nasa"
eilat="eilat"
sdei_avraham="sdei_avraham"
valley_bar="valley_bar"
geva="geva"
ramat_yishai="ramat_yishai"
trablinka="trablinka"
revaya_b="revaya_b"
air_force="air_force"
lower_city_haifa="lower_city_haifa"
asi_nir_david="asi_nir_david"
kaban="kaban"
# endregion
# region inner ring
black_hole="black_hole"
heaven="heaven"
sun="sun"
milky_way="milky_way"
moon="moon"
meteor_shower="meteor_shower"
olympus="olympus"
space_station="space_station"
hell="hell"
cassiopeia="cassiopeia"
# endregion
# endregion

board_tiles_strings = np.array([[tiberias_recruitment_office, beit_shean, katef_shaol, gilboa, house_guy_nurit, menta_gas_station, pita_druzit, house_gal, school],
                                [sea_of_galilea, bakum, bahadim, bgu, dorms, coca, bus870, nasa, konetiket],
                                [sahne, kaban, hell, black_hole, cassiopeia, moon, space_station, eilat, kadima],
                                [kibutzim_river, asi_nir_david, olympus, heaven, meteor_shower, milky_way, sun, sdei_avraham, beit_noam],
                                [house_guy_bh, lower_city_haifa, air_force, revaya_b, trablinka, ramat_yishai, geva, valley_bar, afula],
                                [hospital, synagogue, house_ido, pool_ram_on, house_nitzan, court_ram_on, house_ron, house_omer, afula_beer_fair]])

TAG_WATER = 'water'
TAG_BEER = 'pub'
TAG_SIMPLE_DRAW = 'draw'
KEY_TAGS = "tags"

VALUE_MIDDLE_RING_NUMBER = '1'
VALUE_OUTER_RING_NUMBER = '0'

NORMAL_BOARD_TILE_SHAPE = (1000, 1000)


def iterate_ring_indexes(rectangle, ring_num):
    y_max, x_max = rectangle.shape

    #
    if x_max == y_max and x_max - 2*ring_num == 1:
        yield rectangle[ring_num, ring_num]
        return

    y_max, x_max = y_max - ring_num - 1, x_max - ring_num - 1
    start = ring_num
    # iteration order:
    #       1 >
    #
    #       > > > v
    #       ^     v   2 v
    #  ^4   ^     v
    #       ^ < < <
    #
    #            3
    #            <
    indexes = chain(zip(repeat(start), range(start, x_max)),
                    zip(range(start, y_max), repeat(x_max)),
                    zip(repeat(y_max), range(x_max, start, -1)),
                    zip(range(y_max, start, -1), repeat(start)))

    yield from indexes


class TileFactory(Template):
    def get_template_name(self):
        return "Tile"

    def get_fields(self):
        return KEY_IMG, KEY_TITLE, KEY_TEXT, KEY_RING_NUMBER, KEY_TAGS

    def __init__(self, foreground_image, template_mask, tile_shape=(500, 500),
                 title_area_color=AREA_COLOR_TITLE,
                 text_area_color=AREA_COLOR_TEXT):
        super().__init__()
        self.tile_shape = tile_shape
        self.template_img = np.ndarray((*NORMAL_BOARD_TILE_SHAPE, 3), dtype=np.uint8)
        self.template_img.fill(0)

        self.foreground_image = cv2.resize(foreground_image, NORMAL_BOARD_TILE_SHAPE)
        self.template_mask = cv2.resize(template_mask, NORMAL_BOARD_TILE_SHAPE)

        self.ttl_place = Placeholder(*joker.get_template_area(self.template_mask, title_area_color))
        self.txt_place = Placeholder(*joker.get_template_area(self.template_mask, text_area_color))
        return

    def generate_image(self, instance):
        card = self.template_img.copy()
        h, w, _ = card.shape
        tile_image = instance[KEY_IMG]
        # if instance[KEY_RING_NUMBER] == VALUE_OUTER_RING_NUMBER:
        #     tile_image = tint_color(tile_image, 1)
        # elif instance[KEY_RING_NUMBER] == VALUE_MIDDLE_RING_NUMBER:
        #     tile_image = tint_color(tile_image, 0)

        joker.paste(card, cv2.resize(tile_image, (h, w)), 0, h, 0, w)

        joker.paste_alpha(card, self.foreground_image, 0, h, 0, w)

        joker.paste_alpha(card, joker.get_text_img(self.ttl_place.shape,
                                             instance.get(KEY_TITLE, ''),
                                             FONT_STAM, TITLE_SIZE, ALIGN_CENTER, rtl=True, fit=False, format="RGBA"),
                          *self.ttl_place.offsets)

        joker.paste_alpha(card, joker.get_text_img(self.txt_place.shape,
                                             instance.get(KEY_TEXT, ''),
                                             FONT_ARIAL, BOARD_TILE_TEXT_SIZE, ALIGN_RIGHT, rtl=True, fit=True, format="RGBA", text_color=(255, 255, 255)),
                          *self.txt_place.offsets)
        return cv2.resize(card, self.tile_shape)


def tint_color(img, color):
    colorized = np.ndarray(img.shape, dtype=np.float64)

    black_and_white = np.average(img, 2)
    black_and_white *= 0.3
    for i in range(3):
        colorized[:, :, i] = black_and_white
        if i != color:
            colorized[:, :, i] *= 0.9

        colorized[:, :, color] *= 1.1

    colorized[colorized < 0] = 0
    colorized[colorized > 255] = 255
    return colorized.astype(np.uint8)


def generate_board(tiles_template):
    tiles_y, tiles_x = board_tiles.shape
    h, w = tiles_template.tile_shape
    board_image = joker.create_white_image(tiles_y * h, tiles_x * w, 3)

    for ring in range(3):
        for y, x in iterate_ring_indexes(board_tiles, ring):
            tile_image = tiles_template.generate_image(board_tiles[y, x])
            k = 0
            if y == ring:
                k = 2
            elif y == (tiles_y - 1) - ring:
                k = 0
            elif x == ring:
                k = 3
            elif x == (tiles_x - 1) - ring:
                k = 1
            tile_image = np.rot90(tile_image, k)
            joker.paste(board_image, tile_image, x * w, (x + 1) * w, y * h, (y + 1) * h)

    return board_image


def get_path(f):
    return os.path.join(board_tiles_input_dir, f)


tile_template = TileFactory(cv2.imread(os.path.join(board_root_dir, 'board_tile_template', 'foreground.png'), cv2.IMREAD_UNCHANGED),
                            cv2.imread(os.path.join(board_root_dir, 'board_tile_template', 'mask.png')))
images = {joker.remove_suffix(f): f for f in os.listdir(board_tiles_input_dir) if joker.is_image(f)}


# def make_or_load_tile(name):
#     path = joker.remove_suffix(get_path(images[name])) + '.json'
#     if os.path.exists(path):
#         tile = json.loads(path[:path.rfind('.')] + '.json')
#         for k in tile_template.get_fields():
#             if k not in tile.keys():
#                 tile[k] = ''
#         return tile
#     else:
#         return dict.fromkeys(tile_template.get_fields(), '')
#
#
# def save_tile(name, tile):
#     path = get_path(images[name])
#     path = path[:path.rfind('.')] + '.json'
#     with open(path, 'w') as file:
#         file.write(json.dumps(tile))
#     return


board_tiles = np.ndarray(board_tiles_strings.shape, dtype=object)
for i, j in itertools.product(*[range(l) for l in board_tiles.shape]):
    tile_name = board_tiles_strings[i, j]
    print(get_path(images[tile_name]))
    tile_info = joker.load_or_create_card(get_path(images[tile_name]), tile_template)

    tile_image = tile_info[KEY_IMG]
    if tile_info[KEY_RING_NUMBER] == VALUE_OUTER_RING_NUMBER:
        tile_image = tint_color(tile_image, 1)
    elif tile_info[KEY_RING_NUMBER] == VALUE_MIDDLE_RING_NUMBER:
        tile_image = tint_color(tile_image, 0)
    tile_info[KEY_IMG] = tile_image

    tile_info, _ = query_card_info(tile_info, tile_template)
    joker.save_card(tile_info, os.path.join(board_tiles_input_dir, tile_name + '.json'))
    board_tiles[i, j] = tile_info
joker.show_img(generate_board(tile_template), resize=0.1)
