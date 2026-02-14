# src/primitive_db/core.py

import json
from pathlib import Path
from typing import Any, Dict, List

SUPPORTED_TYPES = {"int", "str", "bool"}

# --- Пути ---
METADATA_FILE = Path(__file__).parent / "metadata.json"


# --- Утилиты для метаданных ---
def load_metadata() -> Dict[str, Any]:
    """Загружает метаданные из файла."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {"tables": {}}
    return {"tables": {}}


def save_metadata(metadata: Dict[str, Any]) -> None:
    """Сохраняет метаданные в файл."""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


# --- CRUD: Insert ---
def insert(metadata: Dict, table_name: str, values: List[str]) -> str:
    """
    Добавляет новую запись в таблицу.
    """
    if table_name not in metadata["tables"]:
        return f"Ошибка: таблица '{table_name}' не существует."

    table = metadata["tables"][table_name]
    columns = table["columns"]

    expected_cols = len(columns) - 1
    if len(values) != expected_cols:
        return f"Ошибка: ожидается {expected_cols} значений, получено {len(values)}."

    from primitive_db.utils import load_table_data, save_table_data
    data = load_table_data(table_name)

    new_id = max((row["ID"] for row in data), default=0) + 1
    new_row = {"ID": new_id}
    value_index = 0

    for col_name, col_type in columns.items():
        if col_name == "ID":
            continue
        raw_value = values[value_index]
        value_index += 1

        try:
            if col_type == "int":
                value = int(raw_value.strip('"').strip("'"))
            elif col_type == "bool":
                value = raw_value.strip('"').strip("'").lower() in ("true", "1", "yes")
            else:  # str
                value = raw_value.strip('"').strip("'")
        except Exception:
            return f"Ошибка: значение '{raw_value}' не соответствует типу '{col_type}' для столбца '{col_name}'."

        new_row[col_name] = value

    data.append(new_row)
    save_table_data(table_name, data)
    return f"Запись с ID={new_id} успешно добавлена в таблицу '{table_name}'."


# --- CRUD: Select ---
def select(table_data: List[Dict], where_clause=None) -> List[Dict]:
    """
    Возвращает отфильтрованные данные.
    """
    if where_clause is None:
        return table_data

    result = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if str(row.get(key)) != str(value):
                match = False
                break
        if match:
            result.append(row)
    return result


# --- CRUD: Update ---
def update(table_data: List[Dict], set_clause: Dict, where_clause: Dict) -> int:
    """
    Обновляет поля в записях по условию.
    Возвращает количество обновлённых записей.
    """
    updated_count = 0
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if str(row.get(key)) != str(value):
                match = False
                break
        if match:
            for key, value in set_clause.items():
                if key in row:
                    row[key] = value
            updated_count += 1
    return updated_count


# --- CRUD: Delete ---
def delete(table_data: List[Dict], where_clause: Dict) -> List[Dict]:
    """
    Удаляет записи по условию.
    Возвращает список оставшихся записей.
    """
    result = []
    for row in table_data:
        match = True
        for key, value in where_clause.items():
            if str(row.get(key)) != str(value):
                match = False
                break
        if not match:
            result.append(row)
    return result


# --- Управление таблицами ---
def create_table(metadata: Dict, table_name: str, columns: List[str]) -> str:
    """
    Создаёт таблицу с ID:int.
    """
    if table_name in metadata["tables"]:
        return f'Ошибка: Таблица "{table_name}" уже существует.'

    table_columns = {"ID": "int"}

    for col in columns:
        if ":" not in col:
            return f'Некорректное значение: {col}. Используйте формат "столбец:тип".'

        col_name, col_type = col.split(":", 1)
        col_name = col_name.strip()
        col_type = col_type.strip()

        if not col_name:
            return "Некорректное значение: имя столбца не может быть пустым."
        if col_type not in SUPPORTED_TYPES:
            return f'Некорректное значение: {col_type}. Поддерживаемые типы: {", ".join(SUPPORTED_TYPES)}.'
        if col_name in table_columns:
            return f'Ошибка: Столбец "{col_name}" уже определён в таблице.'

        table_columns[col_name] = col_type

    metadata["tables"][table_name] = {"columns": table_columns, "data": []}
    return f'Таблица "{table_name}" успешно создана со столбцами: {", ".join([f"{k}:{v}" for k, v in table_columns.items()])}'


def drop_table(metadata: Dict, table_name: str) -> str:
    """
    Удаляет таблицу.
    """
    if table_name not in metadata["tables"]:
        return f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata["tables"][table_name]
    return f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata: Dict) -> str:
    """
    Возвращает список таблиц.
    """
    if not metadata.get("tables"):
        return "Нет созданных таблиц."
    return "\n".join(f"- {name}" for name in sorted(metadata["tables"]))
