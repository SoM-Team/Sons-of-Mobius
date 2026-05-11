#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт 2: Заполнение фокусов данными из таблицы для Hearts of Iron IV / Script 2: Fill focuses with data from spreadsheet for Hearts of Iron IV

Что делает скрипт / What this script does:
- Сопоставляет фокусы в файле с записями в таблице по id / Matches focuses in file with records in spreadsheet by id
- Переносит значения из таблицы в соответствующие поля фокуса / Transfers values from spreadsheet to corresponding focus fields
- Пропускает фокусы, не найденные в таблице (с уведомлением) / Skips focuses not found in spreadsheet (with notification)

Как использовать / How to use:
1 .Сделать копию скрипта и не использовать оригинальный скрипт / Make a copy of this script and do not use the original script
2. Заполнить таблицу (шаблон) данными / Fill spreadsheet (template) with data
3. Настроить параметры в блоке "НАСТРОЙКИ" ниже / Define parameters in "SETTINGS" block below
4. Запустить скрипт: python fill_focus_data.py / Launch the script: python fill_focus_data.py
"""

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ / EDIT VALUES HERE
# ============================================================

# Путь к файлу дерева фокусов (.txt) / Path to focus tree file (.txt)
FOCUS_FILE_PATH = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/common/national_focus/UWM_Jack_Red.txt"

# Путь к файлу таблицы (.xlsx, .xls, .csv) / Path to spreadsheet file (.xlsx, .xls, .csv)
# ВНИМАНИЕ: данные вставляются как есть. Запятые будут удалены. / ATTENTION: Data is inserted as-is. Commas will be removed.
TABLE_FILE_PATH = r"C:/Users/Admin/Desktop/United_Workers_of_Mobius_Focus_Tree.xlsx"

# Имя листа в таблице (если не указан - берётся активный лист)
# Sheet name in spreadsheet (if empty - takes active sheet)
SHEET_NAME = "UWM"

# Столбец в таблице, содержащий id фокусов (для сопоставления) / Column in spreadsheet containing focus ids (for matching)
ID_COLUMN = "Technical focus name"

# Словарь сопоставления: "поле_в_файле" : "столбец_в_таблице"
# Mapping dictionary: "field_in_file" : "column_in_spreadsheet"
# 
# Поддерживаемые поля / Supported fields:
# - id          - переименование фокуса / rename focus
# - icon        - иконка / icon
# - cost        - стоимость / cost
# - prerequisite - предварительные требования / prerequisites
# - mutually_exclusive - взаимно исключаемые фокусы
# - completion_reward - награда за выполнение / completion reward
# - ai_will_do  - ИИ выполнит / AI will do

MAPPING_DICT = {
    "completion_reward": "Effects",
    "id": "Technical focus name",
    # "icon": "Icon Status",
    # "cost": "Cost",
    # "prerequisite": "Parent Focuses",
    # "mutually_exclusive": "Mutually Exclusive With",
}

# ============================================================
# КОД СКРИПТА - НИЧЕГО НЕ МЕНЯТЬ / SCRIPT CODE - DO NOT EDIT
# ============================================================

import os
import re
import sys

def remove_commas(text):
    """Удаляет все запятые из текста / Removes all commas from text"""
    if text is None:
        return None
    if not isinstance(text, str):
        text = str(text)
    return text.replace(',', '')

def generate_field_block(field_name, value):
    """
    Генерирует блок для поля фокуса.
    Возвращает строку с правильным форматированием для вставки.
    """
    if value is None or str(value).strip() == "":
        # Пустое значение - вставляем TODO с правильными скобками
        if field_name in ["completion_reward", "ai_will_do", "prerequisite", "mutually_exclusive"]:
            return f"\t\t{field_name} = {{\n\t\t\t# TODO\n\t\t}}"
        else:
            return f"\t\t{field_name} = # TODO"
    
    value_str = remove_commas(str(value))
    
    # Обработка разных типов полей
    if field_name == "ai_will_do":
        try:
            float(value_str)
        except ValueError:
            print(f"[WARN] ai_will_do не число: {value_str}, используется 1")
            value_str = "1"
        return f"\t\tai_will_do = {{\n\t\t\tbase = {value_str}\n\t\t}}"
    
    elif field_name == "completion_reward":
        return f"\t\tcompletion_reward = {{\n\t\t\t{value_str}\n\t\t}}"
    
    elif field_name in ["prerequisite", "mutually_exclusive"]:
        return f"\t\t{field_name} = {{\n\t\t\t{value_str}\n\t\t}}"
    
    else:
        return f"\t\t{field_name} = {value_str}"

def read_spreadsheet(file_path, sheet_name):
    """Читает таблицу и возвращает словарь {id: {column: value}}"""
    try:
        if file_path.endswith('.csv'):
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        else:
            try:
                import openpyxl
            except ImportError:
                print("[ERROR] Для .xlsx/.xls файлов нужна библиотека openpyxl")
                print("[ERROR] Установите: pip install openpyxl")
                print("[ERROR] Или используйте .csv формат")
                sys.exit(1)
            
            wb = openpyxl.load_workbook(file_path, data_only=True)
            
            # Выбираем лист
            if sheet_name and sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                print(f"[INFO] Используется лист / Using sheet: {sheet_name}")
            else:
                ws = wb.active
                if sheet_name:
                    print(f"[WARN] Лист '{sheet_name}' не найден, используется активный: {ws.title}")
                else:
                    print(f"[INFO] Используется активный лист / Using active sheet: {ws.title}")
            
            headers = []
            for col in range(1, ws.max_column + 1):
                val = ws.cell(row=1, column=col).value
                if val:
                    headers.append(str(val))
                else:
                    headers.append(f"Column_{col}")
            
            rows = []
            for row in range(2, ws.max_row + 1):
                row_data = {}
                for col_idx, header in enumerate(headers, start=1):
                    val = ws.cell(row=row, column=col_idx).value
                    if val is not None:
                        row_data[header] = str(val)
                    else:
                        row_data[header] = ""
                if any(v.strip() for v in row_data.values()):
                    rows.append(row_data)
        
        result = {}
        for row in rows:
            focus_id = row.get(ID_COLUMN, "").strip()
            if focus_id:
                result[focus_id] = row
        
        return result
    
    except FileNotFoundError:
        print(f"[ERROR] Файл не найден / File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ошибка чтения таблицы / Error reading spreadsheet: {e}")
        sys.exit(1)

def read_focus_file(file_path):
    """Читает файл фокусов"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] Файл не найден / File not found: {file_path}")
        sys.exit(1)

