#!/usr/bin/env python3

# src/primitive_db/main.py

from primitive_db.engine import run

'''
Обновите точку входа. В src/primitive_db/main.py измените вызов так, 
чтобы запускалась функция run() из engine.py.
'''

def main():
    print("DB project is running!")
    # welcome()
    run()

if __name__ == "__main__":
    main()
