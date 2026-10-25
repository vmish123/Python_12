import os
import sys
import shutil
import time

def get_bundled_path(relative_path: str) -> str:
    """Возвращает путь к файлам, вшитым внутрь .exe."""
    if getattr(sys, 'frozen', False):
        # Если запущено как скомпилированный .exe
        base_path = sys._MEIPASS
    else:
        # Если запущено из IDE
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_user_data_path(relative_path: str) -> str:
    """Возвращает путь к папке рядом с .exe файлом."""
    if getattr(sys, 'frozen', False):
        # Путь к папке, где физически лежит .exe файл
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Путь к картинке по умолчанию
DEFAULT_COVER = get_bundled_path(os.path.join("assets", "default_cover.png"))

# Путь к папке, куда будут сохраняться новые обложки
IMAGES_DIR = get_user_data_path(os.path.join("assets", "images"))

def ensure_assets_exist() -> None:
    """Создает папки для новых картинок рядом с программой."""
    os.makedirs(IMAGES_DIR, exist_ok=True)

def save_book_cover(source_path: str) -> str:
    """
    Копирование выбранного изображения в папку приложения под уникальным именем.

    :param source_path: Абсолютный или относительный путь к исходному файлу.
    :return: Относительный путь к сохраненной копии.
    """
    if not source_path or not os.path.exists(source_path):
        return ""

    # Извлечение расширения файла
    _, ext = os.path.splitext(source_path)

    # Генерация уникального имени на основе текущего времени
    unique_filename = f"cover_{int(time.time())}{ext}"

    # Формирование итогового пути
    destination_path = os.path.join(IMAGES_DIR, unique_filename).replace("\\", "/")

    # Копирование файла в папку приложения
    shutil.copy(source_path, destination_path)

    return destination_path


def get_cover_path(db_image_path: str) -> str:
    """Возвращает безопасный путь к обложке для отображения в интерфейсе."""
    if db_image_path and os.path.exists(db_image_path):
        return db_image_path

    return DEFAULT_COVER
