# src/primitive_db/engine.py

import shlex

from prettytable import PrettyTable
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from .core import create_table, delete, drop_table, insert, list_tables, select, update
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

# Путь к файлу метаданных
METADATA_FILE = "metadata.json"  # ← Исправлено: должно быть metadata.json, как в core
# Если хочешь оставить db_meta.json — передавай его везде

# Автодополнение команд
completer = WordCompleter([
    "create_table", "drop_table", "list_tables",
    "insert into", "select from", "update", "delete from", "info",
    "help", "exit"
], ignore_case=True)


def print_help():
    """Справка по командам"""
    print("\n***Операции с таблицами***")
    print("Функции:")
    print("create_table <имя> <столбец1:тип> ...  - создать таблицу")
    print("list_tables                              - показать все таблицы")
    print("drop_table <имя>                         - удалить таблицу")
    print("\n***Операции с данными***")
    print("insert into <таблица> values (знач1, ...) - добавить запись")
    print("select from <таблица> [where столбец=знач] - выбрать данные")
    print("update <таблица> set поле=нов_знач where условие - обновить")
    print("delete from <таблица> where условие       - удалить по условию")
    print("info <таблица>                            - информация о таблице")
    print("\nОбщие команды:")
    print("help - справка")
    print("exit - выход")


def print_table(data, columns):
    """Красивый вывод таблицы"""
    if not data:
        print("Таблица пуста.")
        return
    table = PrettyTable()
    table.field_names = list(columns.keys())
    for row in data:
        table.add_row([row.get(col, "") for col in columns])
    print(table)

'''
def parse_where_clause(condition_str):
    condition_str = condition_str.strip()
    if not condition_str:
        return None
    if " = " not in condition_str:
        raise ValueError(f"Неверный формат условия: {condition_str}")
    key, raw_value = condition_str.split(" = ", 1)
    key = key.strip()
    raw_value = raw_value.strip()

    if raw_value.lower() == "true":
        value = True
    elif raw_value.lower() == "false":
        value = False
    elif raw_value.isdigit() or (raw_value.startswith('-') and raw_value[1:].isdigit()):
        value = int(raw_value)
    elif '.' in raw_value:
        try:
            value = float(raw_value)
        except:
            value = raw_value
    elif (raw_value.startswith('"') and raw_value.endswith('"')) or \
         (raw_value.startswith("'") and raw_value.endswith("'")):
        value = raw_value[1:-1]
    else:
        value = raw_value
    return {key: value}
'''


def parse_where_clause(condition_str):
    """Разбирает условие вида 'name=Alice' или 'age=25' (с или без пробелов)"""
    condition_str = condition_str.strip()
    if not condition_str:
        return None

    # Находим ПЕРВОЕ вхождение '=' (не ' = ')
    if '=' not in condition_str:
        raise ValueError(f"Неверный формат условия: {condition_str}")

    idx = condition_str.find('=')
    key = condition_str[:idx].strip()
    value_str = condition_str[idx+1:].strip()

    # Парсим значение
    if value_str.lower() == "true":
        value = True
    elif value_str.lower() == "false":
        value = False
    elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
        value = int(value_str)
    elif '.' in value_str:
        try:
            value = float(value_str)
        except:
            value = value_str.strip('"').strip("'")
    elif (value_str.startswith('"') and value_str.endswith('"')) or \
         (value_str.startswith("'") and value_str.endswith("'")):
        value = value_str[1:-1]
    else:
        value = value_str  # строка без кавычек

    return {key: value}


