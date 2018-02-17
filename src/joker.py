import cv2
import numpy as np
from PIL import ImageDraw, Image, ImageFont


def show_img(img, wait=True):
    img = cv2.resize(img, (int(img.shape[1]/2), int(img.shape[0]/2)))
    # cv2.destroyAllWindows()
    cv2.imshow('hi', img)
    if wait:
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return


# def read_configuration(conf_path):
#     with open(conf_path, 'r') as f:
#         conf = f.readlines()
#     img_path = conf[1].strip('\n')
#     tii = 2
#     tei = 4
#     title = conf[tii + 1]
#     text = '\n'.join(conf[tei + 1: len(conf)])
#     title_size = int(conf[tii].split(":")[1])
#     text_size = int(conf[tei].split(":")[1])
#     return img_path, title, title_size, text, text_size


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
    smaller_lines.append(current_line)
    line = '\n'.join(smaller_lines)
    return line


def get_text_img(shape, text, font_type, font_size, align, rtl=False, fit=True, text_color=(0, 0, 0)):
    img = Image.new('RGB', shape, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    if fit:
        w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type, max_height=shape[1])
        text = "\n".join([fit_line_by_width(draw, line, font, shape[0], rtl) for line in text.split("\n")])
        w, h, font = fit_font_by_height(drawer=draw, text=text, font_size=font_size, font_type=font_type, max_height=shape[1])
    else:
        font = ImageFont.truetype(font_type, font_size)
        w, h = draw.textsize(text, font)

    W = shape[0]
    position = (W // 2 - w // 2, 0)

    if rtl:
        text = '\n'.join([''.join(reversed(line)) for line in text.split("\n")])

    draw.text(position, text, font=font, fill=text_color, align=align)
    return np.array(img)


# def generate_cards_from_template(input_dir, output_dir, template_img, img_area_color, text_area_color, title_area_color):
#     img_shape, img_startX, img_endX, \
#     img_startY, img_endY = get_template_area(template_img, img_area_color)
#
#     txt_shape, txt_startX, txt_endX, \
#     txt_startY, txt_endY = get_template_area(template_img, text_area_color)
#
#     title_shape, title_startX, title_endX, \
#     title_startY, title_endY = get_template_area(template_img, title_area_color)
#
#     for root, _, files in os.walk(input_dir):
#         for f in files:
#             if not f[f.rfind("."):] == '.json':
#                 continue
#
#             conf_path = r'{}\{}'.format(root, f)
#             img_path, title, title_size, text, text_size = read_configuration(conf_path)
#             img_path = r'{}\{}'.format(root, img_path)
#             current_card = generate_card(template_img.copy(),
#                                          img_path,
#                                          img_shape, img_startX, img_startY, img_endX, img_endY,
#                                          title, title_size,
#                                          title_shape, title_startX, title_startY, title_endX, title_endY,
#                                          text, text_size,
#                                          txt_shape, txt_startX, txt_startY, txt_endX, txt_endY)
#
#             # save
#             show_img(current_card)
#             cv2.imwrite('{}\{}.png'.format(output_dir, f[:f.rfind(".")]), current_card)
#     return
