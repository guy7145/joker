import cv2

import joker

# FONT_KREDIT = "KREDIT1.TTF"
FONT_ARIAL = "arial.ttf"
FONT_STAM = 'STAM.TTF'
FONT_MISTRAL = 'MISTRAL.TTF'


STATS_SIZE = 128
TITLE_SIZE = 96
TEXT_SIZE = 42

ALIGN_CENTER = 'center'
ALIGN_RIGHT = 'right'

COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 38, 0)

TEMPLATES_DIR = r'D:\_Guy\PDNs\cards\templates'
MASKS_DIR = TEMPLATES_DIR + r'\masks'
BACKS_DIR = TEMPLATES_DIR + r'\backgrounds'


# region card templates


class Placeholder:
    def __init__(self, shape, startX, endX, startY, endY):
        self.shape = shape
        self.offsets = startX, endX, startY, endY
        return


class CardTemplate:
    def __init__(self, template_img, template_mask,
                 img_area_color=(210, 206, 255),
                 title_area_color=(231, 181, 255),
                 text_area_color=(153, 127, 255)):

        # joker.show_img(template_img)
        # joker.show_img(template_mask)
        self.template_img = template_img
        self.img_place = Placeholder(*joker.get_template_area(template_mask, img_area_color))
        self.ttl_place = Placeholder(*joker.get_template_area(template_mask, title_area_color))
        self.txt_place = Placeholder(*joker.get_template_area(template_mask, text_area_color))
        return

    def get_name(self):
        raise NotImplementedError()

    def generate_card(self, card_instance):
        card = self.template_img.copy()
        joker.paste(card, cv2.resize(card_instance['img'], self.img_place.shape), *self.img_place.offsets)

        joker.paste(card, joker.get_text_img(self.ttl_place.shape,
                                             card_instance['title'],
                                             FONT_STAM, TITLE_SIZE, ALIGN_CENTER, rtl=True, fit=False),
                    *self.ttl_place.offsets)

        joker.paste(card, joker.get_text_img(self.txt_place.shape,
                                             card_instance['text'],
                                             FONT_ARIAL, TEXT_SIZE, ALIGN_RIGHT, rtl=True, fit=True),
                    *self.txt_place.offsets)
        return card


class AdventureTemplate(CardTemplate):
    def __init__(self,
                 template_img=cv2.imread(BACKS_DIR + r'\adventure.png'),
                 template_mask=cv2.imread(MASKS_DIR + r'\adventure.png'),
                 *args, **kwargs):
        super().__init__(template_img, template_mask, *args, **kwargs)
        return

    def get_name(self):
        return "Adventure"


class SpellTemplate(CardTemplate):
    def __init__(self,
                 template_img=cv2.imread(BACKS_DIR + r'\spell.png'),
                 template_mask=cv2.imread(MASKS_DIR + r'\spell.png'),
                 *args, **kwargs):
        super().__init__(template_img, template_mask, *args, **kwargs)
        return

    def get_name(self):
        return "Spell"


class EnemyTemplate(AdventureTemplate):
    def __init__(self,
                 template_mask=cv2.imread(MASKS_DIR + r'\enemy.png'),
                 strength_area_color=(142, 142, 255),
                 skill_area_color=(255, 145, 209), *args, **kwargs):
        super().__init__(template_mask=template_mask, *args, **kwargs)
        self.strength_place = Placeholder(*joker.get_template_area(template_mask, strength_area_color))
        self.skill_place = Placeholder(*joker.get_template_area(template_mask, skill_area_color))
        return

    def get_name(self):
        return "Enemy"

    def generate_card(self, card_inst):
        card = super().generate_card(card_inst)
        joker.paste(card, joker.get_text_img(self.skill_place.shape,
                                             card_inst['skill'],
                                             FONT_MISTRAL, STATS_SIZE, ALIGN_CENTER,
                                             rtl=False, fit=False, text_color=COLOR_BLUE),
                    *self.skill_place.offsets)
        joker.paste(card, joker.get_text_img(self.strength_place.shape,
                                             card_inst['strength'],
                                             FONT_MISTRAL, STATS_SIZE, ALIGN_CENTER,
                                             rtl=False, fit=False, text_color=COLOR_RED),
                    *self.strength_place.offsets)
        return card


class ToolTemplate(CardTemplate):
    def __init__(self,
                 template_img=cv2.imread(BACKS_DIR + r'\tool.png'),
                 template_mask=cv2.imread(MASKS_DIR + r'\tool.png'),
                 *args, **kwargs):
        super().__init__(template_img, template_mask, *args, **kwargs)
        return

    def get_name(self):
        return "Tool"
# endregion


default_card = {
    'img': '',
    'title': '',
    'text': '',
    'strength': '',
    'skill': '',
}


if __name__ == "__main__":
    card_inst = {
        'img': cv2.imread(r"D:\_Guy\PDNs\cards\tmp\super saiyan.jpg"),
        'title': 'סופר סאייה',
        'text': """רשאי להשתמש בתחילת קרב )לפני הטלת הקובייה(.
5+ אוטיזם למשך אותו הקרב.""",
        'strength': '12',
        'skill': '-4'
    }
    adventure = AdventureTemplate()
    spell = SpellTemplate()
    enemy = EnemyTemplate()
    tool = ToolTemplate()
    joker.show_img(adventure.generate_card(card_inst))
    joker.show_img(spell.generate_card(card_inst))
    joker.show_img(enemy.generate_card(card_inst))
    joker.show_img(tool.generate_card(card_inst))
