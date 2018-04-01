import cv2
import joker

# region configuration
# FONT_KREDIT = "KREDIT1.TTF"
FONT_ARIAL = "arial.ttf"
FONT_STAM = 'STAM.TTF'
FONT_MISTRAL = 'MISTRAL.TTF'

STATS_SIZE = 128
TITLE_SIZE = 96
TEXT_SIZE = 46

ALIGN_CENTER = 'center'
ALIGN_RIGHT = 'right'

COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 38, 0)

BACK_IMG_NAME = 'background.png'
MASK_IMG_NAME = 'mask.png'
# endregion


KEY_IMG_PATH = 'img_path'
KEY_IMG = 'img'
KEY_TITLE = 'title'
KEY_TEXT = 'text'
KEY_NB_INSTANCES_IN_DECK = '#'
KEY_STRENGTH = 'strength'
KEY_SKILL = 'skill'


class Placeholder:
    def __init__(self, shape, startX, endX, startY, endY):
        self.shape = shape
        self.offsets = startX, endX, startY, endY
        return


class CardFactory:
    def __init__(self, template_img, template_mask,
                 img_area_color=(210, 206, 255),
                 title_area_color=(231, 181, 255),
                 text_area_color=(153, 127, 255)):

        # joker.show_img(template_img)
        # joker.show_img(template_mask)
        self.template_img = template_img
        self.template_mask = template_mask
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

    def get_card_fields(self):
        return KEY_IMG, KEY_TITLE, KEY_TEXT, KEY_NB_INSTANCES_IN_DECK


class SpellFactory(CardFactory):
    def get_name(self):
        return "Spell"


class ToolFactory(CardFactory):
    def get_name(self):
        return "Tool"


class AdventureFactory(CardFactory):
    def get_name(self):
        return "Adventure"


class EnemyFactory(AdventureFactory):
    def __init__(self, strength_area_color=(142, 142, 255), skill_area_color=(255, 145, 209), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strength_place = Placeholder(*joker.get_template_area(self.template_mask, strength_area_color))
        self.skill_place = Placeholder(*joker.get_template_area(self.template_mask, skill_area_color))
        return

    def get_name(self):
        return "Enemy"

    def generate_card(self, card_instance):
        card = super().generate_card(card_instance)
        no_text = '-'
        strength = card_instance.get('strength', no_text)
        skill = card_instance.get('skill', no_text)
        strength = strength if strength != '' else '-'
        skill = skill if skill != '' else '-'

        joker.paste(card, joker.get_text_img(self.skill_place.shape,
                                             skill,
                                             FONT_MISTRAL, STATS_SIZE, ALIGN_CENTER,
                                             rtl=False, fit=False, text_color=COLOR_BLUE),
                    *self.skill_place.offsets)

        joker.paste(card, joker.get_text_img(self.strength_place.shape,
                                             strength,
                                             FONT_MISTRAL, STATS_SIZE, ALIGN_CENTER,
                                             rtl=False, fit=False, text_color=COLOR_RED),
                    *self.strength_place.offsets)
        return card

    def get_card_fields(self):
        keys = list(super().get_card_fields())
        keys.extend((KEY_STRENGTH, KEY_SKILL))
        return keys
