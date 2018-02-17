import cv2

# from joker import generate_cards_from_template
import os

import joker
from gui import query_card_info, save_card, load_card
from templates import ToolFactory, SpellFactory, AdventureFactory, EnemyFactory, BACK_IMG_NAME, MASK_IMG_NAME


def main(dir, template_name):
    root_dir = r'D:\_Guy\PDNs\cards'
    templates_dir = os.path.join(root_dir, 'templates')
    out_dir = os.path.join(root_dir, 'output')
    conf_dir = os.path.join(out_dir, 'conf')
    gen_dir = os.path.join(out_dir, 'generated')

    template_names = ['adventure', 'enemy', 'spell', 'tool']
    template_constructors = [AdventureFactory, EnemyFactory, SpellFactory, ToolFactory]
    template_images = [
        {
            'template_img': cv2.imread(os.path.join(templates_dir, name, BACK_IMG_NAME)),
            'template_mask': cv2.imread(os.path.join(templates_dir, name, MASK_IMG_NAME))
        }
        for name in template_names
    ]
    templates = { name: constructor(**images) for name, constructor, images in zip(template_names, template_constructors, template_images)}

    ks = list(templates[template_name].get_card_fields())
    ks.remove("img")
    _template = templates[template_name]
    path = r'D:\_Guy\PDNs\cards\images\{}'.format(dir)
    output_dir = r'D:\_Guy\PDNs\cards\final cards'
    for root, _, files in os.walk(path):
        for f in files:
            f_full = root + "\\" + f
            print(f_full)
            if f[f.rfind("."):] == '.json':
                # joker.show_img(_template.generate_card(load_card(f_full)))
                continue
            # else:
            #     continue

            json_path = f_full[:f_full.rfind(".")] + '.json'
            print(json_path)
            if os.path.exists(json_path):
                card_info = load_card(json_path)
            else:
                card_info = None
            img = cv2.imread(f_full)
            img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
            card, card_img = query_card_info(ks, _template, img, card_info=card_info)

            cv2.destroyAllWindows()
            card["img_path"] = f_full
            save_card(card, f_full[:f_full.rfind('.')] + '.json')
            cv2.imwrite('{}\{}.png'.format(output_dir, f[:f.rfind(".")]), card_img)
    return


if __name__ == '__main__':
    main('characters', 'enemy')
