import sqlite3
import hashlib
import os
import sys


class DatabaseManager:
    """Класс для управления базой данных каталога библиотеки."""

    def __init__(self, db_name="library.db"):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(".")

        # Создание папки database рядом с программой
        db_folder = os.path.join(base_dir, "database")
        os.makedirs(db_folder, exist_ok=True)

        # Полный путь к файлу БД
        self.db_path = os.path.join(db_folder, db_name)

        # Файл БД будет занят процессом python до закрытия программы
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Другие программы не смогут получить доступ к БД, пока программа запущена
        self.conn.execute("PRAGMA locking_mode = EXCLUSIVE")

        self._init_db()

    def _init_db(self):
        """Создание таблиц в базе данных, если они не существуют."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                image_path TEXT
            )
        """)
        self.conn.commit()

    def close_connection(self):
        """Принудительное закрытие соединения."""
        if self.conn:
            self.conn.close()

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля с использованием SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        """Регистрация нового пользователя."""
        password_hash = self._hash_password(password)
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Откат транзакции при ошибке
            self.conn.rollback()
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        """Авторизация пользователя."""
        password_hash = self._hash_password(password)
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        return bool(user)

    def get_books(self, search_by: str = None, query: str = "") -> list:
        """Получение списка книг с возможностью фильтрации."""
        cursor = self.conn.cursor()

        # Если строка поиска не пустая
        if query:
            if search_by == "По автору":
                sql = "SELECT * FROM books WHERE author LIKE ?"
                cursor.execute(sql, (f"%{query}%",))
            elif search_by == "По названию":
                sql = "SELECT * FROM books WHERE title LIKE ?"
                cursor.execute(sql, (f"%{query}%",))
            else:
                # Поиск "Все" (вхождение текста и в название, и в автора)
                sql = "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?"
                cursor.execute(sql, (f"%{query}%", f"%{query}%"))
        else:
            # Если строка поиска пустая
            sql = "SELECT * FROM books"
            cursor.execute(sql)

        return [dict(row) for row in cursor.fetchall()]

    def add_book(self, title: str, author: str, year: int, genre: str, image_path: str) -> None:
        """Добавление новой книги."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, year, genre, image_path)
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, year, genre, image_path))
        self.conn.commit()

    def update_book(self, book_id: int, title: str, author: str, year: int, genre: str, image_path: str) -> None:
        """Обновление данных книги."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE books 
            SET title = ?, author = ?, year = ?, genre = ?, image_path = ?
            WHERE id = ?
        """, (title, author, year, genre, image_path, book_id))
        self.conn.commit()

    def delete_book(self, book_id: int) -> None:
        """Удаление книги."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()
