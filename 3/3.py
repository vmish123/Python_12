import sys
import random
from PyQt6 import QtWidgets, QtGui, QtCore

from ui_3 import Ui_Form


class ShapeCanvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Установка фокуса на окно для перехвата событий клавиатуры
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        # Список для хранения всех видимых в данный момент фигур
        self.shapes = []

        # Задание времени жизни фигуры на экране
        self.display_time = 3000

    def add_shape(self, shape_type, pos):
        # Генерация случайных параметров для новой фигуры
        size = random.randint(30, 150)
        color = QtGui.QColor(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

        # Создание словаря с параметрами фигуры
        shape_data = {
            'type': shape_type,
            'x': pos.x(),
            'y': pos.y(),
            'size': size,
            'color': color
        }

        # Добавление фигуры в список и вызов перерисовки
        self.shapes.append(shape_data)
        self.update()

        # Запуск одноразового таймера для удаления именно этой фигуры в будущем
        QtCore.QTimer.singleShot(self.display_time, self.remove_oldest_shape)

    def remove_oldest_shape(self):
        # Удаление самой старой фигуры по срабатыванию таймера
        if self.shapes:
            self.shapes.pop(0)
            self.update()

    def mousePressEvent(self, event):
        # Перехват кликов мыши и добавление соответствующих фигур
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.add_shape('circle', event.pos())

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.add_shape('square', event.pos())

    def keyPressEvent(self, event):
        # Перехват нажатия пробела
        if event.key() == QtCore.Qt.Key.Key_Space:
            # Получение координат курсора на экране и перевод их в координаты окна
            global_pos = QtGui.QCursor.pos()
            local_pos = self.mapFromGlobal(global_pos)

            self.add_shape('triangle', local_pos)

    def paintEvent(self, event):
        # Настройка инструмента рисования
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)

        # Отрисовка всех фигур из списка на экране
        for shape in self.shapes:
            painter.setBrush(shape['color'])

            x = shape['x']
            y = shape['y']
            size = shape['size']
            half_size = size // 2

            if shape['type'] == 'circle':
                painter.drawEllipse(x - half_size, y - half_size, size, size)

            elif shape['type'] == 'square':
                painter.drawRect(x - half_size, y - half_size, size, size)

            elif shape['type'] == 'triangle':
                # Формирование треугольника по трем точкам
                polygon = QtGui.QPolygon([
                    QtCore.QPoint(x, y - half_size),  # Верх
                    QtCore.QPoint(x - half_size, y + half_size),  # Левый нижний угол
                    QtCore.QPoint(x + half_size, y + half_size)  # Правый нижний угол
                ])
                painter.drawPolygon(polygon)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ShapeCanvas()
    window.show()
    sys.exit(app.exec())
