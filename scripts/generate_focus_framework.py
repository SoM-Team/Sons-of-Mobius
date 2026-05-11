#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт 1: Создание каркаса дерева национальных фокусов для Hearts of Iron IV / Script 1: Generate national focus tree framework for Hearts of Iron IV

Что делает скрипт / What this script does:
- Создаёт заданное количество пустых фокусов в указанном файле мода / Generates specified number of empty focuses in the given mod file
- Фокусы имеют только id, иконку, координаты и пустые блоки prerequisite/completion_reward / Focuses contain only id, icon, coordinates, and empty prerequisite/completion_reward blocks
- Все фокусы могут быть привязаны к первому через relative_position_id (опционально) / All focuses can be linked to the first one via relative_position_id (optional)
- При создании нового файла добавляет обязательный блок country с тэгом из префикса / When creating new file, adds required country block with tag from prefix

Как использовать / How to use:
1. Сделать копию скрипта и не использовать оригинальный скрипт / Make a copy of this script and do not use the original script
2. Открыть скрипт в редакторе Visual Studio Code с помощью терминала / Open script in Visual Studio Code editor by using terminal
3. Настроить параметры в блоке "НАСТРОЙКИ" ниже / Define settings in "SETTINGS" block below
4. Запустить скрипт: python generate_focus_framework.py / Launch the script: python generate_focus_framework.py
"""

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ / EDIT VALUES HERE
# ============================================================

# Путь к файлу дерева фокусов в моде / Path to focus tree file in mod
# ВАЖНО: имя файла (без расширения) станет id дерева фокусов / IMPORTANT: filename (without extension) becomes focus tree id
FILE_PATH = r"C:\Users\Admin\Documents\Paradox Interactive\Hearts of Iron IV\mod\sonic017\common\national_focus\NOR_focus.txt"

# Количество создаваемых фокусов / Number of focuses to generate
FOCUS_COUNT = 10

# Префикс для id фокусов (например, "NOR_" или "KOA_") / Prefix for focus ids (e.g., "NOR_" or "KOA_")
# ВАЖНО: префикс должен быть ТЭГОМ страны + нижнее подчёркивание / IMPORTANT: prefix must be COUNTRY TAG + underscore
# Пример / Example: "NOR_" (правильно / correct), "NOR" (неправильно / incorrect)
PREFIX = "NOR_"

# Стоимость фокуса (cost). Если список пустой - блок cost НЕ создаётся / Focus cost. If list is empty - cost block is NOT created.
# Пример / Example: [10] - создаст / creates cost = 10
#        []   - не создаст / does not create
COST_LIST = [10]

# Использовать relative_position_id (привязку к первому фокусу) / Use relative_position_id (link to first focus)
# True  - все фокусы (кроме первого) будут привязаны к первому
#         all focuses (except first) will be linked to first
# False - фокусы будут независимыми (без relative_position_id)
#         focuses will be independent (no relative_position_id)
USE_RELATIVE_POSITION = True

# Блок ai_will_do. Если список пустой - блок НЕ создаётся.
# ai_will_do block. If list is empty - block is NOT created.
# Пример / Example: [1]   - создаст / creates ai_will_do = { base = 1 }
#        [0.5] - создаст / creates ai_will_do = { base = 0.5 }
#        []    - не создаст / does not create
AI_WILL_DO_LIST = [1]

# ============================================================
# КОД СКРИПТА - НИЖЕ НИЧЕГО НЕ МЕНЯТЬ / SCRIPT CODE - DO NOT EDIT BELOW
# ============================================================

import os

def ensure_directory_exists(file_path):
    """Проверяет/создаёт директорию для файла / Check/create directory for file"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[INFO] Создана директория / Created directory: {directory}")

