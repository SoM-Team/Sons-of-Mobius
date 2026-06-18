#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт: Массовый шрифтозаменитель в интерфейсах (.gui) HOI4
Sons of Mobius Development Tools

Что делает скрипт:
- Ищет в указанном .gui файле все текстовые поля (font = "...").
- Заменяет старые ванильные шрифты на новые по вашему списку соответствия.
- Автоматически создает резервную копию (.bak) исходного файла перед изменением.
- Игнорирует закомментированные строки (где стоит #), чтобы не делать ложных правок.
"""

import os
import re
import shutil
from pathlib import Path

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ ТОЛЬКО ТУТ
# ============================================================

# 1. Полный путь к редактируемому .gui файлу мода
TARGET_GUI_FILE = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/interface/countrytechtreeview.gui"

# 2. КАРТА ЗАМЕНЫ ШРИФТОВ
# Формат элементарный: "что_ищем_в_ванили": "на_что_меняем_в_моде"
# Если какого-то шрифта нет в списке, скрипт его просто не тронет.
FONT_MAPPING = {
    "century_gothic_16": "som_font_title_36",      # Главные заголовки окон
    "legacy_bataillon_18.5": "som_font_medium_24",     # Подзаголовки и важный текст
    "impact_32": "som_font_clean_18",           # Стандартный жирный текст
    # "hoi_16mbs": "som_font_small_16",         # Мелкий текст списков
}

# ============================================================
# КОД СКРИПТА - НЕ ИЗМЕНЯЙТЕ БЕЗ НЕОБХОДИМОСТИ
# ============================================================

def main():
    print("=" * 60)
    print("[START] Запуск Массового Шрифтозаменителя")
    print("=" * 60)

    gui_path = Path(TARGET_GUI_FILE)

    # ПРОВЕРКА 1: Существует ли файл
    if not gui_path.exists():
        print(f"[ERROR] Файл интерфейса не найден по пути:\n        {TARGET_GUI_FILE}")
        print("[INFO] Проверьте правильность пути в блоке НАСТРОЙКИ.")
        return

    # ПРОВЕРКА 2: Заданы ли шрифты для замены
    if not FONT_MAPPING:
        print("[WARN] Словарь FONT_MAPPING пуст. Нечего заменять.")
        return

    print(f"[INFO] Целевой файл: {gui_path.name}")
    print(f"[INFO] Загружено правил замены шрифтов: {len(FONT_MAPPING)}")

    # Создаем резервную копию оригинального файла
    backup_path = gui_path.with_suffix(gui_path.suffix + ".bak")
    print(f"[INFO] Создаем бэкап файла в: {backup_path.name}")
    shutil.copyfile(gui_path, backup_path)

    # Читаем файл построчно, чтобы точно знать номера строк для логов
    with open(gui_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    updated_lines = []
    total_replacements = 0

    print("-" * 60)
    print("[PROCESS] Начинаем сканирование строк...")
    print("-" * 60)

    # Регулярка ищет конструкцию font = "любое_имя_шрифта"
    # Захватывает имя шрифта в отдельную группу для проверки
    font_pattern = re.compile(r'(font\s*=\s*")([^"]+)(")')

    for line_num, line in enumerate(lines, start=1):
        # Делим строку по символу #, чтобы не менять закомментированный код
        parts = line.split("#", 1)
        code_part = parts[0]
        comment_part = "#" + parts[1] if len(parts) > 1 else ""

        # Ищем, есть ли в кодовой части строки упоминание шрифта
        match = font_pattern.search(code_part)
        
        if match:
            old_font = match.group(2) # Вытаскиваем само имя шрифта
            
            # Если этот шрифт есть в нашей карте замены — меняем!
            if old_font in FONT_MAPPING:
                new_font = FONT_MAPPING[old_font]
                
                # Собираем строку обратно с новым шрифтом
                new_code_part = code_part.replace(f'font = "{old_font}"', f'font = "{new_font}"')
                # На случай если у кодера были нестандартные пробелы вокруг знака '=':
                new_code_part = font_pattern.sub(rf'\1{new_font}\3', code_part)
                
                full_line = new_code_part + comment_part
                print(f"[REPLACE] Строка {line_num}: заменено '{old_font}' -> '{new_font}'")
                total_replacements += 1
            else:
                # Шрифт нашли, но в настройках его менять не просили
                full_line = line
        else:
            # В строке вообще нет шрифтов
            full_line = line

        updated_lines.append(full_line)

    # Сохраняем файл, только если были реальные замены
    if total_replacements > 0:
        with open(gui_path, "w", encoding="utf-8") as f:
            f.write("".join(updated_lines))
        print("-" * 60)
        print(f"[FINISH] Шрифты успешно обновлены! Всего замен: {total_replacements}")
        print(f"[FINISH] Результат сохранен в: {gui_path.name}")
    else:
        print("-" * 60)
        print("[INFO] Ни одного совпадения по шрифтам не найдено. Файл оставлен без изменений.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()