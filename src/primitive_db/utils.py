# src/primitive_db/utils.py

# Для вспомогательных функций (например, работа с файлами).

import json


def load_metadata(filepath: str) -> dict:
    '''Загружает данные из JSON-файла. 
    Если файл не найден, возвращает пустой словарь {}. 
    Используйте try...except FileNotFoundError.'''

    """
    Загружает метаданные из JSON-файла.
    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}. Создан пустой файл.")
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    '''Сохраняет переданные данные в JSON-файл.'''

    """
    Сохраняет метаданные в JSON-файл.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)