def read_existing_content(file_path):
    """Читает существующий файл / Read existing file"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def find_focus_tree_start(content):
    """
    Проверяет наличие 'focus_tree = {' в файле
    Check if 'focus_tree = {' exists in file
    Возвращает / Returns: (found, indent_level)
    """
    if not content:
        return False, 0
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('focus_tree = {'):
            indent = len(line) - len(line.lstrip(' '))
            return True, indent
    return False, 0

def get_tree_id_from_path(file_path):
    """
    Извлекает id дерева фокусов из имени файла (без расширения)
    Extract focus tree id from filename (without extension)
    """
    basename = os.path.basename(file_path)
    tree_id = os.path.splitext(basename)[0]
    return tree_id

def get_tag_from_prefix(prefix):
    """
    Извлекает тэг страны из префикса (удаляет последний символ, если это '_')
    Extract country tag from prefix (removes trailing '_' if present)
    """
    tag = prefix.rstrip('_')
    return tag

def generate_country_block(tree_id, tag):
    """
    Генерирует блок country для дерева фокусов
    Generate country block for focus tree
    """
    lines = []
    lines.append(f"\tid = {tree_id}")
    lines.append("\tcountry = {")
    lines.append("\t\tfactor = 0")
    lines.append("\t\tmodifier = {")
    lines.append("\t\t\tadd = 10")
    lines.append(f"\t\t\ttag = {tag}")
    lines.append("\t\t}")
    lines.append("\t}")
    lines.append("\tdefault = no")
    return '\n'.join(lines)

def generate_focus(focus_id, focus_number, total_focuses, cost_value, 
                   use_relative_position, ai_value):
    """
    Генерирует текст одного фокуса / Generate one focus block
    """
    lines = []
    
    lines.append("\tfocus = {")
    lines.append(f"\t\tid = {focus_id}")
    lines.append("\t\ticon = GFX_goal_unknown")
    
    # cost / стоимость (если задан / if provided)
    if cost_value is not None:
        lines.append(f"\t\tcost = {cost_value}")
    
    # prerequisite / предварительные требования (всегда пустой / always empty)
    lines.append("\t\tprerequisite = { }")
    
    # координаты / coordinates
    y_coord = focus_number - 1
    lines.append(f"\t\tx = 0")
    lines.append(f"\t\ty = {y_coord}")
    
    # relative_position_id (для всех фокусов, кроме первого, если включено)
    # for all focuses except first, if enabled
    if use_relative_position and focus_number > 1:
        first_focus_id = focus_id.rsplit('_', 1)[0] + "_1"
        lines.append(f"\t\trelative_position_id = {first_focus_id}")
    
    # completion_reward / награда за выполнение (всегда пустой / always empty)
    lines.append("\t\tcompletion_reward = { }")
    
    # ai_will_do (если задан / if provided)
    if ai_value is not None:
        lines.append(f"\t\tai_will_do = {{")
        lines.append(f"\t\t\tbase = {ai_value}")
        lines.append(f"\t\t}}")
    
    lines.append("\t}")
    return '\n'.join(lines)

def generate_new_tree_content(tree_id, tag, focus_count, cost_value, 
                               use_relative_position, ai_value):
    """
    Генерирует полное содержимое нового файла дерева фокусов (с нуля)
    Generate full content for new focus tree file (from scratch)
    """
    lines = []
    lines.append("focus_tree = {")
    lines.append(generate_country_block(tree_id, tag))
    lines.append("")
    lines.append("\tcontinuous_focus_position = { x = 0 y = 2000 }")
    lines.append("")
    
    for i in range(1, focus_count + 1):
        focus_id = f"{tag}_focus_{i}" if tag else f"{prefix}focus_{i}"
        lines.append(generate_focus(focus_id, i, focus_count, cost_value, 
                                     use_relative_position, ai_value))
        if i < focus_count:
            lines.append("")
    
    lines.append("}")
    return '\n'.join(lines)

def add_focuses_to_existing_tree(content, tag, focus_count, cost_value, 
                                  use_relative_position, ai_value):
    """
    Добавляет фокусы в существующее дерево
    Add focuses to existing tree
    """
    existing_lines = content.split('\n')
    new_lines = []
    inserted = False
    
    for line in existing_lines:
        new_lines.append(line)
        # Вставляем фокусы после строки continuous_focus_position
        # Insert focuses after continuous_focus_position line
        if not inserted and 'continuous_focus_position' in line:
            new_lines.append("")
            for i in range(1, focus_count + 1):
                focus_id = f"{tag}_focus_{i}" if tag else f"{prefix}focus_{i}"
                new_lines.append(generate_focus(focus_id, i, focus_count, cost_value,
                                                 use_relative_position, ai_value))
                if i < focus_count:
                    new_lines.append("")
            new_lines.append("")
            inserted = True
    
    return '\n'.join(new_lines)

def main():
    """Основная функция / Main function"""
    print("=" * 60)
    print("Скрипт 1: Генерация каркаса дерева национальных фокусов")
    print("Script 1: Generate national focus tree framework")
    print("=" * 60)
    print()
    
    # Проверка настроек / Validate settings
    print("[INFO] Настройки / Settings:")
    print(f"       - Файл / File: {FILE_PATH}")
    print(f"       - Количество фокусов / Focus count: {FOCUS_COUNT}")
    print(f"       - Префикс / Prefix: {PREFIX}")
    print(f"       - Cost: {COST_LIST[0] if COST_LIST else 'НЕ БУДЕТ / NOT CREATED'}")
    print(f"       - Relative position: {'ВКЛ / ON' if USE_RELATIVE_POSITION else 'ВЫКЛ / OFF'}")
    print(f"       - AI will do: {AI_WILL_DO_LIST[0] if AI_WILL_DO_LIST else 'НЕ БУДЕТ / NOT CREATED'}")
    print()
    
    # Валидация / Validation
    if FOCUS_COUNT < 1:
        print("[ERROR] Количество фокусов должно быть больше 0 / Focus count must be > 0")
        return
    
    cost_value = COST_LIST[0] if COST_LIST else None
    ai_value = AI_WILL_DO_LIST[0] if AI_WILL_DO_LIST else None
    
    # Получаем id дерева из имени файла / Get tree id from filename
    tree_id = get_tree_id_from_path(FILE_PATH)
    # Получаем тэг из префикса / Get tag from prefix
    tag = get_tag_from_prefix(PREFIX)
    
    print(f"[INFO] ID дерева фокусов / Focus tree ID: {tree_id}")
    print(f"[INFO] Тэг страны / Country tag: {tag}")
    print()
    
    # Создаём директорию при необходимости / Create directory if needed
    ensure_directory_exists(FILE_PATH)
    
    # Читаем существующий файл / Read existing file
    existing_content = read_existing_content(FILE_PATH)
    
    if existing_content:
        print("[INFO] Файл существует / File exists. Проверка focus_tree...")
        has_focus_tree, _ = find_focus_tree_start(existing_content)
        if has_focus_tree:
            print("[INFO] focus_tree найден. Фокусы будут добавлены.")
            print("[INFO] focus_tree found. Focuses will be added.")
            new_content = add_focuses_to_existing_tree(existing_content, tag, FOCUS_COUNT,
                                                        cost_value, USE_RELATIVE_POSITION, ai_value)
        else:
            print("[INFO] focus_tree не найден. Будет создано новое дерево.")
            print("[INFO] focus_tree not found. New tree will be created.")
            new_content = generate_new_tree_content(tree_id, tag, FOCUS_COUNT,
                                                     cost_value, USE_RELATIVE_POSITION, ai_value)
    else:
        print("[INFO] Файл не существует / File does not exist. Будет создан новый файл.")
        new_content = generate_new_tree_content(tree_id, tag, FOCUS_COUNT,
                                                 cost_value, USE_RELATIVE_POSITION, ai_value)
    
    # Записываем файл / Write file
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print()
    print(f"[SUCCESS] Файл успешно записан / File written: {FILE_PATH}")
    print(f"[SUCCESS] Создано фокусов / Focuses created: {FOCUS_COUNT}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()