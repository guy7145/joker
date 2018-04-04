import sys
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
import joker
from templates import KEY_IMG


def query_card_info(card_info, template):
    fields_to_query = list(card_info.keys())
    if KEY_IMG in fields_to_query:
        fields_to_query.remove(KEY_IMG)
    actions = []

    app = QApplication(sys.argv)
    w = QDialog()
    w.setWindowTitle('Joker')
    w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    w.setModal(True)  # set blocking

    def set_card_info_procedure_factory(name, text_box):
        def act():
            card_info[name] = text_box.toPlainText()
        return act

    def create_text_changed_event_handler(_k, _box, _w):
        def update_design():
            card_info[_k] = _box.toPlainText()
            joker.show_img(template.generate_image(card_info), wait=False)

        return update_design

    offset = 0
    for k in fields_to_query:
        # generate gui
        label = QLabel(k + ":", w)
        label.move(20, 80*offset)
        textbox = QPlainTextEdit(w)
        textbox.insertPlainText(card_info[k])
        textbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        textbox.resize(280, 40)
        textbox.move(20, 80*offset + 20)
        textbox.textChanged.connect(create_text_changed_event_handler(k, textbox, w))
        offset += 1
        actions.append(set_card_info_procedure_factory(k, textbox))

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
    card_img = template.generate_image(card_info)
    joker.show_img(card_img, wait=False)
    w.show()
    app.exec_()
    del card_info[KEY_IMG]
    return card_info, card_img
