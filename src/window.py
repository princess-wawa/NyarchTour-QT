# window.py
#
# Copyright 2023 Francesco Caracciolo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QToolButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6 import uic
import os
import subprocess
from pages import PAGES

# main nyarch linux class
class NyarchtourWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("window.ui", self) # load the main ui file
        self.galleryLayout.setSpacing(0)
        self.galleryLayout.setContentsMargins(0, 0, 0, 0)

        # initialize the carrousel to empty 
        self.current_index = 0
        self.pages_labels = []
        self.dots = []
        self.pages = []

        # connect the buttons
        self.connect_signals()
        self.add_all_pages()
        
        QTimer.singleShot(0, self._resize_pages)
        
        # if we ever have lag, we won't be able to update in time, so we need to update just after the lag spikes if the windows are ever resized during the lag
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(100)  # set the timer
        self._resize_timer.timeout.connect(self._resize_pages)
            

    def connect_signals(self):
        self.leftButton.clicked.connect(self.go_previous)
        self.rightButton.clicked.connect(self.go_next)
        
    def add_page(self, title="", description="", image_path=None, buttons=None):
        page = CarouselPage(self)

        page.set_title(title)
        page.set_description(description)

        if image_path:
            page.set_image(image_path)

        if buttons:
            for btn in buttons:
                page.add_button(btn["label"], btn["command"])


        self.galleryLayout.addWidget(page)
        self.pages.append(page)
        self.add_dot()

        return page

    def add_all_pages(self):
        for e in PAGES:
            page = self.add_page(e["title"], e["body"], f"pictures/{e["icon"]}.png", e["buttons"])
            page.update_image()
            self._resize_pages()
            
    def add_dot(self):
        dot = QPushButton()
        dot.setCheckable(True)
        dot.setAutoExclusive(True)
        dot.setFixedSize(12, 12)
        dot.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                background-color: gray;
                border: none;
            }
            QPushButton:checked {
                background-color: black;
            }
        """)

        index = len(self.dots)
        dot.clicked.connect(lambda _, i=index: self.go_to(i))

        self.dotLayout.addWidget(dot)
        self.dots.append(dot)

        if len(self.dots) == 1:
            dot.setChecked(True)
            
    def go_next(self):
        if not self.pages:
            return
        self.go_to((self.current_index + 1) % len(self.pages))

    def go_previous(self):
        if not self.pages:
            return
        self.go_to((self.current_index - 1) % len(self.pages))

    def go_to(self, index):
        self.current_index = index
        self.scroll_to_current()
        self.dots[self.current_index].setChecked(True)        
    
    def scroll_to_current(self, animation=True):
        if not self.pages:
            return

        page_width = self.scrollArea.viewport().width()  # use viewport, not page.width()
        target = self.current_index * page_width

        scroll_bar = self.scrollArea.horizontalScrollBar()
        self.animation = QPropertyAnimation(scroll_bar, b"value")
        if animation:
            self.animation.setDuration(300)
        else: 
            self.animation.setDuration(0)
           
        self.animation.setStartValue(scroll_bar.value())
        self.animation.setEndValue(target)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_pages() 
        self.scroll_to_current(animation=False)
        self._resize_timer.start()

    def _resize_pages(self):
        viewport_width = self.scrollArea.viewport().width()
        viewport_height = self.scrollArea.viewport().height()
        for page in self.pages:
            page.setFixedSize(viewport_width, viewport_height)

# carroussel page
class CarouselPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("carousel_page.ui", self) # load the carroussel page file

    def set_image(self, path: str):
        self._pixmap = QPixmap(path)  # save original, don't scale yet
        self.update_image()

    def update_image(self):
        if self._pixmap is None:
            return
        scaled = self._pixmap.scaled(
            self.imageLabel.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.imageLabel.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()

    def set_title(self, text: str):
        self.titleLabel.setText(text)

    def set_description(self, text: str):
        self.descriptionLabel.setText(text)

    def add_button(self, title: str, command):
        btn = QToolButton()
        btn.setText(title)
        btn.clicked.connect(lambda: subprocess.run(command, shell=True))
                
        self.horizontalLayout.addWidget(btn)
        
