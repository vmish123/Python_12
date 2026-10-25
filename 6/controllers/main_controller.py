from PyQt6.QtWidgets import (QMainWindow, QMessageBox, QAbstractItemView, QHeaderView)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PyQt6.QtCore import Qt

from ui import Ui_MainWindow
from utils import get_cover_path
from .book_controller import BookController


class MainController(QMainWindow, Ui_MainWindow):
    """
    Контроллер главного окна приложения.
    Отвечает за вывод списка книг, поиск и управление записями.
    """

    def __init__(self, db_manager, username: str):
        super().__init__()
        self.setupUi(self)

        self.db = db_manager

        # Вывод имени авторизованного пользователя на экран
        self.user_name.setText(username)

        # Инициализация выпадающего списка для поиска
        self.search_selection.addItems(["Все", "По автору", "По названию"])
        self.search_line.returnPressed.connect(self.search_btn.click)

        self._setup_table()
        self._connect_signals()

        # Первичная загрузка данных в таблицу при открытии окна
        self.load_data()

    def _setup_table(self):
        """Настройка внешнего вида и поведения таблицы."""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(
            ["ID", "Название", "Автор", "Год", "Жанр", "Путь_Картинки"]
        )
        self.tableView.setModel(self.model)

        # Скрытие технических колонок
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(5, True)

        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self.tableView.horizontalHeader()

        # Запрет ручного изменения размеров столбцов пользователем для всех колонок
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # Установка фиксированной ширины для автора, года и жанра
        self.tableView.setColumnWidth(2, 160)  # Автор
        self.tableView.setColumnWidth(3, 60)  # Год
        self.tableView.setColumnWidth(4, 120)  # Жанр

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def _connect_signals(self):
        """Подключение кнопок и событий к методам обработки."""
        self.search_btn.clicked.connect(self.load_data)
        self.tableView.clicked.connect(self.show_book_details)

        # Кнопки из верхнего меню
        self.add_btn.triggered.connect(self.add_book)
        self.edit_btn.triggered.connect(self.edit_book)
        self.delete_btn.triggered.connect(self.delete_book)

    def load_data(self):
        """Чтение данных из БД и вывод их в таблицу на экран."""
        # Очистка таблицы перед новой загрузкой
        self._clear_details_panel()
        self.model.removeRows(0, self.model.rowCount())

        search_by = self.search_selection.currentText()
        query = self.search_line.text().strip()

        # Получение отфильтрованных данных из базы
        books = self.db.get_books(search_by=search_by, query=query)

        # Заполнение модели данными
        for book in books:
            row = [
                QStandardItem(str(book['id'])),
                QStandardItem(book['title']),
                QStandardItem(book['author']),
                QStandardItem(str(book['year'])),
                QStandardItem(book['genre']),
                QStandardItem(book['image_path'] or "")
            ]
            self.model.appendRow(row)

    def show_book_details(self, index):
        """Вывод детальной информации о книге на панель."""
        row = index.row()

        # Извлечение данных из выбранной строки таблицы
        title = self.model.item(row, 1).text()
        author = self.model.item(row, 2).text()
        year = self.model.item(row, 3).text()
        genre = self.model.item(row, 4).text()
        db_image_path = self.model.item(row, 5).text()

        # Вывод текста в поля "только для чтения"
        self.book_name.setText(title)
        self.book_author.setText(author)
        self.book_year.setText(year)
        self.book_genre.setText(genre)

        # Вывод картинки на экран
        actual_path = get_cover_path(db_image_path)
        pixmap = QPixmap(actual_path)

        # Масштабирование картинки под размер виджета без искажения пропорций
        pixmap = pixmap.scaled(
            self.cover.width(), self.cover.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.cover.setPixmap(pixmap)

    def add_book(self):
        """Обработка нажатия на 'Добавить книгу'."""
        dialog = BookController()

        # Если пользователь нажал "Сохранить" в диалоговом окне
        if dialog.exec():
            data = dialog.get_data()
            self.db.add_book(
                data['title'],
                data['author'],
                data['year'],
                data['genre'],
                data['image_path']
            )
            # Обновление таблицы на экране
            self.load_data()

    def edit_book(self):
        """Обработка нажатия на 'Изменить книгу'."""
        selected = self.tableView.selectionModel().selectedRows()

        if not selected:
            QMessageBox.warning(self, "Внимание", "Сначала выберите книгу в таблице.")
            return

        row = selected[0].row()
        book_id = int(self.model.item(row, 0).text())

        # Сбор текущих данных для передачи в окно редактирования
        current_data = {
            'title': self.model.item(row, 1).text(),
            'author': self.model.item(row, 2).text(),
            'year': int(self.model.item(row, 3).text()),
            'genre': self.model.item(row, 4).text(),
            'image_path': self.model.item(row, 5).text()
        }

        dialog = BookController(current_data)

        # Если пользователь нажал "Сохранить" после изменения
        if dialog.exec():
            data = dialog.get_data()
            self.db.update_book(
                book_id,
                data['title'],
                data['author'],
                data['year'],
                data['genre'],
                data['image_path']
            )
            self.load_data()

    def delete_book(self):
        """Обработка нажатия на 'Удалить книгу'."""
        selected = self.tableView.selectionModel().selectedRows()

        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите книгу для удаления.")
            return

        # Запрос подтверждения у пользователя
        reply = QMessageBox.question(
            self, 'Внимание', 'Вы уверены, что хотите удалить выбранную книгу?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            book_id = int(self.model.item(row, 0).text())
            self.db.delete_book(book_id)
            # Обновление вывода на экран после удаления
            self.load_data()

    def closeEvent(self, event):
        """
        Перехват события закрытия окна на крестик.
        Необходимо для безопасного отключения от базы данных.
        """
        self.db.close_connection()
        event.accept()

    def _clear_details_panel(self):
        """Очищает текстовые поля и картинку в боковой панели."""
        self.book_name.clear()
        self.book_author.clear()
        self.book_year.clear()
        self.book_genre.clear()
        self.cover.clear()
