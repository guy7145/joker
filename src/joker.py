from itertools import product, chain, repeat
import json
import os
import cv2
import numpy as np
from PIL import ImageDraw, Image, ImageFont
import math

from constants import KEY_IMG, KEY_NB_INSTANCES_IN_DECK, KEY_IMG_PATH, COLOR_WHITE
from gui import query_card_info
from templates import BACK_IMG_NAME, MASK_IMG_NAME, AdventureFactory, EnemyFactory, SpellFactory, ToolFactory


# region utils (saving and loading, etc.)
def remove_suffix(path):
    return path[:path.rfind('.')]


def get_suffix(path):
    return path[path.rfind('.'):]


def is_image(path):
    return not is_json(path)


def is_json(path):
    return get_suffix(path) == '.json'


def save_card(c, card_path):
    safe = dict(c)

    if KEY_IMG in safe.keys():
        del safe[KEY_IMG]

    with open(card_path, 'w') as f:
        json.dump(safe, f)

    return


def load_existing_card(json_path, img_path):
    c = None
    with open(json_path, 'r') as file:
        c = json.load(file)
    if c is None:
        raise Exception()

    c[KEY_IMG] = cv2.imread(img_path)
    return c


def load_or_create_card(img_path, template):
    json_path = remove_suffix(img_path) + '.json'
    if os.path.exists(json_path):
        return load_existing_card(json_path, img_path)
    else:
        keys = list(template.get_fields())
        keys.remove(KEY_IMG)
        card_info = dict.fromkeys(keys, '')
        card_info[KEY_IMG] = cv2.imread(img_path)
        return card_info


def show_img(img, wait=True, resize=0.25):
    resize = math.sqrt(resize)
    img = cv2.resize(img, (int(img.shape[1] * resize), int(img.shape[0] * resize)))
    cv2.imshow('hi', img)
    if wait:
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return
# endregion


# region image editing and processing
def create_white_image(height, width, depth):
    WHITE = 255
    img = np.ndarray((height, width, depth), dtype=np.uint8)
    img.fill(WHITE)
    return img


def to_rgba(img):
    channels = cv2.split(img)
    if len(channels) == 4:
        pass
    elif len(channels) == 3:
        alpha_channel = np.ones(channels[0].shape, dtype=channels[0].dtype)
        img = cv2.merge((*channels, alpha_channel))
    else:
        raise Exception()
    return img


def get_template_area(img, area_color):
    mask = cv2.inRange(img, area_color, area_color)
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    box = np.int0(cv2.boxPoints(cv2.minAreaRect(contours[-1])))

    numOfCorners = 4
    startX = min([box[i][0] for i in range(numOfCorners)])
    startY = min([box[i][1] for i in range(numOfCorners)])
    endX = max([box[i][0] for i in range(numOfCorners)])
    endY = max([box[i][1] for i in range(numOfCorners)])

    w = endX - startX
    h = endY - startY
    shape = (w, h)
    return shape, startX, endX, startY, endY


def paste(dst, src, startX, endX, startY, endY):
    dst[startY:endY, startX:endX] = src
    return


