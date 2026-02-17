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
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
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
            self.add_page(e["title"], e["body"], f"pictures/{e["icon"]}.png", e["buttons"])
            
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
    
    def scroll_to_current(self):
        if not self.pages:
            return

        page_width = self.scrollArea.viewport().width()  # use viewport, not page.width()
        target = self.current_index * page_width

        scroll_bar = self.scrollArea.horizontalScrollBar()
        self.animation = QPropertyAnimation(scroll_bar, b"value")
        self.animation.setDuration(300)
        self.animation.setStartValue(scroll_bar.value())
        self.animation.setEndValue(target)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_pages()

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
        self._update_image()

    def _update_image(self):
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
        self._update_image()

    def set_title(self, text: str):
        self.titleLabel.setText(text)

    def set_description(self, text: str):
        self.descriptionLabel.setText(text)

    def add_button(self, title: str, command):
        btn = QToolButton()
        btn.setText(title)
        btn.clicked.connect(lambda: subprocess.run(command, shell=True))
                
        self.horizontalLayout.addWidget(btn)
        
        
'''
class NyarchtourApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='moe.nyarchlinux.tour',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.create_action('quit', self.quit, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = NyarchtourWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='nyarchtour',
                                application_icon='moe.nyarchlinux.tour',
                                developer_name='Francesco Caracciolo',
                                version='0.4.5',
                                developers=['Francesco Caracciolo'],
                                copyright='© 2025 Francesco Caracciolo')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = NyarchtourApplication()
    return app.run(sys.argv)

from gi.repository import Adw
from gi.repository import Gtk
from .pages import PAGES
import subprocess
@Gtk.Template(resource_path='/moe/nyarchlinux/tour/window.ui')
class NyarchtourWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'NyarchtourWindow'

    carousel = Gtk.Template.Child("carousel")
    previous = Gtk.Template.Child("previous")
    nextbutton = Gtk.Template.Child("next")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.commands = {}
        self.current_page = 0
        for page in PAGES:
            if "condition" in page and not page["condition"]():
                continue
            p = self.generate_page(page)
            self.carousel.append(p)
        self.carousel.connect("page-changed", self.page_changes)
        self.nextbutton.connect("clicked", self.next_page)
        self.previous.connect("clicked", self.previous_page)
        self.connect("close-request", self.on_close_request)

    def on_close_request(self, window):
        if (self.current_page > 7):
            return False
        dialog = Adw.MessageDialog(
            transient_for=self,
            title="Confirm Exit",
            body="Nyarch Tour will guide you through all the Nyarch Linux features.\nAre you sure?",
            default_response="cancel",
            close_response="cancel",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("exit", "Exit")
        dialog.set_response_appearance("exit", Adw.ResponseAppearance.DESTRUCTIVE)
        def on_response(dialog, response):
            if response == "exit":
                window.destroy()  # Close the window if "Exit" is clicked
            dialog.destroy()  # Close the dialog

        dialog.connect("response", on_response)
        dialog.present()
        return True
    def page_changes(self, carousel, page):
        self.current_page = page
        if page > 0:
            self.previous.set_opacity(1)
        else:
            self.previous.set_opacity(0)
        if page >= self.carousel.get_n_pages()-1:
            self.nextbutton.set_opacity(0)
        else:
           self.nextbutton.set_opacity(1)
    def next_page(self, button):
        self.carousel.get_position()
        if self.carousel.get_position() < self.carousel.get_n_pages()-1:
            self.carousel.scroll_to(self.carousel.get_nth_page(self.carousel.get_position()+1), True)

    def previous_page(self, button):
        self.carousel.get_position()
        if self.carousel.get_position() > 0:
            self.carousel.scroll_to(self.carousel.get_nth_page(self.carousel.get_position()-1), True)

    def generate_page(self, page):
        builder = Gtk.Builder.new_from_resource("/moe/nyarchlinux/tour/carousel_page.ui")
        p = builder.get_object("page")
        titlelabel = builder.get_object("title")
        bodylabel = builder.get_object("body")
        gtkimage = builder.get_object("image")
        buttonsBox = builder.get_object("buttonsBox")
        for button in page['buttons']:
        	Gtkbutton = Gtk.Button()
        	button_content = Adw.ButtonContent()
        	# Set properties
        	if button["style"] is not None:
        		Gtkbutton.set_css_classes([button["style"]])
        	if button["icon"] is not None:
        		button_content.set_icon_name(button["icon"])
        		button_content.set_use_underline(True)
        		button_content.set_label(button["label"])
        		Gtkbutton.set_child(button_content)
        	else:
        		Gtkbutton.set_label(button["label"])
        	self.commands[Gtkbutton] = button["command"]
        	Gtkbutton.connect("clicked", self.button_clicked)
        	buttonsBox.append(Gtkbutton)

        titlelabel.set_label(page["title"])
        bodylabel.set_label(page["body"])
        gtkimage.set_resource("/moe/nyarchlinux/tour/pictures/" + page["icon"] + ".png")
        #gtkimage.set_pixel_size(page["icon-size"])
        return p

    def button_clicked(self, button):
        	self.background_process(self.commands[button])

    def background_process(self, command):
    	subprocess.Popen(["flatpak-spawn",  "--host"] + command.split())
    
'''