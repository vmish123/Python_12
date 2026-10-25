import sys
import sqlite3
import datetime
from PyQt6 import QtWidgets, QtGui, QtCore

from ui_2 import Ui_Form as Ui_MainWindow
from dialog_ui import Ui_Form as Ui_DialogForm


class FilmDialog(QtWidgets.QDialog):
    def __init__(self, film_id=None, parent=None):
        super().__init__(parent)

        # Инициализация интерфейса диалога
        self.ui = Ui_DialogForm()
        self.ui.setupUi(self)
        self.film_id = film_id

        # Настройка ограничений для числовых полей
        self.ui.spinBox.setRange(1895, 2100)  # Год выпуска
        self.ui.spinBox_2.setRange(1, 1000)  # Продолжительность

        # Добавление кнопок "ОК" и "Отмена" в макет
        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.ui.verticalLayout.addWidget(self.button_box)

        # Подключение сигналов кнопок
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        self.load_genres()

        # Проверка режима (добавление или редактирование)
        if self.film_id is not None:
            self.setWindowTitle("Редактирование фильма")
            self.load_film_data()
        else:
            self.setWindowTitle("Добавление фильма")
            self.ui.spinBox.setValue(datetime.date.today().year)

    def load_genres(self):
        # Загрузка жанров из БД в выпадающий список
        con = sqlite3.connect('films_db.sqlite')
        cur = con.cursor()
        cur.execute("SELECT id, title FROM genres")
        genres = cur.fetchall()
        con.close()

        for genre_id, title in genres:
            self.ui.comboBox.addItem(title, userData=genre_id)

    def load_film_data(self):
        # Получение данных фильма для редактирования
        con = sqlite3.connect('films_db.sqlite')
        cur = con.cursor()
        cur.execute("SELECT title, year, genre, duration FROM films WHERE id = ?", (self.film_id,))
        film = cur.fetchone()
        con.close()

        if film:
            self.ui.lineEdit.setText(film[0])
            self.ui.spinBox.setValue(film[1])
            self.ui.spinBox_2.setValue(film[3])

            genre_id = film[2]
            index = self.ui.comboBox.findData(genre_id)
            if index >= 0:
                self.ui.comboBox.setCurrentIndex(index)

    def validate_and_accept(self):
        # Проверка пользовательского ввода перед сохранением
        title = self.ui.lineEdit.text().strip()
        year = self.ui.spinBox.value()
        duration = self.ui.spinBox_2.value()
        current_year = datetime.date.today().year

        if not title:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Название фильма не может быть пустым.")
            return

        if year > current_year:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Год выпуска не может быть в будущем.")
            return

        if duration <= 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Продолжительность должна быть больше нуля.")
            return

        self.accept()

    def get_data(self):
        # Возврат введенных данных в виде словаря
        return {
            'title': self.ui.lineEdit.text().strip(),
            'year': self.ui.spinBox.value(),
            'genre': self.ui.comboBox.currentData(),
            'duration': self.ui.spinBox_2.value()
        }


class FilmsDatabaseApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Настройка таблицы 
        self.ui.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Запрет изменения высоты строк пользователем
        self.ui.tableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        # Отключение вертикального заголовка (дублирующейся нумерации строк)
        self.ui.tableView.verticalHeader().setVisible(False)

        # Создание модели для таблицы
        self.model = QtGui.QStandardItemModel()
        self.ui.tableView.setModel(self.model)

        # Подключение сигналов кнопок главного окна
        self.ui.pushButton.clicked.connect(self.add_film)
        self.ui.pushButton_2.clicked.connect(self.edit_film)
        self.ui.pushButton_3.clicked.connect(self.delete_film)

        self.load_table_data()

    def load_table_data(self):
        # Очистка текущей модели
        self.model.clear()

        con = sqlite3.connect('films_db.sqlite')
        cur = con.cursor()

        # Запрос с извлечением оригинальных названий полей
        query = """
            SELECT films.id, 
                   films.title, 
                   films.year, 
                   genres.title AS genre, 
                   films.duration
            FROM films 
            JOIN genres ON films.genre = genres.id
        """
        cur.execute(query)
        data = cur.fetchall()

        # Извлечение названий столбцов непосредственно из параметров курсора БД
        headers = [description[0] for description in cur.description]
        self.model.setHorizontalHeaderLabels(headers)

        con.close()

        # Заполнение таблицы данными
        for row_data in data:
            row_items = [QtGui.QStandardItem(str(item)) for item in row_data]
            self.model.appendRow(row_items)

        # Настройка ширины столбцов
        header = self.ui.tableView.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.ui.tableView.setColumnWidth(0, 60)

        # Title растягивается
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # Остальные поля подстраиваются под ширину контента
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def get_selected_film_id(self):
        # Возвращение ID выделенного фильма из первого столбца
        selection = self.ui.tableView.selectionModel()
        if not selection.hasSelection():
            return None

        selected_row = selection.selectedRows()[0].row()
        film_id_item = self.model.item(selected_row, 0)
        return int(film_id_item.text())

    def add_film(self):
        # Вызов диалога и добавление записи в БД
        dialog = FilmDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()

            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute(
                "INSERT INTO films (title, year, genre, duration) VALUES (?, ?, ?, ?)",
                (data['title'], data['year'], data['genre'], data['duration'])
            )
            con.commit()
            con.close()

            self.load_table_data()

    def edit_film(self):
        # Вызов диалога редактирования
        film_id = self.get_selected_film_id()
        if film_id is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования.")
            return

        dialog = FilmDialog(film_id=film_id, parent=self)
        if dialog.exec():
            data = dialog.get_data()

            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute(
                "UPDATE films SET title = ?, year = ?, genre = ?, duration = ? WHERE id = ?",
                (data['title'], data['year'], data['genre'], data['duration'], film_id)
            )
            con.commit()
            con.close()

            self.load_table_data()

    def delete_film(self):
        # Подтверждение и удаление выделенной записи
        film_id = self.get_selected_film_id()
        if film_id is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return

        reply = QtWidgets.QMessageBox.question(
            self, 'Подтверждение', 'Вы действительно хотите удалить выбранный фильм?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            con = sqlite3.connect('films_db.sqlite')
            cur = con.cursor()
            cur.execute("DELETE FROM films WHERE id = ?", (film_id,))
            con.commit()
            con.close()

            self.load_table_data()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FilmsDatabaseApp()
    window.show()
    sys.exit(app.exec())