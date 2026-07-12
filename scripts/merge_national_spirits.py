#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт 5: Объединение национальных духов для Hearts of Iron IV
Script 5: Merge national spirits for Hearts of Iron IV
"""

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ / EDIT VALUES HERE
# ============================================================

# Путь к файлу национальных духов (.txt) / Path to national spirits file (.txt)
SPIRIT_FILE_PATH = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/common/ideas/NOR.txt"

# Список названий национальных духов для объединения (с префиксом)
SPIRIT_NAMES = [
    "NOR_New_Liberty",
    "NOR_Northamerian_Great_Mission",
]

# Имя для объединённого духа (с префиксом) / Name for the merged spirit (with prefix)
MERGED_SPIRIT_NAME = "NOR_Northamerian_Great_Mission_2"

# Картинка для объединённого духа / Picture for the merged spirit
MERGED_PICTURE = "GFX_idea_generic"

# Список элементов для объединения
ELEMENTS_TO_MERGE = [
    "modifier",
    "on_add",
    "on_remove",
    "targeted_modifier",
    "allowed",
    "available",
    "cancel_if_invalid",
    "research_bonus",
    "equipment_bonus",
]

# ============================================================
# КОД СКРИПТА - НИЖЕ НИЧЕГО НЕ МЕНЯТЬ / SCRIPT CODE - DO NOT EDIT BELOW
# ============================================================

import os
import re
import sys

def read_spirit_file(file_path):
    """Читает файл национальных духов"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[ERROR] Файл не найден / File not found: {file_path}")
        sys.exit(1)

