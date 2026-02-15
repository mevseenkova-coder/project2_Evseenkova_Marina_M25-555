# project2_Evseenkova_Marina_M25-555
Домашнее задание №2. Примитивная база данных

# Primitive DB

Простая CLI-база данных с поддержкой таблиц и персистентности.

Инструкции по установке (poetry install или make install) и запуску (poetry run project или make project).
Чтобы установить poetry, напишите команду sudo apt install python3-poetry
Активируйте виртуальное окружение командами: poetry env activate
После этого у вас в терминале появится что то похожее (только с вашими данными, ниже это пример!):
C:\Users\пользователь\projects\github\project2_Evseenkova_Marina_M25-555\project2_Evseenkova_Marina_M25-555\.venv\Scripts\activate.ps1

Чтобы запустить poetry, напишите команду poetry run python -m src.primitive_db.main 
Альтернативный вариант:
    Выполните установку пакета с помощью команды: poetry install 
    Poetry создаст виртуальное окружение и установит в него пакет.
    После успешной установки пакета проверьте, что скрипт работает: poetry run project
    Альтернативный скрипт для запуска проекта - poetry run database или make run

poetry install создаёт виртуальное окружение и устанавливает зависимости из pyproject.toml.
make install — это удобная оболочка для poetry install, если в проекте есть Makefile.

poetry run project активирует виртуальное окружение и запускает команду.
make project — это ярлык для poetry run project, если в Makefile определена соответствующая команда.

## Управление таблицами
Проект реализует:
Управление таблицами (create_table, drop_table, list_tables).
Операции с данными (insert, select, update, delete).
Метаданные БД (хранение схемы в metadata.json).
Кэширование запросов select.
Декораторы (@handle_db_errors, @log_time, @confirm_action, @create_cacher).
Валидацию типов данных (int, str, bool).

Интерфейс командной строки
После запуска доступны команды:
Операции с таблицами:
create_table <имя> <столбец1:тип> ... — создать таблицу
list_tables — показать все таблицы
drop_table <имя> — удалить таблицу

Операции с данными:
insert into <таблица> values (знач1, ...) — добавить запись
select from <таблица> [where столбец=знач] — выбрать данные
update <таблица> set поле=нов_знач where условие — обновить
delete from <таблица> where условие — удалить по условию
info <таблица> — информация о таблице

Общие команды:
help — справка
exit — выход

### Пример использования

```bash
poetry run database
>>> Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>> Введите команду: list_tables
- users

>>> Введите команду: drop_table users
Таблица "users" успешно удалена.

2. База данных
Запишите аскинему с примером установки пакета, запуска БД, создание, проверку и удаление таблицы. Опубликуйте ее в сервисе и встройте ее в README.md
{"id":787087,
"message":"View the recording at:\n\n    https://asciinema.org/a/9UNrKjSpnjCHiCkW\n",
"description":null,
"title":"mevseenkova",
"url":"https://asciinema.org/a/9UNrKjSpnjCHiCkW",
"audio_url":null,
"visibility":"unlisted",
"file_url":"https://asciinema.org/a/9UNrKjSpnjCHiCkW.cast"}

***Операции с данными***

Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.
<command> exit - выход из программы
<command> help- справочная информация

>>>Введите команду: _ 

3. Адаптируем модуль “База данных”
Обновите README.md. Добавьте раздел "CRUD-операции" с описанием новых команд. Запишите asciinema с демонстрацией всех операций и вставьте ее в README.md.
{"id":788118,
"message":"View the recording at:\n\n    https://asciinema.org/a/ct90LTSegIrsGmlw\n",
"description":null,
"title":"mevseenkova",
"url":"https://asciinema.org/a/ct90LTSegIrsGmlw",
"visibility":"unlisted",
"audio_url":null,
"file_url":"https://asciinema.org/a/ct90LTSegIrsGmlw.cast"}

4. Декораторы и замыкания
Финальное README.md и asciinema. 
Обновите README.md, добавив информацию о новых возможностях (обработка ошибок, подтверждение действий).
Запишите финальную asciinema, демонстрирующую работу декораторов (например, запрос на подтверждение удаления).
{"id":788133,
"message":"View the recording at:\n\n    https://asciinema.org/a/AYr31TxVFQPlkufQ\n",
"description":null,
"title":"mevseenkova",
"url":"https://asciinema.org/a/AYr31TxVFQPlkufQ",
"visibility":"unlisted",
"audio_url":null,
"file_url":"https://asciinema.org/a/AYr31TxVFQPlkufQ.cast"}

продолжение:
{"id":788136,
"message":"View the recording at:\n\n    https://asciinema.org/a/iUTWR9fuds2gnsaJ\n",
"description":null,
"title":"mevseenkova",
"url":"https://asciinema.org/a/iUTWR9fuds2gnsaJ",
"visibility":"unlisted",
"audio_url":null,
"file_url":"https://asciinema.org/a/iUTWR9fuds2gnsaJ.cast"}