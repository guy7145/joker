import cv2
import joker

# region configuration
# FONT_KREDIT = "KREDIT1.TTF"
from constants import KEY_IMG, KEY_TITLE, KEY_TEXT, KEY_NB_INSTANCES_IN_DECK, KEY_STRENGTH, KEY_SKILL, AREA_COLOR_TEXT, \
    AREA_COLOR_TITLE, AREA_COLOR_IMG, AREA_COLOR_STRENGTH, AREA_COLOR_SKILL

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


class Placeholder:
    def __init__(self, shape, startX, endX, startY, endY):
        self.shape = shape
        self.offsets = startX, endX, startY, endY
        return


class Template:
    def __init__(self):
        return

    def get_template_name(self):
        raise NotImplementedError()

    def generate_image(self, instance):
        raise NotImplementedError()

    def get_fields(self):
        raise NotImplementedError()


class CardTemplate(Template):
    def __init__(self, template_img, template_mask,
                 img_area_color=AREA_COLOR_IMG,
                 title_area_color=AREA_COLOR_TITLE,
                 text_area_color=AREA_COLOR_TEXT):
        super().__init__()
        self.template_img = template_img
        self.template_mask = template_mask
        self.img_place = Placeholder(*joker.get_template_area(template_mask, img_area_color))
        self.ttl_place = Placeholder(*joker.get_template_area(template_mask, title_area_color))
        self.txt_place = Placeholder(*joker.get_template_area(template_mask, text_area_color))
        return

    def get_template_name(self):
        raise NotImplementedError()

    def generate_image(self, instance):
        card = self.template_img.copy()
        joker.paste(card, cv2.resize(instance[KEY_IMG], self.img_place.shape), *self.img_place.offsets)

        joker.paste(card, joker.get_text_img(self.ttl_place.shape,
                                             instance[KEY_TITLE],
                                             FONT_STAM, TITLE_SIZE, ALIGN_CENTER, rtl=True, fit=False),
                    *self.ttl_place.offsets)

        joker.paste(card, joker.get_text_img(self.txt_place.shape,
                                             instance[KEY_TEXT],
                                             FONT_ARIAL, TEXT_SIZE, ALIGN_RIGHT, rtl=True, fit=True),
                    *self.txt_place.offsets)
        return card

    def get_fields(self):
        return KEY_IMG, KEY_TITLE, KEY_TEXT, KEY_NB_INSTANCES_IN_DECK


class SpellFactory(CardTemplate):
    def get_template_name(self):
        return "Spell"


class ToolFactory(CardTemplate):
    def get_template_name(self):
        return "Tool"


class AdventureFactory(CardTemplate):
    def get_template_name(self):
        return "Adventure"


class EnemyFactory(AdventureFactory):
    def __init__(self, strength_area_color=AREA_COLOR_STRENGTH, skill_area_color=AREA_COLOR_SKILL, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strength_place = Placeholder(*joker.get_template_area(self.template_mask, strength_area_color))
        self.skill_place = Placeholder(*joker.get_template_area(self.template_mask, skill_area_color))
        return

    def get_template_name(self):
        return "Enemy"

    def generate_image(self, instance):
        card = super().generate_image(instance)
        no_text = '-'
        strength = instance.get(KEY_STRENGTH, no_text)
        skill = instance.get(KEY_SKILL, no_text)
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

    def get_fields(self):
        keys = list(super().get_fields())
        keys.extend((KEY_STRENGTH, KEY_SKILL))
        return keys
