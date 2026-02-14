# src/decorators.py

"""
Модуль с декораторами для обработки ошибок в БД.
"""

import functools
import time
import traceback


def handle_db_errors(func):
    """
    Декоратор для перехвата и обработки типичных ошибок при работе с БД.

    Перехватывает:
    - FileNotFoundError: файл данных не найден
    - KeyError: обращение к несуществующей таблице/столбцу
    - ValueError: ошибки валидации (например, неверный тип данных)
    - Любые другие исключения (с выводом трассировки)

    Если ошибка произошла, выводит сообщение и возвращает None.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"Ошибка БД: файл данных не найден. Возможно, база не инициализирована.\n{e}") # noqa: E501
        except KeyError as e:
            print(f"Ошибка БД: объект не найден — проверьте существование таблицы/столбца.\nКлюч: {e}") # noqa: E501
        except ValueError as e:
            print(f"Ошибка БД: ошибка валидации данных.\n{e}")
        except Exception as e:
            # Для отладки — выводим полную трассировку
            print(f"Неожиданная ошибка в БД:\n{type(e).__name__}: {e}")
            traceback.print_exc()
        return None  # Возвращаем None при любой ошибке

    return wrapper


def confirm_action(action_name: str):
    """
    Декоратор-фабрика: запрашивает у пользователя подтверждение перед 
    выполнением действия.
    
    Args:
        action_name (str): Название действия (например, "удаление таблицы").
    
    Returns:
        Декоратор, который оборачивает функцию.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Выводим запрос на подтверждение
            user_input = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower() # noqa: E501
            
            if user_input != 'y':
                print("Операция отменена.")
                return None  # Возвращаем None, если пользователь отказался
            
            # Если подтверждено — вызываем оригинальную функцию
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции.
    Использует time.monotonic() для точного измерения (не зависит от системных часов).
    
    Выводит в консоль: "Функция <имя_функции> выполнилась за X.XXX секунд".
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()  # Точное время начала
        result = func(*args, **kwargs)  # Вызов оригинальной функции
        end_time = time.monotonic()   # Точное время окончания
        
        execution_time = end_time - start_time
        # print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд")
        print(f"Функция {func.__name__} выполнилась за {execution_time*1e6:.0f} мкс")
        
        return result
    
    return wrapper


def create_cacher():
    """
    Создаёт кэш-механизм с замыканием.
    
    Возвращает функцию cache_result(key, value_func), которая:
    - проверяет наличие результата по ключу в кэше;
    - если есть — возвращает закэшированное значение;
    - если нет — вызывает value_func(), сохраняет результат и возвращает его.
    """
    cache = {}  # Словарь для хранения кэшированных результатов

    def cache_result(key, value_func):
        """
        Кэширует результат вызова value_func() по ключу key.
        
        Args:
            key: идентификатор для кэширования (например, строка с запросом);
            value_func: функция без аргументов, возвращающая значение.
        
        Returns:
            Закэшированный или свежеполученный результат.
        """
        if key in cache:
            print(f"[КЭШ] Используем закэшированный результат для ключа '{key}'")
            return cache[key]

        print(f"[КЭШ] Вычисляем результат для ключа '{key}' (кэширование...)")
        result = value_func()
        cache[key] = result
        return result

    return cache_result
