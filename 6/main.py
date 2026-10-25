import sys
from PyQt6.QtWidgets import QApplication

from database import DatabaseManager
from utils import ensure_assets_exist
from controllers import AuthController, MainController


def main():
    # Создание папок и заглушек, если их нет
    ensure_assets_exist()

    app = QApplication(sys.argv)

    db = DatabaseManager()

    # Инициализация окна авторизации
    auth_window = AuthController(db)

    # Переменная для хранения ссылки на главное окно.
    main_window = None

    # Функция-обработчик входа
    def on_auth_success(username: str):
        nonlocal main_window

        main_window = MainController(db, username)

        main_window.show()

    # Подключение сигнала авторизации к функции-обработчику
    auth_window.auth_successful.connect(on_auth_success)

    # Вывод окна авторизации на экран и запуск приложения
    auth_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
