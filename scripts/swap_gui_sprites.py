#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт: Текстурный мост для GUI (Массовая замена спрайтов) в HOI4
Sons of Mobius Development Tools

Что делает скрипт:
- Сканирует указанный .gui файл на наличие старых имен спрайтов/текстур.
- Заменяет их на новые кастомные имена по вашему списку соответствия.
- Автоматически создает резервную копию (.bak) исходного файла перед изменением.
- Игнорирует закомментированные строки (после знака #), чтобы не портить историю.
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

# 2. КАРТА ПОДМЕНЫ ТЕКСТУР И СПРАЙТОВ
# Формат: "ванильное_имя_спрайта": "новое_имя_из_мода"
# Скрипт заменит только то, что указано здесь. Остальные текстуры не пострадают.
SPRITE_MAPPING = {
    "GFX_tiled_plain_bg2": "GFX_som_production_main_bg",      # Главный фон меню производства
    "GFX_stats_entry_long_bg": "GFX_som_production_header_clean",       # Подложка под заголовок окна
    "GFX_technology_folder_bg": "GFX_som_resource_box",       # Маленькие плашки для ресурсов
    # "GFX_production_line_arrow": "GFX_som_prod_arrow",        # Стрелочки в линиях производства
}

# ============================================================
# КОД СКРИПТА - НЕ ИЗМЕНЯЙТЕ БЕЗ НЕОБХОДИМОСТИ
# ============================================================

def main():
    print("=" * 60)
    print("[START] Запуск Текстурного моста для GUI")
    print("=" * 60)

    gui_path = Path(TARGET_GUI_FILE)

    # ПРОВЕРКА 1: Существует ли файл
    if not gui_path.exists():
        print(f"[ERROR] Файл интерфейса не найден по пути:\n        {TARGET_GUI_FILE}")
        print("[INFO] Проверьте правильность пути в блоке НАСТРОЙКИ.")
        return

    # ПРОВЕРКА 2: Заданы ли текстуры для замены
    if not SPRITE_MAPPING:
        print("[WARN] Словарь SPRITE_MAPPING пуст. Заменять нечего.")
        return

    print(f"[INFO] Целевой файл: {gui_path.name}")
    print(f"[INFO] Загружено правил подмены текстур: {len(SPRITE_MAPPING)}")

    # Создаем бэкап
    backup_path = gui_path.with_suffix(gui_path.suffix + ".bak")
    print(f"[INFO] Создаем бэкап файла в: {backup_path.name}")
    shutil.copyfile(gui_path, backup_path)

    # Читаем файл построчно
    with open(gui_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    updated_lines = []
    total_replacements = 0

    print("-" * 60)
    print("[PROCESS] Начинаем сканирование и замену текстур...")
    print("-" * 60)

    # Регулярка ищет параметры quadTextureSprite или spriteType, за которыми идет имя в кавычках
    # Группа 1: 'quadTextureSprite = "' или 'spriteType = "'
    # Группа 2: само имя спрайта
    # Группа 3: закрывающая кавычка '"'
    sprite_pattern = re.compile(r'((?:quadTextureSprite|spriteType)\s*=\s*")([^"]+)(")')

    for line_num, line in enumerate(lines, start=1):
        # Отрезаем комментарии, чтобы не производить замену в неактивном коде
        parts = line.split("#", 1)
        code_part = parts[0]
        comment_part = "#" + parts[1] if len(parts) > 1 else ""

        match = sprite_pattern.search(code_part)

        if match:
            old_sprite = match.group(2) # Берем текущее имя ассета из файла

            if old_sprite in SPRITE_MAPPING:
                new_sprite = SPRITE_MAPPING[old_sprite]
                
                # Делаем безопасную замену с сохранением структуры пробелов
                new_code_part = sprite_pattern.sub(rf'\1{new_sprite}\3', code_part)
                full_line = new_code_part + comment_part
                
                print(f"[SWAP] Строка {line_num}: подмена '{old_sprite}' -> '{new_sprite}'")
                total_replacements += 1
            else:
                full_line = line
        else:
            full_line = line

        updated_lines.append(full_line)

    # Сохраняем результат
    if total_replacements > 0:
        with open(gui_path, "w", encoding="utf-8") as f:
            f.write("".join(updated_lines))
        print("-" * 60)
        print(f"[FINISH] Текстурный мост успешно отработал! Всего замен: {total_replacements}")
        print(f"[FINISH] Изменения внесены в: {gui_path.name}")
    else:
        print("-" * 60)
        print("[INFO] Ни одной текстуры из списка настроек в файле не обнаружено. Ничего не изменено.")

    print("=" * 60)

if __name__ == "__main__":
    main()