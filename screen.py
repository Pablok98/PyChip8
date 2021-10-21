import sys

from PyQt5.QtWidgets import QMainWindow, QDockWidget, QWidget, QLineEdit, QPushButton, QLabel, QDesktopWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal, QTimer, QObject, Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QPixmap


class Screen(QMainWindow):
    key_signal = pyqtSignal(list)
    key_press_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 640, 320)
        self.screen = [0 for _ in range(64 * 32)]
        self.label = QLabel(self)
        canvas = QPixmap(640, 320)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.painter_pen = QPen()
        self.painter_pen.setWidth(10)

        self.pressed_keys = []

        self.show()

    def render_screen(self):
        painter = QPainter(self.label.pixmap())
        y = 0
        for i, point in enumerate(self.screen):
            pen = QPen()
            pen.setWidth(10)
            if point == 0:
                pen.setColor(QColor('black'))
            else:
                pen.setColor(QColor('white'))
            painter.setPen(pen)
            painter.drawPoint((i - y*64)*10, y*10)
            if (i + 1) % 64 == 0:
                y += 1
        painter.end()
        self.update()

    def keyPressEvent(self, event):
        key_ = event.text().lower()
        if key_ not in self.pressed_keys:
            self.pressed_keys.append(key_)
            self.key_signal.emit(self.pressed_keys)
            self.key_press_signal.emit(key_)

    def keyReleaseEvent(self, event):
        key_ = event.text().lower()
        if key_ in self.pressed_keys:
            self.pressed_keys.remove(key_)
            self.key_signal.emit(self.pressed_keys)


if __name__ == "__main__":
    app = QApplication([])
    win = Screen()
    sys.exit(app.exec())