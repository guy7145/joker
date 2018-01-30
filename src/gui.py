import json
import sys
import os
from PyQt5 import QtCore
import cv2
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
import joker
from templates import default_card, EnemyTemplate, SpellTemplate


def save_card(c, card_path):
    with open(card_path, 'w') as f:
        json.dump(card, f)


def load_card(_path):
    c = None
    with open(_path, 'r') as file:
        c = json.load(file)
    if c is None:
        raise Exception()

    c['img'] = cv2.imread(c['img_path'])
    del c['img_path']
    return c


def query_card_info(keys, _card_template, image):
    img_name = ''
    offset = 0
    card_info = default_card.copy()
    card_info['img'] = image
    actions = []
    app = QApplication(sys.argv)
    w = QDialog()
    w.setWindowTitle(img_name)
    w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    w.setModal(True)

    def action(name, text_box):
        def act():
            card_info[name] = text_box.toPlainText()
        return act

    def create_text_changed(_k, _box, _w):
        def update_design():
            card_info[_k] = _box.toPlainText()
            joker.show_img(_card_template.generate_card(card_info), wait=False)

        return update_design

    for k in keys:
        label = QLabel(k + ":", w)
        label.move(20, 80*offset)
        textbox = QPlainTextEdit(w)
        textbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        textbox.resize(280, 40)
        textbox.move(20, 80*offset + 20)
        textbox.textChanged.connect(create_text_changed(k, textbox, w))
        offset += 1
        actions.append(action(k, textbox))

    def create_onclick(window):
        @pyqtSlot()
        def on_click():
            for a in actions:
                a()
            window.close()
        return on_click

    # Create a button in the window
    button = QPushButton('OK', w)
    button.clicked.connect(create_onclick(w))
    button.move(20, 80*offset)
    card_img = _card_template.generate_card(card_info)
    joker.show_img(card_img, wait=False)
    w.show()
    app.exec_()
    del card_info['img']
    return card_info, card_img


ks = list(default_card.keys())
ks.remove("img")
_template = EnemyTemplate()
path = r'D:\_Guy\PDNs\cards\images\enemies'
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
        img = cv2.imread(f_full)
        img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
        card, card_img = query_card_info(ks, _template, img)
        cv2.destroyAllWindows()
        card["img_path"] = f_full
        save_card(card, f_full[:f_full.rfind('.')] + '.json')
        cv2.imwrite('{}\{}.png'.format(output_dir, f[:f.rfind(".")]), card_img)
