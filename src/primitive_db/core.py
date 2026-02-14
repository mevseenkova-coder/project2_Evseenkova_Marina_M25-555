# src/primitive_db/core.py

"""
Модуль с основными операциями CRUD и управления таблицами.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.decorators import confirm_action, create_cacher, handle_db_errors, log_time

SUPPORTED_TYPES = {"int", "str", "bool"}

# --- Пути ---
METADATA_FILE = Path(__file__).parent / "metadata.json"

# Глобальный кэш для select
select_cache = create_cacher()


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
'''
@handle_db_errors
@log_time
def insert(metadata: Dict, table_name: str, values: List[str]) -> str:
    """
    Добавляет новую запись в таблицу.

    Args:
        metadata: словарь метаданных БД.
        table_name: имя таблицы.
        values: список значений (без ID).

    Returns:
        Сообщение о результате операции.
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
            return f"Ошибка: значение '{raw_value}' не соответствует \
                    типу '{col_type}' для столбца '{col_name}'." # noqa: E501

        new_row[col_name] = value

    data.append(new_row)
    save_table_data(table_name, data)
    return f"Запись с ID={new_id} успешно добавлена в таблицу '{table_name}'."
'''

@handle_db_errors
@log_time
def insert(metadata: Dict[str, Any], table_name: str, values: List[str]) -> str:
    """
    Добавляет новую запись в таблицу.

    Args:
        metadata: словарь метаданных БД (содержит описание таблиц).
        table_name: имя таблицы для вставки.
        values: список значений полей (без ID), соответствующих столбцам таблицы.

    Returns:
        Сообщение об успехе или ошибке.
    """
    # Проверка существования таблицы
    if table_name not in metadata["tables"]:
        return f"Ошибка: таблица '{table_name}' не существует."

    table = metadata["tables"][table_name]
    columns = table["columns"]

    # Проверка количества значений (без учёта ID)
    expected_cols = len(columns) - 1
    if len(values) != expected_cols:
        return (
            f"Ошибка: ожидается {expected_cols} значений, "
            f"получено {len(values)}."
        )

    # Загрузка данных таблицы
    from primitive_db.utils import load_table_data, save_table_data
    data = load_table_data(table_name)

    # Генерация нового ID
    new_id = max((row["ID"] for row in data), default=0) + 1
    new_row = {"ID": new_id}

    # Обработка каждого столбца (кроме ID)
    for col_name, col_type in columns.items():
        if col_name == "ID":
            continue

        raw_value = values[new_row["ID"] - 1]  # Исправлено: индекс зависит от ID
        # ИЛИ (если сохранять старый подход):
        # raw_value = values[len(new_row) - 1]

        try:
            cleaned = raw_value.strip('"').strip("'")
            if col_type == "int":
                value = int(cleaned)
            elif col_type == "bool":
                value = cleaned.lower() in ("true", "1", "yes")
            else:  # str
                value = cleaned
        except ValueError as e:
            return (
                f"Ошибка: значение '{raw_value}' не соответствует типу "
                f"'{col_type}' для столбца '{col_name}'. Детали: {e}"
            )
        except Exception as e:
            return f"Ошибка обработки значения '{raw_value}'. Детали: {e}"

        new_row[col_name] = value

    # Сохранение новой записи
    data.append(new_row)
    save_table_data(table_name, data)

    return f"Запись с ID={new_id} успешно добавлена в таблицу '{table_name}'."


# --- CRUD: Select ---
'''
@handle_db_errors
@log_time
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
'''

@handle_db_errors
@log_time
def select(table_data: List[Dict], where_clause=None) -> List[Dict]:
    """
    Возвращает отфильтрованные данные с кэшированием.


    Args:
        table_data: список записей таблицы.
        where_clause: словарь условий фильтрации (ключ-значение).


    Returns:
        Список отфильтрованных записей.
    """
    
    # Формируем ключ кэша: зависит от данных и условия where
    # Для простоты используем строковое представление where_clause
    where_str = str(where_clause) if where_clause else "no_where"
    key = f"select_{len(table_data)}_rows_{where_str}"
    
    # Функция для получения данных (будет вызвана только при отсутствии кэша)
    def get_data():
        if where_clause is None:
            return table_data
        
        result = []
        for row in table_data:
            match = all(
                str(row.get(key)) == str(value)
                for key, value in where_clause.items()
            )
            if match:
                result.append(row)
        return result
    
    # Используем кэш
    return select_cache(key, get_data)


# --- CRUD: Update ---
@handle_db_errors
def update(table_data: List[Dict], set_clause: Dict, where_clause: Dict) -> int:
    """
    Обновляет поля в записях по условию.

    Args:
        table_data: список записей таблицы.
        set_clause: словарь новых значений (ключ-значение).
        where_clause: условия для выбора записей.

    Returns:
        Количество обновлённых записей.
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
@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: List[Dict], where_clause: Dict) -> List[Dict]:
    """
    Удаляет записи по условию.

    Args:
        table_data: список записей таблицы.
        where_clause: условия для удаления.

    Returns:
        Список оставшихся записей.
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
@handle_db_errors
def create_table(metadata: Dict, table_name: str, columns: List[str]) -> str:
    """
    Создаёт таблицу с ID:int.

    Args:
        metadata: словарь метаданных БД.
        table_name: имя новой таблицы.
        columns: список столбцов в формате "имя:тип".

    Returns:
        Сообщение о результате.
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
            return f'Некорректное значение: {col_type}. Поддерживаемые типы: {", ".join(SUPPORTED_TYPES)}.' # noqa: E501
        if col_name in table_columns:
            return f'Ошибка: Столбец "{col_name}" уже определён в таблице.'

        table_columns[col_name] = col_type

    metadata["tables"][table_name] = {"columns": table_columns, "data": []}
    return f'Таблица "{table_name}" успешно создана со столбцами: {", ".join([f"{k}:{v}" for k, v in table_columns.items()])}' # noqa: E501

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: Dict, table_name: str) -> str:
    """
    Удаляет таблицу.

    Args:
        metadata: словарь метаданных БД.
        table_name: имя таблицы для удаления.

    Returns:
        Сообщение о результате.
    """

    if table_name not in metadata["tables"]:
        return f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata["tables"][table_name]
    return f'Таблица "{table_name}" успешно удалена.'

@handle_db_errors
def list_tables(metadata: Dict) -> str:
    """
    Возвращает список таблиц.

    Args:
        metadata: словарь метаданных БД.

    Returns:
        Строка с перечнем таблиц (или сообщение об отсутствии).
    """

    if not metadata.get("tables"):
        return "Нет созданных таблиц."
    return "\n".join(f"- {name}" for name in sorted(metadata["tables"]))