def extract_focus_blocks(content):
    """
    Извлекает блоки фокусов из содержимого файла.
    Возвращает список словарей с информацией о каждом фокусе.
    """
    pattern = r'\n?\tfocus = \{\n(.*?)\n\t\}'
    matches = re.findall(pattern, content, re.DOTALL)
    
    focuses = []
    for match in matches:
        id_match = re.search(r'^\t\tid = (\S+)', match, re.MULTILINE)
        if id_match:
            focus_id = id_match.group(1)
            focuses.append({
                'id': focus_id,
                'full_block': f"\tfocus = {{\n{match}\n\t}}",
                'inner_content': match
            })
    
    return focuses

def remove_field_from_content(inner_content, field_name):
    """
    Удаляет поле из внутреннего содержимого фокуса.
    Возвращает новое содержимое без указанного поля.
    """
    lines = inner_content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        match = re.match(rf'^\t\t{field_name}\s*=', line)
        
        if match:
            if '{' not in line and '}' not in line:
                i += 1
                continue
            
            brace_level = 0
            j = i
            
            while j < len(lines):
                current_line = lines[j]
                brace_level += current_line.count('{')
                brace_level -= current_line.count('}')
                if brace_level <= 0 and j > i:
                    j += 1
                    break
                j += 1
            
            i = j
            continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)

def update_focus_block(inner_content, new_fields):
    """
    Обновляет блок фокуса: удаляет старые поля и вставляет новые.
    new_fields - словарь {поле: значение_для_вставки}
    """
    # Удаляем все поля, которые будем обновлять
    for field_name in new_fields.keys():
        inner_content = remove_field_from_content(inner_content, field_name)
    
    lines = inner_content.split('\n')
    new_lines = []
    id_line = None
    id_index = -1
    
    # Находим строку с id
    for i, line in enumerate(lines):
        if re.match(r'^\t\tid =', line):
            id_line = line
            id_index = i
            break
    
    if id_index >= 0:
        new_lines.extend(lines[:id_index])
        new_lines.append(id_line)
        for field_name, field_value in new_fields.items():
            if field_value is not None:
                new_lines.append(field_value)
        new_lines.extend(lines[id_index + 1:])
    else:
        new_lines.extend(lines)
        for field_name, field_value in new_fields.items():
            if field_value is not None:
                new_lines.append(field_value)
    
    return '\n'.join(new_lines)

