# src/primitive_db/core.py

SUPPORTED_TYPES = {"int", "str", "bool"}

# Здесь будет основная логика работы с таблицами и данными.


def create_table(metadata: dict, table_name: str, columns: list) -> str:
    '''Она должна принимать текущие метаданные, имя таблицы и список столбцов.
    Автоматически добавлять столбец ID:int в начало списка столбцов.
    Проверять, не существует ли уже таблица с таким именем. Если да, выводить ошибку.
    Проверять корректность типов данных (только int, str, bool).
    В случае успеха, обновлять словарь metadata и возвращать его.'''

    """
    Создаёт таблицу с автоматическим ID:int.
    Проверяет имя и типы.
    Возвращает сообщение об успехе или ошибке.
    """
    if table_name in metadata:
        return f'Ошибка: Таблица "{table_name}" уже существует.'

    # Начинаем с ID:int
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

    metadata[table_name] = table_columns
    return f'Таблица "{table_name}" успешно создана со столбцами: {", ".join([f"{k}:{v}" for k, v in table_columns.items()])}' # noqa: E501


def drop_table(metadata: dict, table_name: str) -> str:
    '''Проверяет существование таблицы. Если таблицы нет, выводит ошибку.
    Удаляет информацию о таблице из metadata и возвращает обновленный словарь.'''

    """
    Удаляет таблицу.
    """
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata[table_name]
    return f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata: dict) -> str:
    """
    Возвращает список таблиц.
    """
    if not metadata:
        return "Нет созданных таблиц."
    return "\n".join(f"- {name}" for name in sorted(metadata))
