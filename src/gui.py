import json
import sys
import os
from PyQt5 import QtCore
import cv2
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
import joker
from templates import EnemyFactory, SpellFactory, AdventureFactory, ToolFactory, BACK_IMG_NAME, MASK_IMG_NAME


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


def query_card_info(keys, _card_template, image, card_info=None):
    img_name = 'joker'
    offset = 0
    if card_info is None:
        card_info = dict.fromkeys(['img', 'title', 'text', 'strength', 'skill'], '')
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
        textbox.insertPlainText(card_info[k])
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
