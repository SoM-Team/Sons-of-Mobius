#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт: Проверка на здравомыслие (Sanity Check) для .gui файлов HOI4
Sons of Mobius Development Tools

Что делает скрипт:
- Проверяет баланс открывающих '{' и закрывающих '}' скобок.
- Отслеживает, какое именно окно (containerWindowType) забыли закрыть.
- Показывает точный номер строки, где произошел сбой.
- Ничего не перезаписывает, работает безопасно (только чтение).
"""

import os
from pathlib import Path

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ ТОЛЬКО ТУТ
# ============================================================

# 1. Полный путь к файлу интерфейса, который нужно проверить
# (Можно указать любой .gui файл вашего мода)
TARGET_GUI_FILE = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/interface/countrytechtreeview.gui"

# ============================================================
# КОД СКРИПТА - НЕ ИЗМЕНЯЙТЕ БЕЗ НЕОБХОДИМОСТИ
# ============================================================

def main():
    print("=" * 60)
    print("[START] Запуск проверки на здравомыслие (Sanity Check)")
    print("=" * 60)

    gui_path = Path(TARGET_GUI_FILE)

    # ПРОВЕРКА: Существует ли вообще этот файл
    if not gui_path.exists():
        print(f"[ERROR] Файл интерфейса не найден по указанному пути:\n        {TARGET_GUI_FILE}")
        print("[INFO] Проверьте блок НАСТРОЙКИ.")
        return

    print(f"[INFO] Анализируем файл: {gui_path.name}")
    print("[INFO] Погнали считать скобки...")
    print("-" * 60)

    # Читаем все строки из файла
    with open(gui_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    opened_brackets = 0
    closed_brackets = 0
    
    # Стек для отслеживания имен окон. Сюда будем складывать кортежи: (имя_окна, номер_строки)
    window_stack = []
    
    current_window_name = "Неизвестный контейнер"
    errors_found = False

    for line_num, line in enumerate(lines, start=1):
        # Убираем пробелы по бокам и комментарии игры (всё, что после #)
        clean_line = line.strip().split("#")[0]

        # Пытаемся поймать имя контейнера/окна для контекста, если оно тут объявляется
        if "name =" in clean_line:
            # Вытягиваем то, что в кавычках после name =
            try:
                current_window_name = clean_line.split("=")[1].replace('"', '').strip()
            except Exception:
                pass

        # Считаем скобки в текущей строке
        for char in clean_line:
            if char == "{":
                opened_brackets += 1
                # Если это открытие какого-то блока, запоминаем текущее имя окна и строку
                window_stack.append((current_window_name, line_num))
                
            elif char == "}":
                closed_brackets += 1
                if len(window_stack) > 0:
                    window_stack.pop() # Успешно закрыли последний открытый блок
                else:
                    # Паника! Закрывающих скобок больше, чем открывающих
                    print(f"[CRITICAL] Лишняя закрывающая скобка '}}' на строке {line_num}!")
                    print(f"[CONTEXT] Код в этой строке: `{clean_line}`")
                    errors_found = True

    print("-" * 60)
    print(f"[RESULT] Всего открыто '{{': {opened_brackets}")
    print(f"[RESULT] Всего закрыто '}}': {closed_brackets}")

    # Финальный вердикт
    if opened_brackets == closed_brackets and not errors_found:
        print()
        print("====== [УСПЕХ / SUCCESS] ======")
        print("Баланс скобок идеален!")
        print("Этот файл можно спокойно пушить в Гит.")
        print("================================")
    else:
        print()
        print("====== [ВНИМАНИЕ / WARNING] ======")
        print("[ERROR] Обнаружена критическая ошибка в структуре файла!")
        
        if opened_brackets > closed_brackets:
            diff = opened_brackets - closed_brackets
            print(f"[ERROR] Не хватает закрывающих скобок '}}': {diff} шт.")
            print("\n[INFO] Список блоков, которые были открыты, но НЕ закрыты до конца файла:")
            
            # Покажем последние незакрытые блоки (но не больше 5, чтобы не спамить консоль)
            for name, line in window_stack[-5:]:
                print(f"  - Блок/Окно близ строки {line} (возможный name: '{name}')")
                
        elif closed_brackets > opened_brackets:
            print("[ERROR] Кто-то бахнул лишних закрывающих скобок '}'.")
            print("[INFO] Поднимитесь выше по логу консоли, там указаны строки с лишними '}'.")
            
        print("\n[TIP] Игра ОДНОЗНАЧНО сломается или вылетит, если запустить её с таким файлом.")
        print("==================================")

    print()
    print("=" * 60)
    print("[END] Проверка завершена.")
    print("=" * 60)

if __name__ == "__main__":
    main()