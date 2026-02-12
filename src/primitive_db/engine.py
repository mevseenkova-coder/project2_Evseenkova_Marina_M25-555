# src/primitive_db/engine.py

import shlex

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

# Путь к файлу метаданных
METADATA_FILE = "db_meta.json"

# Автодополнение команд
completer = WordCompleter(["create_table", "drop_table", "list_tables", "help", \
                            "exit"], ignore_case=True)

# Этот файл будет отвечать за запуск, игровой цикл и парсинг команд.

def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    """
    Приветствует пользователя и запускает цикл обработки команд.
    Использует prompt-toolkit для улучшенного ввода.
    """
    print("Первая попытка запустить проект!")
    print("***")

    completer = WordCompleter(['help', 'exit'], ignore_case=True)

    while True:
        user_input = prompt("Введите команду: ", completer=completer).strip().lower()

        if user_input == "exit":
            print("Завершение программы.")
            break
        elif user_input == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print("Неизвестная команда. Введите 'help', чтобы посмотреть доступные команды.") # noqa: E501


def run():
    '''Создайте главную функцию run(), которая будет содержать основной цикл программы 
    (while True).
    В цикле:
    Загружайте актуальные метаданные с помощью load_metadata.
    Запрашивайте ввод у пользователя.
    Разбирайте введенную строку на команду и аргументы.
    Подсказка: Для надежного разбора строки используйте библиотеку shlex. 
    args = shlex.split(user_input).
    Используйте if/elif/else или match/case для вызова соответствующей функции 
    из core.py.
    После каждой успешной операции (create_table, drop_table) сохраняйте измененные 
    метаданные с помощью save_metadata.'''

    """
    Основной цикл программы.
    """
    
    print_help()

    while True:
        try:
            user_input = prompt(">>> Введите команду: ", completer=completer).strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            cmd = args[0].lower()

            metadata = load_metadata(METADATA_FILE)

            if cmd == "create_table":
                if len(args) < 3:
                    print("Использование: create_table <имя_таблицы> <столбец1:тип> ...") # noqa: E501
                else:
                    table_name = args[1]
                    columns = args[2:]
                    result = create_table(metadata, table_name, columns)
                    print(result)
                    if "успешно" in result:
                        save_metadata(METADATA_FILE, metadata)

            elif cmd == "drop_table":
                if len(args) != 2:
                    print("Использование: drop_table <имя_таблицы>")
                else:
                    table_name = args[1]
                    result = drop_table(metadata, table_name)
                    print(result)
                    if "успешно" in result:
                        save_metadata(METADATA_FILE, metadata)

            elif cmd == "list_tables":
                if len(args) != 1:
                    print("Использование: list_tables")
                else:
                    print(list_tables(metadata))

            elif cmd == "help":
                print_help()

            elif cmd == "exit":
                print("Выход из программы.")
                break

            else:
                print(f'Функции "{cmd}" нет. Попробуйте снова.')

        except KeyboardInterrupt:
            print("\n\nПрервано пользователем.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")