def write_focus_file(file_path, content):
    """Записывает обновлённое содержимое в файл"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[INFO] Файл сохранён / File saved: {file_path}")

def fix_focus_order(content):
    """
    Финальная чистка: приводит все блоки focus к правильному порядку.
    id всегда первым полем после открывающей скобки.
    """
    def reorder_focus_block(match):
        full_match = match.group(0)
        inner = match.group(1)
        
        id_match = re.search(r'^\s*id\s*=\s*(\S+)', inner, re.MULTILINE)
        if not id_match:
            return full_match
        
        id_line = id_match.group(0).strip()
        inner_without_id = re.sub(r'^\s*id\s*=\s*\S+\s*\n?', '', inner, flags=re.MULTILINE)
        
        new_block = f"\tfocus = {{\n\t\t{id_line}\n{inner_without_id}\n\t}}"
        return new_block
    
    pattern = r'\n?\tfocus = \{\n(.*?)\n\t\}'
    new_content = re.sub(pattern, reorder_focus_block, content, flags=re.DOTALL)
    return new_content

def main():
    """Основная функция"""
    print("=" * 60)
    print("Скрипт 2: Заполнение фокусов данными из таблицы")
    print("Script 2: Fill focuses with data from spreadsheet")
    print("=" * 60)
    print()
    
    print("[INFO] Настройки / Settings:")
    print(f"       - Файл фокусов / Focus file: {FOCUS_FILE_PATH}")
    print(f"       - Файл таблицы / Table file: {TABLE_FILE_PATH}")
    print(f"       - Лист таблицы / Sheet name: {SHEET_NAME if SHEET_NAME else '(активный / active)'}")
    print(f"       - Столбец ID / ID column: {ID_COLUMN}")
    print(f"       - Сопоставление / Mapping: {MAPPING_DICT}")
    print()
    
    # 1. Читаем таблицу
    print("[INFO] Чтение таблицы / Reading spreadsheet...")
    table_data = read_spreadsheet(TABLE_FILE_PATH, SHEET_NAME)
    print(f"[INFO] Найдено записей в таблице: {len(table_data)}")
    
    # Выводим первые 5 id для проверки
    if table_data:
        sample_ids = list(table_data.keys())[:5]
        print(f"[INFO] Примеры id из таблицы: {sample_ids}")
    print()
    
    # 2. Читаем файл фокусов
    print("[INFO] Чтение файла фокусов / Reading focus file...")
    file_content = read_focus_file(FOCUS_FILE_PATH)
    
    # 3. Извлекаем блоки фокусов
    focuses = extract_focus_blocks(file_content)
    print(f"[INFO] Найдено фокусов в файле: {len(focuses)}")
    
    # Выводим первые 5 id для проверки
    if focuses:
        sample_focus_ids = [f['id'] for f in focuses[:5]]
        print(f"[INFO] Примеры id из файла: {sample_focus_ids}")
    print()
    
    # 4. Обрабатываем каждый фокус
    updated_focuses = []
    matched_count = 0
    skipped_count = 0
    
    for focus in focuses:
        focus_id = focus['id']
        
        if focus_id not in table_data:
            print(f"[SKIP] Фокус не найден в таблице / Focus not found: {focus_id}")
            skipped_count += 1
            updated_focuses.append(focus['full_block'])
            continue
        
        print(f"[MATCH] Обработка / Processing: {focus_id}")
        matched_count += 1
        
        row_data = table_data[focus_id]
        
        new_fields = {}
        for file_field, table_column in MAPPING_DICT.items():
            raw_value = row_data.get(table_column, "")
            new_fields[file_field] = generate_field_block(file_field, raw_value)
        
        new_inner_content = update_focus_block(focus['inner_content'], new_fields)
        new_full_block = f"\tfocus = {{\n{new_inner_content}\n\t}}"
        updated_focuses.append(new_full_block)
    
    print()
    print(f"[INFO] Обработано фокусов / Processed: {matched_count + skipped_count}")
    print(f"[INFO] Совпадений / Matches: {matched_count}")
    print(f"[INFO] Пропущено / Skipped: {skipped_count}")
    print()
    
    if matched_count == 0:
        print("[WARN] Нет совпадений! Проверьте:")
        print("       1. Имя листа в таблице (SHEET_NAME)")
        print("       2. Столбец ID (ID_COLUMN)")
        print("       3. Совпадение id в файле и таблице")
        print()
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            print("[INFO] Выход / Exiting")
            return
    
    # Заменяем старые блоки фокусов новыми
    new_content = file_content
    for i, focus in enumerate(focuses):
        new_content = new_content.replace(focus['full_block'], updated_focuses[i], 1)
    
    # Финальная чистка
    print("[INFO] Финальная чистка структуры фокусов...")
    new_content = fix_focus_order(new_content)
    
    # Сохраняем файл
    write_focus_file(FOCUS_FILE_PATH, new_content)
    
    print()
    print("=" * 60)
    print("[SUCCESS] Готово / Done")
    print("=" * 60)

if __name__ == "__main__":
    main()