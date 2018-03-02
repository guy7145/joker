import numpy as np
from itertools import product, chain, repeat
import joker
from templates import FONT_ARIAL


class Tile:
    def __init__(self, title, text):
        self.title, self.text = title, text
        return

    def __repr__(self):
        return self.title

    def generate(self, h, w):
        return joker.get_text_img((h, w), 'tile', FONT_ARIAL, 96, 'center')

# region tiles
house_guy_nurit = Tile('tile', '...')
house_guy_bh = Tile('tile', '...')
house_ido = Tile('tile', '...')
house_gal = Tile('tile', '...')
house_ron = Tile('tile', '...')
house_omer = Tile('tile', '...')
house_nitzan = Tile('tile', '...')
nasa = Tile('tile', '...')
recruit = Tile('tile', '...')
beit_shean = Tile('tile', '...')
afula = Tile('tile', '...')
gilboa = Tile('tile', '...')
menta_gas_station = Tile('tile', '...')
pita_druzit = Tile('tile', '...')
school = Tile('tile', '...')
coca = Tile('tile', '...')
university = Tile('tile', '...')
black_hole = Tile('tile', '...')
heaven = Tile('tile', '...')
sun = Tile('tile', '...')
milky_way = Tile('tile', '...')
moon = Tile('tile', '...')
meteor_shower = Tile('tile', '...')
olympus = Tile('tile', '...')
space_station = Tile('tile', '...')
sahne = Tile('tile', '...')
asi_nir_david = Tile('tile', '...')
revaya_b = Tile('tile', '...')
trablinka = Tile('tile', '...')
pool_ram_on = Tile('tile', '...')
geva = Tile('tile', '...')
kibutzim_river = Tile('tile', '...')
sea_of_galilea = Tile('tile', '...')
tiberias = Tile('tile', '...')
hospital = Tile('tile', '...')
pedagogue = Tile('tile', '...')
bakum = Tile('tile', '...')
kaban = Tile('tile', '...')
bottom_city_haifa = Tile('tile', '...')
air_force = Tile('tile', '...')
bahadim = Tile('tile', '...')
hell = Tile('tile', '...')
dorms = Tile('tile', '...')
katef_shaol = Tile('tile', '...')
bus = Tile('tile', '...')
konetiket = Tile('tile', '...')
# endregion

# region iterate_ring test
# t0, t1, t2, t3 = Tile('0', '...'), Tile('1', '...'), Tile('2', '...'), Tile('3', '...')
# tiles = np.array([[t0, t0, t0, t0, t0, t0, t0],
#                   [t0, t1, t1, t1, t1, t1, t0],
#                   [t0, t1, t2, t2, t2, t1, t0],
#                   [t0, t1, t2, t3, t2, t1, t0],
#                   [t0, t1, t2, t2, t2, t1, t0],
#                   [t0, t1, t1, t1, t1, t1, t0],
#                   [t0, t0, t0, t0, t0, t0, t0]])
# endregion

tiles = np.array([[tiberias, beit_shean, katef_shaol, gilboa, house_guy_nurit, menta_gas_station, pita_druzit, house_gal, school],
                  [sea_of_galilea, bakum, bahadim, university, dorms, coca, bus, nasa, konetiket],
                  [coca, coca, coca, coca, coca, coca, coca, coca, coca],
                  [coca, coca, coca, coca, coca, coca, coca, coca, coca],
                  [coca, coca, coca, coca, coca, coca, coca, coca, coca],
                  [coca, coca, coca, coca, coca, coca, coca, coca, coca]])


def iterate_ring(rectangle, ring_num):
    y_max, x_max = rectangle.shape
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

    for y, x in indexes:
        yield rectangle[y, x]
    return


class Board:
    def __init__(self, tile_width=500, tile_height=500):
        self.tile_width = tile_width
        self.tile_height = tile_height
        return

    def generate_board(self):
        tiles_y, tiles_x = tiles.shape
        board = np.ndarray((tiles_y * self.tile_height, tiles_x * self.tile_width, 3))
        WHITE = 255
        board.fill(255)
        for y, x in product(range(tiles_y), range(tiles_x)):
            joker.show_img(tiles[y, x].generate(self.tile_height, self.tile_width))
        return


for k in range(4):
    for i, tile in enumerate(iterate_ring(tiles, k)):
        print((i, tile))

# Board().generate_board()
