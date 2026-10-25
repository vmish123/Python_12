import sys
import random
from PyQt6 import QtWidgets, QtCore, QtGui

from ui_4 import Ui_Form


class RunawayButton(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Включение отслеживания курсора
        self.setMouseTracking(True)

        self.ui.pushButton.installEventFilter(self)

    def mouseMoveEvent(self, event):
        # Получение текущей позиции мыши и геометрии кнопки
        mouse_pos = event.pos()
        btn_rect = self.ui.pushButton.geometry()

        # Создание невидимой опасной зоны
        danger_zone = btn_rect.adjusted(-20, -20, 20, 20)

        # Перемещение кнопки, если курсор попал в опасную зону
        if danger_zone.contains(mouse_pos):
            self.teleport_button()

        super().mouseMoveEvent(event)

    def eventFilter(self, obj, event):
        # Отлов события наведения на кнопку, если мышь двигалась быстрее обработчика mouseMoveEvent
        if obj == self.ui.pushButton and event.type() == QtCore.QEvent.Type.Enter:
            self.teleport_button()
            return True

        return super().eventFilter(obj, event)

    def teleport_button(self):
        # Получение размеров кнопки
        btn_w = self.ui.pushButton.width()
        btn_h = self.ui.pushButton.height()

        # Определение максимальных координат, чтобы кнопка не ушла за края формы
        max_x = self.width() - btn_w
        max_y = self.height() - btn_h

        # Защита от слишком маленького размера окна
        if max_x <= 0 or max_y <= 0:
            return

        # Получение текущей позиции курсора в координатах окна
        mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())

        # Генерация новых координат с проверкой, чтобы кнопка не появилась прямо под курсором
        attempts = 0
        while attempts < 100:
            new_x = random.randint(0, max_x)
            new_y = random.randint(0, max_y)

            new_rect = QtCore.QRect(new_x, new_y, btn_w, btn_h)
            new_danger_zone = new_rect.adjusted(-30, -30, 30, 30)

            if not new_danger_zone.contains(mouse_pos):
                self.ui.pushButton.move(new_x, new_y)
                break

            attempts += 1

    def resizeEvent(self, event):
        # Возврат кнопки в пределы окна, если пользователь резко уменьшил размер формы
        btn_rect = self.ui.pushButton.geometry()

        max_x = self.width() - btn_rect.width()
        max_y = self.height() - btn_rect.height()

        new_x = min(btn_rect.x(), max_x)
        new_y = min(btn_rect.y(), max_y)

        # Защита от отрицательных координат
        new_x = max(0, new_x)
        new_y = max(0, new_y)

        self.ui.pushButton.move(new_x, new_y)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RunawayButton()
    window.show()
    sys.exit(app.exec())
