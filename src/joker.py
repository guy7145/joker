from itertools import product, chain, repeat
import json
import os
import cv2
import numpy as np
from PIL import ImageDraw, Image, ImageFont
import math

from gui import query_card_info
from templates import BACK_IMG_NAME, MASK_IMG_NAME, AdventureFactory, EnemyFactory, SpellFactory, ToolFactory


def save_card(c, card_path):
    with open(card_path, 'w') as f:
        json.dump(c, f)


def load_card(_path):
    c = None
    with open(_path, 'r') as file:
        c = json.load(file)
    if c is None:
        raise Exception()

    c['img'] = cv2.imread(c['img_path'])
    del c['img_path']
    return c


def show_img(img, wait=True):
    img = cv2.resize(img, (int(img.shape[1]/2), int(img.shape[0]/2)))
    cv2.imshow('hi', img)
    if wait:
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return


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


def get_text_img(shape, text, font_type, font_size, align, rtl=False, fit=True, text_color=(0, 0, 0)):
    # text = text.replace('\n', '. ').replace('\r', '').replace('..', '.')
    img = Image.new('RGB', shape, color=(255, 255, 255))
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

    draw.text(position, text, font=font, fill=text_color)
    return np.array(img)


def create_white_image(height, width, depth):
    WHITE = 255
    img = np.ndarray((height, width, depth), dtype=np.uint8)
    img.fill(WHITE)
    return img


class JokerToolbox:
    @staticmethod
    def get_card_json(path, template):
        json_path = path[:path.rfind(".")] + '.json'
        if os.path.exists(json_path):
            return load_card(json_path)
        else:
            keys = list(template.get_card_fields())
            keys.remove("img")
            return dict.fromkeys(keys, '')

    @staticmethod
    def is_json(path):
        return path[path.rfind('.'):] == '.json'

    @staticmethod
    def is_image(path):
        return not JokerToolbox.is_json(path)

    def __init__(self, templates_dir, output_dir):
        template_names = [d for d in os.listdir(templates_dir) if d.find('.') < 0]
        template_images = [
            {
                'template_img': cv2.imread(os.path.join(templates_dir, name, BACK_IMG_NAME)),
                'template_mask': cv2.imread(os.path.join(templates_dir, name, MASK_IMG_NAME))
            }
            for name in template_names
        ]
        template_types = []
        for tn in template_names:
            with open(os.path.join(templates_dir, tn, 'type.txt'), 'r') as type_file:
                template_types.append(type_file.readlines()[0])
        constructor_mapping = {
            'adventure': AdventureFactory,
            'enemy': EnemyFactory,
            'spell': SpellFactory,
            'tool': ToolFactory
        }
        self.templates = {name: constructor_mapping[type](**images) for name, type, images in
                     zip(template_names, template_types, template_images)}
        self.output_dir = output_dir
        return

    def clear_output_dir(self):
        for root_dir, _, file_names in os.walk(self.output_dir):
            for file_name in file_names:
                file_path = os.path.join(root_dir, file_name)
                os.remove(file_path)
        return

    def regenerate_dir(self, path, template_name):
        template = self.templates[template_name]
        for root_dir, _, file_names in os.walk(path):
            for file_name in file_names:
                if not JokerToolbox.is_image(file_name):
                        continue

                file_path = os.path.join(root_dir, file_name)
                card_info = JokerToolbox.get_card_json(file_path, template)
                card_info['img'] = cv2.imread(file_path)
                card_img = template.generate_card(card_info)
                cv2.imwrite('{}\{}_{}.png'.format(self.output_dir, template_name, file_name[:file_name.rfind(".")]),
                            card_img)
        return

    def edit_dir(self, path, template_name):
        for root_dir, _, file_names in os.walk(path):
            for file_name in file_names:
                if not JokerToolbox.is_image(file_name):
                    continue

                file_path = os.path.join(root_dir, file_name)
                self.edit(file_path, template_name)
        return

    def edit(self, file_path, template_name):
        template = self.templates[template_name]
        card_info = JokerToolbox.get_card_json(file_path, template)
        card_img = cv2.imread(file_path)
        card_info, card_img = query_card_info(card_info, template, card_img)
        cv2.destroyAllWindows()

        i = max(file_path.rfind('\\'), 0)
        file_name = file_path[i + 1:]
        card_info["img_path"] = file_name
        save_card(card_info, file_path[:file_path.rfind('.')] + '.json')
        cv2.imwrite('{}\{}_{}.png'.format(self.output_dir, template_name, file_name[:file_name.rfind(".")]), card_img)
        return

    @staticmethod
    def make_printables(path, row_size, column_size, resize=1):
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