def paste_alpha(dst, src, startX, endX, startY, endY):
    h_src, w_src, d_src = src.shape
    h_dst, w_dst, d_dst = dst.shape
    # endY = min(startY + h_src, h_dst)
    # endX = min(startX + w_src, w_dst)
    # print('{}-{}, {}-{}'.format(startX, endX, startY, endY))

    # get alpha channel
    if d_src < 4:
        src_alpha = np.full((h_src, w_src), 255.)
    else:
        src_alpha = src[:, :, 3]

    alpha_factor = src_alpha[:, :, np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

    src_rgb = src[:, :, :3].astype(np.float32)
    dst_rgb = dst[startY:endY, startX:endX, :3].astype(np.float32)

    dst[startY:endY, startX:endX, :3] = dst_rgb * (1 - alpha_factor) + src_rgb * alpha_factor
    return


def fit_image(shape, image_to_fit):
    img = np.ndarray(shape)
    h, w, d = shape
    H, W, D = image_to_fit.shape
    ratio = min([H/h, W/w])

    print("{},{},{} -{}-> {},{},{}".format(H, W, D, ratio, h, w, d))

    image_to_fit = cv2.resize(image_to_fit, (int(H / ratio), int(W / ratio)))
    img[:, :, :] = image_to_fit[0:h, 0:w, :d]
    return img
# endregion


# region text-imaging
def fit_font_by_height(drawer, text, font_size, font_type, max_height):
    while True:
        font = ImageFont.truetype(font_type, font_size)
        w, h = drawer.textsize(text, font)
        if h > max_height:
            font_size -= 1
        else:
            break
    return w, h, font


def fit_line_by_width(drawer, line, font, max_width, rtl=False):
    w, _ = drawer.textsize(line, font)
    if w < max_width:
        return line
    smaller_lines = []
    words = line.split(" ")
    # words = list(line)
    if rtl:
        words.reverse()
    current_line = words.pop()
    while len(words) > 0:
        w, _ = drawer.textsize(current_line + " " + words[0], font)
        if w > max_width:
            smaller_lines.append(current_line)
            current_line = words.pop()
        else:
            current_line += " " + words.pop()
            # current_line += words.pop()
    smaller_lines.append(current_line)
    line = '\n'.join(smaller_lines)
    return line


def get_text_img(shape, text, font_type, font_size, align, rtl=False, fit=True, text_color=(0, 0, 0), format="RGB"):
    if format == "RGBA":
        color = 0
    else:
        color = COLOR_WHITE

    img = Image.new(format, shape, color=color)

    # region dealing with crap
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')
    text = text.strip('\n')
    if text == '':
        return np.array(img)
    # endregion

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_type, font_size)
    w, h = draw.textsize(text, font)
    target_h, target_w = shape
    if fit:
        if w > target_w and not h >= target_h:
            text = "\n".join([fit_line_by_width(draw, line, font, shape[0], rtl) for line in text.split("\n")])
            w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type, max_height=shape[1])
        elif w <= target_w and h > target_h:
            w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type,
                                            max_height=shape[1])
        else:
            # w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type, max_height=shape[1])
            text = "\n".join([fit_line_by_width(draw, line, font, shape[0], rtl) for line in text.split("\n")])
            w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type, max_height=shape[1])


    else:
        font = ImageFont.truetype(font_type, font_size)
        w, h = draw.textsize(text, font)

    W = shape[0]
    position = (W // 2 - w // 2, 0)

    if rtl:
        text = '\n'.join([''.join(reversed(line)) for line in text.split("\n")])

    draw.multiline_text(position, text, font=font, fill=text_color, align=align)
    # draw.text(position, text, font=font, fill=text_color)
    return np.array(img)
# endregion


class JokerToolbox:
    def __init__(self, templates_dir, output_dir):
        self.output_dir = output_dir

        template_names = [d for d in os.listdir(templates_dir) if d.find('.') < 0]
        template_images = [
            {
                'template_img': cv2.imread(os.path.join(templates_dir, name, BACK_IMG_NAME)),
                'template_mask': cv2.imread(os.path.join(templates_dir, name, MASK_IMG_NAME))
            }
            for name in template_names
        ]
        template_types = []
        for name in template_names:
            with open(os.path.join(templates_dir, name, 'type.txt'), 'r') as type_file:
                template_types.append(type_file.readlines()[0])

        constructor_mapping = {
            'adventure': AdventureFactory,
            'enemy': EnemyFactory,
            'spell': SpellFactory,
            'tool': ToolFactory
        }
        self.templates = {name: constructor_mapping[type](**images) for name, type, images in zip(template_names, template_types, template_images)}
        return

    def clear_output_dir(self):
        for root_dir, _, file_names in os.walk(self.output_dir):
            for file_name in file_names:
                file_path = os.path.join(root_dir, file_name)
                os.remove(file_path)
        return

    def save_final_card_to_output_dir(self, final_card, card_name, template_name, nb_instances):
        for i in range(nb_instances):
            cv2.imwrite('{}\{}_{}_x{}.png'.format(self.output_dir, template_name, card_name, i + 1), final_card)
        return

    def regenerate_dir(self, path, template_name):
        template = self.templates[template_name]
        for root_dir, _, file_names in os.walk(path):
            for file_name in file_names:
                if not is_image(file_name):
                        continue

                file_path = os.path.join(root_dir, file_name)
                card_info = load_or_create_card(file_path, template)
                # card_info[KEY_IMG] = cv2.imread(file_path)
                card_img = template.generate_image(card_info)
                self.save_final_card_to_output_dir(card_img,
                                                   file_name[:file_name.rfind(".")],
                                                   template_name,
                                                   int(card_info[KEY_NB_INSTANCES_IN_DECK]))
        return

    def edit_dir(self, path, template_name):
        for root_dir, _, file_names in os.walk(path):
            for file_name in file_names:
                if not is_image(file_name):
                    continue

                file_path = os.path.join(root_dir, file_name)
                self.edit(file_path, template_name)
        return

    def edit(self, file_path, template_name):
        template = self.templates[template_name]
        card_info = load_or_create_card(file_path, template)
        card_info, card_img = query_card_info(card_info, template)
        cv2.destroyAllWindows()

        i = max(file_path.rfind('\\'), 0)
        file_name = file_path[i + 1:]
        card_info[KEY_IMG_PATH] = file_name
        save_card(card_info, remove_suffix(file_path) + '.json')
        self.save_final_card_to_output_dir(card_img,
                                           template_name,
                                           file_name[:file_name.rfind(".")],
                                           int(card_info[KEY_NB_INSTANCES_IN_DECK]))
        return

    @staticmethod
    def make_printouts(path, row_size, column_size, resize=1):
        def iter_images():
            for root_dir, _, file_names in os.walk(path):
                for file_name in file_names:
                    if file_name.rfind('.png') > 0:
                        yield cv2.imread(os.path.join(root_dir, file_name))

        def iter_image_clusters():
            i = 0
            images = []
            for image in iter_images():
                images.append(image)
                i += 1
                if i == row_size * column_size:
                    yield images
                    i = 0
                    images = []
            if len(images) > 0:
                yield images

        printables = []
        resize = math.sqrt(resize)
        for number, images in enumerate(iter_image_clusters()):
            height, width, depth = images[0].shape  # all images have the same dimensions and color depth
            height, width = int(height * resize), int(width * resize)

            printable = create_white_image(row_size * height, column_size * width, depth)
            for img, (i, j) in zip(images, product(range(row_size), range(column_size))):
                img = cv2.resize(img, (width, height))
                paste(printable, img, width * j, width * (j + 1), height * i, height * (i + 1))
            printables.append(printable)
        return printables
