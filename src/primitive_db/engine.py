# src/primitive_db/engine.py

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


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