'''
def parse_set_clause(set_str):
    set_str = set_str.strip()
    if not set_str:
        return {}
    parts = []
    part = ""
    in_quotes = False
    for char in set_str:
        if char in ('"', "'"):
            in_quotes = not in_quotes
        if char == ',' and not in_quotes:
            parts.append(part)
            part = ""
        else:
            part += char
    parts.append(part)

    result = {}
    for part in parts:
        part = part.strip()
        if " = " not in part:
            raise ValueError(f"Неверный формат в set: {part}")
        key, raw_value = part.split(" = ", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value.lower() == "true":
            value = True
        elif raw_value.lower() == "false":
            value = False
        elif raw_value.isdigit() or (raw_value.startswith('-') and raw_value[1:].isdigit()):
            value = int(raw_value)
        elif '.' in raw_value:
            try:
                value = float(raw_value)
            except:
                value = raw_value
        elif (raw_value.startswith('"') and raw_value.endswith('"')) or \
             (raw_value.startswith("'") and raw_value.endswith("'")):
            value = raw_value[1:-1]
        else:
            value = raw_value
        result[key] = value
    return result
'''


def parse_set_clause(set_str):
    """Разбирает строку вида 'age=26, name="Alice"' или 'age = 26, name = "Alice"'"""
    set_str = set_str.strip()
    if not set_str:
        return {}
    
    # Сначала разбиваем по запятым, но учитываем кавычки
    parts = []
    part = ""
    in_quotes = False
    for char in set_str:
        if char in ('"', "'"):
            in_quotes = not in_quotes
        if char == ',' and not in_quotes:
            parts.append(part.strip())
            part = ""
        else:
            part += char
    parts.append(part.strip())

    result = {}
    for part in parts:
        # Поддерживаем оба формата: age=26 и age = 26
        if '=' not in part:
            raise ValueError(f"Неверный формат в set: {part}")
        
        # Разделяем по первому '='
        key_end = part.find('=')
        key = part[:key_end].strip()
        value_str = part[key_end+1:].strip()

        # Парсим значение
        if value_str.lower() == "true":
            value = True
        elif value_str.lower() == "false":
            value = False
        elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            value = int(value_str)
        elif '.' in value_str:
            try:
                value = float(value_str)
            except:
                value = value_str.strip('"').strip("'")
        elif (value_str.startswith('"') and value_str.endswith('"')) or \
             (value_str.startswith("'") and value_str.endswith("'")):
            value = value_str[1:-1]
        else:
            value = value_str  # например, строка без кавычек

        result[key] = value
    return result


