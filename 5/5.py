import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore

from ui_5 import Ui_Form


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller распаковывает данные во временную папку sys._MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # При обычном запуске поиск в текущей директории
    return os.path.join(os.path.abspath("."), relative_path)


class UFOControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация пользовательского интерфейса
        self.ui = Ui_Form()
        self.ui.setupUi(self)


        # Установка фокуса на главное окно для перехвата нажатий клавиатуры
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        # Настройка шага перемещения НЛО
        self.step = 20

        self.prepare_pixmap()

        # Вычисление стартовых координат
        self.ufo_x = (self.width() - self.ufo_w) // 2
        self.ufo_y = (self.height() - self.ufo_h) // 2

    def prepare_pixmap(self):
        # Правильный путь к картинке
        image_path = resource_path('ufo.png')

        # Загрузка исходного изображения
        image = QtGui.QImage(image_path)
        image = image.convertToFormat(QtGui.QImage.Format.Format_ARGB32)

        # Удаление светлого фона
        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                if color.alpha() > 0 and color.red() > 240 and color.green() > 240 and color.blue() > 240:
                    image.setPixelColor(x, y, QtGui.QColor(0, 0, 0, 0))

        original_pixmap = QtGui.QPixmap.fromImage(image)

        # Уменьшение размера картинки и сохранение её в памяти
        self.ufo_pixmap = original_pixmap.scaled(
            80, 80,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )

        self.ufo_w = self.ufo_pixmap.width()
        self.ufo_h = self.ufo_pixmap.height()

    def keyPressEvent(self, event):
        # Изменение координат в зависимости от нажатой стрелки
        if event.key() == QtCore.Qt.Key.Key_Left:
            self.ufo_x -= self.step
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.ufo_x += self.step
        elif event.key() == QtCore.Qt.Key.Key_Up:
            self.ufo_y -= self.step
        elif event.key() == QtCore.Qt.Key.Key_Down:
            self.ufo_y += self.step
        else:
            super().keyPressEvent(event)
            return

        # Кольцевая математика удерживает координаты внутри окна
        self.ufo_x %= self.width()
        self.ufo_y %= self.height()

        # Вызов принудительной перерисовки окна
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        win_w = self.width()
        win_h = self.height()

        # Отрисовка основной НЛО
        painter.drawPixmap(self.ufo_x, self.ufo_y, self.ufo_pixmap)

        # Отрисовка фантома по горизонтали
        if self.ufo_x > win_w - self.ufo_w:
            painter.drawPixmap(self.ufo_x - win_w, self.ufo_y, self.ufo_pixmap)

        # Отрисовка фантома по вертикали
        if self.ufo_y > win_h - self.ufo_h:
            painter.drawPixmap(self.ufo_x, self.ufo_y - win_h, self.ufo_pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UFOControl()
    window.show()
    sys.exit(app.exec())
