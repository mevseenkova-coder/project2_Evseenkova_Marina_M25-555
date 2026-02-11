# project2_Evseenkova_Marina_M25-555
Домашнее задание №2. Примитивная база данных

# Primitive DB

Простая CLI-база данных с поддержкой таблиц и персистентности.

## Управление таблицами

Доступные команды:

- `create_table <имя> <столбец1:тип> ...` — создать таблицу (автоматически добавляется `ID:int`)
- `drop_table <имя>` — удалить таблицу
- `list_tables` — показать все таблицы
- `help` — справка
- `exit` — выход

Поддерживаемые типы: `int`, `str`, `bool`.

### Пример использования

```bash
poetry run database
>>> Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>> Введите команду: list_tables
- users

>>> Введите команду: drop_table users
Таблица "users" успешно удалена.