def run():
    """Основной цикл программы"""
    print("DB project is running!")
    print_help()

    while True:
        try:
            user_input = prompt(">>> Введите команду: ", completer=completer).strip()
            if not user_input:
                continue

            # Разбираем через shlex — правильно обработает кавычки
            args = shlex.split(user_input)
            cmd = args[0].lower() if args else ""

            # Загружаем метаданные
            metadata = load_metadata()

            # === CREATE TABLE ===
            if cmd == "create_table":
                if len(args) < 3:
                    print("Использование: create_table <имя> <столбец1:тип> ...")
                else:
                    table_name = args[1]
                    columns = args[2:]
                    result = create_table(metadata, table_name, columns)
                    print(result)
                    if "успешно" in result:
                        save_metadata(data=metadata)

            # === LIST TABLES ===
            elif cmd == "list_tables":
                print(list_tables(metadata))

            # === DROP TABLE ===
            elif cmd == "drop_table":
                if len(args) != 2:
                    print("Использование: drop_table <имя>")
                else:
                    table_name = args[1]
                    result = drop_table(metadata, table_name)
                    print(result)
                    if "успешно" in result:
                        save_metadata(data=metadata)

            # === INSERT INTO ===
                '''
                elif cmd == "insert" and len(args) > 1 and args[1] == "into":
                    if len(args) < 5 or args[3] != "values":
                        print("Пример: insert into users values (\"Alice\", 30)")
                        continue
                    table_name = args[2]
                    values_str = args[4]  # "(\"Alice\", 30)"
                    if values_str.startswith("(") and values_str.endswith(")"):
                        values_str = values_str[1:-1]
                    values = [v.strip() for v in values_str.split(",") if v.strip()]
                    result = insert(metadata, table_name, values)
                    print(result)
                '''

            elif cmd == "insert" and len(args) > 1 and args[1] == "into":
                if len(args) < 3:
                    print("Использование: insert into <таблица> values (...)")
                    continue
                table_name = args[2]

                # Ищем "values" и всё, что после
                try:
                    values_index = user_input.lower().index("values")
                    values_part = user_input[values_index + 6:].strip()  # "values" = 6 символов
                    if values_part.startswith("(") and values_part.endswith(")"):
                        values_part = values_part[1:-1]
                    # Разбиваем вручную, учитывая кавычки
                    values = []
                    part = ""
                    in_quotes = False
                    for char in values_part:
                        if char in ('"', "'"):
                            in_quotes = not in_quotes
                        if char == ',' and not in_quotes:
                            values.append(part.strip())
                            part = ""
                        else:
                            part += char
                    values.append(part.strip())

                    result = insert(metadata, table_name, values)
                    print(result)
                except Exception as e:
                    print(f"Ошибка разбора значений: {e}")

            # === SELECT FROM ===
            elif cmd == "select" and len(args) > 1 and args[1] == "from":
                if len(args) < 3:
                    print("Использование: select from <таблица> [where ...]")
                    continue
                table_name = args[2]
                if table_name not in metadata["tables"]:
                    print(f"Ошибка: таблица '{table_name}' не существует.")
                    continue

                where_clause = None
                if "where" in user_input:
                    where_part = user_input.split("where", 1)[1].strip()
                    where_clause = parse_where_clause(where_part)

                data = load_table_data(table_name)
                result_data = select(data, where_clause)
                print_table(result_data, metadata["tables"][table_name]["columns"])

            # === UPDATE ===
            elif cmd == "update" and len(args) > 1:
                if len(args) < 6 or "set" not in args or "where" not in args:
                    print("Пример: update users set name=\"Bob\" where ID=1")
                    continue
                table_name = args[1]
                set_index = args.index("set")
                where_index = args.index("where") if "where" in args else None
                if where_index is None or where_index <= set_index:
                    print("Ошибка: требуется 'where'")
                    continue

                set_str = " ".join(args[set_index + 1:where_index])
                where_str = " ".join(args[where_index + 1:])

                set_clause = parse_set_clause(set_str)
                where_clause = parse_where_clause(where_str)

                data = load_table_data(table_name)
                updated = update(data, set_clause, where_clause)
                if updated > 0:
                    save_table_data(table_name, data)
                    print(f"Обновлено {updated} записей.")
                else:
                    print("Не найдено записей для обновления.")

            # === DELETE FROM ===
            elif cmd == "delete" and len(args) > 1 and args[1] == "from":
                if len(args) < 4 or "where" not in args:
                    print("Пример: delete from users where ID=1")
                    continue
                table_name = args[2]
                where_str = " ".join(args[args.index("where") + 1:])
                where_clause = parse_where_clause(where_str)

                data = load_table_data(table_name)
                old_count = len(data)
                new_data = delete(data, where_clause)
                if len(new_data) < old_count:
                    save_table_data(table_name, new_data)
                    print("Запись успешно удалена.")
                else:
                    print("Не найдено записей для удаления.")

            # === INFO ===
            elif cmd == "info":
                if len(args) != 2:
                    print("Использование: info <таблица>")
                else:
                    table_name = args[1]
                    if table_name not in metadata["tables"]:
                        print(f"Таблица '{table_name}' не существует.")
                    else:
                        t = metadata["tables"][table_name]
                        cols = ", ".join([f"{k}:{v}" for k, v in t["columns"].items()])
                        data = load_table_data(table_name)
                        print(f"Таблица: {table_name}\nСтолбцы: {cols}\nЗаписей: {len(data)}")

            # === HELP / EXIT ===
            elif cmd == "help":
                print_help()

            elif cmd == "exit":
                print("Выход из программы.")
                break

            else:
                print(f"Неизвестная команда: {cmd}. Введите 'help'.")

        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
