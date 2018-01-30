import cv2

from joker import generate_cards_from_template


def main():
    input_dir = r'D:\_Guy\PDNs\cards\tmp'
    output_dir = r'D:\_Guy\PDNs\cards\generated_cards'
    template_img = cv2.imread(r'D:\_Guy\PDNs\cards\empty adventure card template.png')
    # BGR
    img_area_color = (210, 206, 255)
    txt_area_color = (153, 127, 255)
    title_area_color = (231, 181, 255)
    generate_cards_from_template(input_dir, output_dir, template_img, img_area_color, txt_area_color, title_area_color)
    return


if __name__ == '__main__':
    main()
