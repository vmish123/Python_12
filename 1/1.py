import sys
import csv
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QWidget

from ui_1 import Ui_Form


class OlympiadResults(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Результаты олимпиады")

        # Инициализация пользовательского интерфейса
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.all_data = []

        # Загрузка данных и настройка элементов управления
        self.load_data()
        self.setup_ui()
        self.update_table()

    def load_data(self):
        # Чтение данных из файла CSV
        try:
            with open('rez.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    login = row.get('login', '')
                    # Извлечение номера школы и класса из логина
                    parts = login.split('-')
                    if len(parts) >= 4:
                        school = parts[2]
                        grade = parts[3]
                    else:
                        school, grade = "Неизвестно", "Неизвестно"

                    try:
                        score = int(row.get('Score', 0))
                    except ValueError:
                        score = 0

                    self.all_data.append({
                        'login': login,
                        'name': row.get('user_name', ''),
                        'score': score,
                        'school': school,
                        'grade': grade
                    })
        except FileNotFoundError:
            # Вывод сообщения об ошибке, если файл не найден
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Файл rez.csv не найден.")
            sys.exit(1)

    def setup_ui(self):
        # Получение уникальных списков школ и классов для фильтров
        schools = sorted(list(set(item['school'] for item in self.all_data)))
        grades = sorted(list(set(item['grade'] for item in self.all_data)))

        # Заполнение выпадающих списков
        self.ui.school_cb.addItem("Все")
        self.ui.school_cb.addItems(schools)

        self.ui.class_cb.addItem("Все")
        self.ui.class_cb.addItems(grades)

        # Подключение сигналов изменения фильтров к функции обновления таблицы
        self.ui.school_cb.currentIndexChanged.connect(self.update_table)
        self.ui.class_cb.currentIndexChanged.connect(self.update_table)

        # Настройка таблицы
        self.ui.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.tableView.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        # Создание и установка модели данных для таблицы
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Логин", "ФИО", "Суммарный балл"])
        self.ui.tableView.setModel(self.model)

        # Настройка растяжения столбцов таблицы
        header = self.ui.tableView.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def update_table(self):
        # Получение текущих значений фильтров
        selected_school = self.ui.school_cb.currentText()
        selected_grade = self.ui.class_cb.currentText()

        # Применение фильтров к данным
        filtered_data = []
        for item in self.all_data:
            match_school = (selected_school == "Все" or item['school'] == selected_school)
            match_grade = (selected_grade == "Все" or item['grade'] == selected_grade)

            if match_school and match_grade:
                filtered_data.append(item)

        # Определение уникальных баллов для вычисления призовых мест
        unique_scores = sorted(list(set(item['score'] for item in filtered_data)), reverse=True)

        top_scores = []
        # Сохранение баллов за 1, 2 и 3 место
        for i in range(min(3, len(unique_scores))):
            top_scores.append(unique_scores[i])

        # Очистка таблицы перед новым заполнением
        self.model.removeRows(0, self.model.rowCount())

        # Вывод отфильтрованных данных на экран
        for data_row in filtered_data:
            login_item = QtGui.QStandardItem(data_row['login'])
            name_item = QtGui.QStandardItem(data_row['name'])
            score_item = QtGui.QStandardItem(str(data_row['score']))

            row_items = [login_item, name_item, score_item]

            # Раскраска строк в зависимости от занятого места
            if data_row['score'] in top_scores:
                place = top_scores.index(data_row['score']) + 1

                if place == 1:
                    color = QtGui.QColor(255, 215, 0)  # Золотой (1 место)
                elif place == 2:
                    color = QtGui.QColor(220, 220, 220)  # Серебряный (2 место)
                else:
                    color = QtGui.QColor(205, 127, 50)  # Бронзовый (3 место)

                for item in row_items:
                    item.setBackground(color)

            for item in row_items:
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)

            self.model.appendRow(row_items)

        self.ui.tableView.resizeColumnsToContents()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OlympiadResults()
    window.show()
    sys.exit(app.exec())
