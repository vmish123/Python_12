from PyQt6.QtWidgets import QWidget, QPushButton, QMessageBox, QLineEdit
from PyQt6.QtCore import pyqtSignal

from ui import Ui_AuthWindow


class AuthController(QWidget, Ui_AuthWindow):
    """Контроллер окна авторизации и регистрации."""

    # Сигнал об успешной авторизации. Передает логин пользователя.
    auth_successful = pyqtSignal(str)

    def __init__(self, db_manager):
        super().__init__()
        self.setupUi(self)
        self.db = db_manager

        self.password_line.returnPressed.connect(self.btn_login.click)
        # Скрытие вводимого пароля
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)

        # Добавление кнопки регистрации
        self.btn_register = QPushButton("Регистрация")
        self.horizontalLayout.insertWidget(1, self.btn_register)

        # Подключение кнопок к методам обработки
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.handle_register)
        self.btn_exit.clicked.connect(self.close)

    def handle_login(self):
        """Обработка нажатия на кнопку 'Войти'."""
        username = self.login_line.text().strip()
        password = self.password_line.text().strip()

        # Проверка на пустые поля
        if not username or not password:
            self.label_3.setText("Введите логин и пароль.")
            return

        # Вызов метода авторизации из базы данных
        if self.db.authenticate_user(username, password):
            self.label_3.setText("Авторизация успешна.")
            # Отправка сигнала в главный файл для смены окон
            self.auth_successful.emit(username)
            self.close()
        else:
            self.label_3.setText("Неверный логин или пароль.")

    def handle_register(self):
        """Обработка нажатия на кнопку 'Регистрация'."""
        username = self.login_line.text().strip()
        password = self.password_line.text().strip()

        # Проверка на пустые поля
        if not username or not password:
            self.label_3.setText("Введите логин и пароль.")
            return

        # Вызов метода регистрации из базы данных
        if self.db.register_user(username, password):
            self.label_3.setText("Регистрация успешна. Вы не авторизованы в системе.")

            # Вывод сообщения об успехе на экран в виде всплывающего окна
            QMessageBox.information(
                self,
                "Регистрация",
                "Вы успешно зарегистрированы.\nИспользуйте свои данные для входа."
            )

            # Очистка поля пароля для удобства
            self.password_line.clear()
        else:
            # Если db_manager вернул False (ошибка уникальности)
            self.label_3.setText("Пользователь уже существует.")
