import datetime

from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from ui import Ui_BookDialog
from utils import save_book_cover, get_cover_path


class BookController(QDialog, Ui_BookDialog):
    """
    Контроллер диалогового окна книги.
    Служит для ввода новых данных или редактирования существующих.
    """

    def __init__(self, book_data: dict = None):
        super().__init__()
        self.setupUi(self)

        # Ограничение длины вводимого текста
        self.book_name.setMaxLength(100)  # Название не длиннее 100 символов
        self.book_author.setMaxLength(50)  # Автор не длиннее 50 символов
        self.book_genre.setMaxLength(30)  # Жанр не длиннее 30 символов
        self.book_year.setMaxLength(4)  # Год не длиннее 4 символов

        # Переменные для хранения путей к картинке
        self.current_image_path = ""
        self.new_image_selected = False

        # Подключение кнопок к методам обработки
        self.btn_cover.clicked.connect(self.select_cover)
        self.btn_save.clicked.connect(self.validate_and_save)

        # Если переданы данные
        if book_data:
            self._fill_data(book_data)

    def _fill_data(self, data: dict):
        """Заполнение полей ввода существующими данными."""
        # Вывод текста в поля на экран
        self.book_name.setText(data.get('title', ''))
        self.book_author.setText(data.get('author', ''))
        self.book_year.setText(str(data.get('year', '')))
        self.book_genre.setText(data.get('genre', ''))

        # Вывод картинки на экран
        self.current_image_path = data.get('image_path', '')
        self._display_image(self.current_image_path)

    def select_cover(self):
        """Открытие диалога выбора файла и вывод выбранной картинки на экран."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите обложку",
            "",
            "Изображения (*.png *.jpg *.jpeg)"
        )

        # Если пользователь выбрал файл
        if file_path:
            self.current_image_path = file_path
            self.new_image_selected = True
            self._display_image(self.current_image_path)

    def _display_image(self, path: str):
        """Вывод изображения в виджет QLabel на экран."""
        # Получение пути к изображению
        actual_path = get_cover_path(path)

        pixmap = QPixmap(actual_path)

        # Масштабирование картинки под размер рамки
        pixmap = pixmap.scaled(
            self.label.width(), self.label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setPixmap(pixmap)

    def validate_and_save(self):
        """Проверка введенных данных перед закрытием окна."""
        title = self.book_name.text().strip()
        author = self.book_author.text().strip()
        year_text = self.book_year.text().strip()

        # Базовая проверка на пустоту обязательных полей
        if not title or not author:
            QMessageBox.warning(self, "Ошибка", "Необходимо указать название и автора.")
            return

        # Проверка года издания
        if year_text:
            try:
                year = int(year_text)
                current_year = datetime.datetime.now().year

                # Год не может быть отрицательным или из будущего
                if year < 0 or year > current_year:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        f"Год издания должен быть от 0 до {current_year}."
                    )
                    return
            except ValueError:
                # Если ввели буквы вместо цифр
                QMessageBox.warning(self, "Ошибка", "Год издания должен быть целым числом.")
                return

        self.accept()

    def get_data(self) -> dict:
        """
        Сбор данных из полей ввода для передачи в MainController.
        Если была выбрана новая картинка, копирует её в папку приложения.
        """
        # Если пользователь выбрал новую картинку с компьютера
        if self.new_image_selected:
            # Вызов функции копирования
            final_image_path = save_book_cover(self.current_image_path)
        else:
            final_image_path = self.current_image_path

        # Конвертация года в число
        year_text = self.book_year.text().strip()
        year = int(year_text) if year_text else 0

        # Возврат словаря с данными
        return {
            'title': self.book_name.text().strip(),
            'author': self.book_author.text().strip(),
            'year': year,
            'genre': self.book_genre.text().strip(),
            'image_path': final_image_path
        }
