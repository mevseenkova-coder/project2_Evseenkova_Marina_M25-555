# src/primitive_db/utils.py

import json
from pathlib import Path

# Пути
DATA_DIR = Path(__file__).parent / "data"
METADATA_FILE = Path(__file__).parent / "metadata.json"  # ← добавили

def ensure_data_dir():
    """Создаёт папку data, если её ещё нет"""
    DATA_DIR.mkdir(exist_ok=True)

def load_table_data(table_name):
    """Загружает данные таблицы из файла data/<table_name>.json"""
    ensure_data_dir()
    file_path = DATA_DIR / f"{table_name}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_table_data(table_name, data):
    """Сохраняет данные таблицы в файл data/<table_name>.json"""
    ensure_data_dir()
    file_path = DATA_DIR / f"{table_name}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_metadata(filepath=None):
    """
    Загружает метаданные из JSON-файла.
    Если filepath не указан — использует metadata.json в папке модуля.
    Если файла нет — возвращает пустой словарь.
    """
    if filepath is None:
        filepath = METADATA_FILE

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Убедимся, что структура правильная
            if "tables" not in data:
                data["tables"] = {}
            return data
    except FileNotFoundError:
        return {"tables": {}}
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения metadata.json: {e}. Создаём пустую структуру.")
        return {"tables": {}}

def save_metadata(filepath=None, data=None):
    """
    Сохраняет метаданные в JSON-файл.
    Если filepath не указан — сохраняет в metadata.json.
    """
    if filepath is None:
        filepath = METADATA_FILE
    if data is None:
        data = {"tables": {}}

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