def write_spirit_file(file_path, content):
    """Записывает содержимое в файл"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[INFO] Файл сохранён / File saved: {file_path}")

def extract_spirit_blocks(content):
    """Извлекает блоки национальных духов из содержимого файла."""
    pattern = r'\t([A-Za-z0-9_]+)\s*=\s*\{'
    spirits = {}
    
    for match in re.finditer(pattern, content):
        spirit_id = match.group(1)
        start_pos = match.start()
        brace_level = 0
        end_pos = start_pos
        
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_level += 1
            elif content[i] == '}':
                brace_level -= 1
                if brace_level == 0:
                    end_pos = i + 1
                    break
        
        spirits[spirit_id] = content[start_pos:end_pos]
    
    return spirits

def parse_modifier_block(block_text):
    """Парсит блок modifier и возвращает словарь {ключ: значение}"""
    result = {}
    if not block_text:
        return result
    
    match = re.search(r'modifier\s*=\s*\{([^}]*)\}', block_text, re.DOTALL)
    if not match:
        return result
    
    content = match.group(1)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        kv_match = re.match(r'^([a-zA-Z0-9_]+)\s*=\s*(.+?)\s*$', line)
        if kv_match:
            key = kv_match.group(1)
            value_str = kv_match.group(2)
            
            try:
                if '.' in value_str:
                    value = float(value_str)
                else:
                    value = int(value_str)
                result[key] = result.get(key, 0) + value
            except ValueError:
                if key in result and result[key] != value_str:
                    print(f"[WARN] Нечисловое значение для '{key}': '{value_str}' не совпадает с '{result[key]}'")
                else:
                    result[key] = value_str
    
    return result

def parse_simple_block(block_text, block_name):
    """Парсит простой блок (allowed, available, on_add и т.д.)"""
    pattern = rf'{block_name}\s*=\s*\{{([^}}]*)\}}'
    match = re.search(pattern, block_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def parse_cancel_if_invalid(block_text):
    """Парсит cancel_if_invalid"""
    match = re.search(r'cancel_if_invalid\s*=\s*(yes|no)', block_text)
    if match:
        return match.group(1)
    return None

def parse_picture(block_text):
    """Парсит picture"""
    match = re.search(r'picture\s*=\s*(\S+)', block_text)
    if match:
        return match.group(1)
    return None

def merge_modifiers(spirits_data):
    """Объединяет модификаторы из всех духов"""
    merged = {}
    for spirit_id, blocks in spirits_data.items():
        if 'modifier' in blocks and blocks['modifier']:
            mod_dict = parse_modifier_block(blocks['modifier'])
            for key, value in mod_dict.items():
                if key in merged:
                    if isinstance(value, (int, float)) and isinstance(merged[key], (int, float)):
                        merged[key] += value
                    else:
                        if merged[key] != value:
                            print(f"[WARN] Нечисловое значение для '{key}': '{value}' не совпадает с '{merged[key]}'")
                else:
                    merged[key] = value
    return merged

def merge_simple_element(spirits_data, element_name):
    """Объединяет простой элемент (allowed, available, on_add и т.д.)"""
    values = []
    for spirit_id, blocks in spirits_data.items():
        if element_name in blocks and blocks[element_name]:
            values.append(blocks[element_name])
    
    if not values:
        return None
    
    first = values[0]
    for i, val in enumerate(values[1:], 2):
        if val != first:
            print(f"[WARN] {element_name} не совпадает для разных духов")
            print(f"       Дух 1: {first[:50]}...")
            print(f"       Дух {i}: {val[:50]}...")
    
    return first

def merge_cancel_if_invalid(spirits_data):
    """Объединяет cancel_if_invalid"""
    values = []
    for spirit_id, blocks in spirits_data.items():
        if 'cancel_if_invalid' in blocks and blocks['cancel_if_invalid']:
            values.append(blocks['cancel_if_invalid'])
    
    if not values:
        return None
    
    first = values[0]
    for i, val in enumerate(values[1:], 2):
        if val != first:
            print(f"[WARN] cancel_if_invalid не совпадает: {first} vs {val}")
    
    return first

def generate_modifier_block(modifier_dict):
    """Генерирует блок modifier из словаря с округлением float до 3 знаков"""
    if not modifier_dict:
        return "\t\tmodifier = { }"
    
    lines = ["\t\tmodifier = {"]
    for key, value in modifier_dict.items():
        if isinstance(value, float):
            # Округляем до 3 знаков после запятой и убираем лишние нули на конце (.250 -> .25)
            formatted_value = f"{value:.3f}".rstrip('0').rstrip('.')
            lines.append(f"\t\t\t{key} = {formatted_value}")
        else:
            lines.append(f"\t\t\t{key} = {value}")
    lines.append("\t\t}")
    return '\n'.join(lines)

def generate_simple_block(block_name, content):
    """Генерирует простой блок"""
    if not content:
        return None
    return f"\t\t{block_name} = {{\n\t\t\t{content}\n\t\t}}"

def generate_spirit_block(spirit_id, picture, elements):
    """Генерирует полный блок национального духа"""
    lines = []
    lines.append(f"\t{spirit_id} = {{")
    
    if elements.get('allowed'):
        lines.append(f"\t\tallowed = {{\n\t\t\t{elements['allowed']}\n\t\t}}")
    if elements.get('available'):
        lines.append(f"\t\tavailable = {{\n\t\t\t{elements['available']}\n\t\t}}")
    
    lines.append(f"\t\tpicture = {picture}")
    
    if elements.get('cancel_if_invalid'):
        lines.append(f"\t\tcancel_if_invalid = {elements['cancel_if_invalid']}")
    if elements.get('modifier'):
        lines.append(elements['modifier'])
    if elements.get('on_add'):
        lines.append(f"\t\ton_add = {{\n\t\t\t{elements['on_add']}\n\t\t}}")
    if elements.get('on_remove'):
        lines.append(f"\t\ton_remove = {{\n\t\t\t{elements['on_remove']}\n\t\t}}")
    if elements.get('targeted_modifier'):
        lines.append(f"\t\ttargeted_modifier = {{\n\t\t\t{elements['targeted_modifier']}\n\t\t}}")
    if elements.get('research_bonus'):
        lines.append(f"\t\tresearch_bonus = {{\n\t\t\t{elements['research_bonus']}\n\t\t}}")
    if elements.get('equipment_bonus'):
        lines.append(f"\t\tequipment_bonus = {{\n\t\t\t{elements['equipment_bonus']}\n\t\t}}")
    
    lines.append("\t}")
    return '\n'.join(lines)

def spirit_exists(content, spirit_id):
    """Проверяет, существует ли уже дух в файле"""
    pattern = r'\t' + re.escape(spirit_id) + r'\s*=\s*\{'
    return bool(re.search(pattern, content))

def add_spirit_to_file(content, spirit_block):
    """Добавляет новый дух в файл перед предпоследней закрывающей скобкой"""
    lines = content.split('\n')
    
    # Ищем закрывающие скобки с конца файла
    close_braces_indices = [i for i, line in enumerate(lines) if line.strip() == "}"]
    
    # Чтобы вставить внутрь country = { ... }, нам нужна предпоследняя скобка
    if len(close_braces_indices) < 2:
        print("[WARN] Недостаточно уровней вложенности. Пробуем вставить перед последней скобкой.")
        if not close_braces_indices:
            print("[ERROR] Не найдена структура файла (отсутствуют закрывающие скобки).")
            return content
        insert_index = close_braces_indices[-1]
    else:
        insert_index = close_braces_indices[-2]
    
    new_lines = lines[:insert_index]
    new_lines.append("")
    new_lines.append(spirit_block)
    new_lines.append("")
    new_lines.extend(lines[insert_index:])
    
    return '\n'.join(new_lines)

def update_spirit_in_file(content, spirit_block, spirit_id):
    """Заменяет существующий дух новым блоком"""
    pattern = r'\t' + re.escape(spirit_id) + r'\s*=\s*\{[^{}]*\}(?:[^{}]*\})*[^{}]*\}'
    new_content = re.sub(pattern, spirit_block, content, flags=re.DOTALL)
    
    if new_content == content:
        return add_spirit_to_file(content, spirit_block)
    return new_content

def main():
    print("=" * 60)
    print("Скрипт 5: Объединение национальных духов")
    print("=" * 60)
    
    content = read_spirit_file(SPIRIT_FILE_PATH)
    all_spirits = extract_spirit_blocks(content)
    
    spirits_to_merge = {}
    for spirit_name in SPIRIT_NAMES:
        if spirit_name in all_spirits:
            spirits_to_merge[spirit_name] = all_spirits[spirit_name]
            print(f"[OK] Найден дух: {spirit_name}")
        else:
            print(f"[WARN] Дух не найден: {spirit_name}")
    
    if len(spirits_to_merge) < 2:
        print("[ERROR] Нужно хотя бы 2 духа для объединения")
        sys.exit(1)
    
    parsed_spirits = {}
    for spirit_id, block in spirits_to_merge.items():
        parsed = {}
        for element in ELEMENTS_TO_MERGE:
            if element == "modifier":
                parsed[element] = block
            elif element == "cancel_if_invalid":
                val = parse_cancel_if_invalid(block)
                if val: parsed[element] = val
            elif element == "picture":
                val = parse_picture(block)
                if val: parsed[element] = val
            else:
                val = parse_simple_block(block, element)
                if val: parsed[element] = val
        parsed_spirits[spirit_id] = parsed

    merged_elements = {}
    for element in ELEMENTS_TO_MERGE:
        if element == "modifier":
            merged_elements[element] = generate_modifier_block(merge_modifiers(parsed_spirits))
        elif element == "cancel_if_invalid":
            val = merge_cancel_if_invalid(parsed_spirits)
            if val: merged_elements[element] = val
        elif element == "picture":
            merged_elements[element] = MERGED_PICTURE
        else:
            val = merge_simple_element(parsed_spirits, element)
            if val: merged_elements[element] = val
    
    new_spirit_block = generate_spirit_block(MERGED_SPIRIT_NAME, MERGED_PICTURE, merged_elements)
    
    if spirit_exists(content, MERGED_SPIRIT_NAME):
        new_content = update_spirit_in_file(content, new_spirit_block, MERGED_SPIRIT_NAME)
    else:
        new_content = add_spirit_to_file(content, new_spirit_block)
    
    write_spirit_file(SPIRIT_FILE_PATH, new_content)
    print("[SUCCESS] Объединение завершено")

if __name__ == "__main__":
    main()