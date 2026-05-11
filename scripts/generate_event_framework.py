#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# НАСТРОЙКИ - МЕНЯЙ ТОЛЬКО ЗДЕСЬ / SETTINGS - CHANGE ONLY THIS
# ============================================================

# ПОЛНЫЙ ПУТЬ ОПЕРАЦИОННОЙ СИСТЕМЫ К ФАЙЛУ ДЛЯ РЕДАКТИРОВАНИЯ / FULL OC (WINDOWS/LINUX/MAC) PATH TO THE FILE FOR EDITING
EVENT_FILE_PATH = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/events/Kingdom_Akorn.txt"

# СКОЛЬКО СОБЫТИЙ ТЫ ХОЧЕШЬ ДОБАВИТЬ / HOW MANY EVENTS DO YOU WANT TO ADD
EVENT_COUNT = 10

# НОМЕР ПЕРВОГО СОБЫТИЯ, КОТОРОЕ ТЫ ДОБАВЛЯЕШЬ. НУМЕРАЦИЯ ИДЁТ С НЕГО / NUMBER OF THE FIRST EVENT THAT YOU WANT TO ADD. NUMERATION STARTS FROM HERE
START_NUMBER = 2

# НЕЙМСПЕЙС ("ТЕГ") ДЛЯ ДОБАВЛЯЕМЫХ ТОБОЙ СОБЫТИЙ / NAMESPACE FOR EVENTS THAT YOU WANT TO ADD
NAMESPACE = "koa.leftists"

# КАРТИНКА ПО УМОЛЧАНИЮ ДЛЯ ДОБАВЛЯЕМЫХ ТОБОЙ СОБЫТИЙ / DEFAULT PICTURE FOR THE EVENTS THAT YOU WANT TO ADD
DEFAULT_PICTURE = "GFX_report_event_generic"

# ЕСЛИ СОБЫТИЕ ДОЛЖНО ИМЕТЬ ВОЗМОЖНОСТЬ ПОВТОРЯТЬСЯ - ИСПОЛЬЗУЙ False / IF THE EVENT MUST BE ABLE TO HAPPEN AGAIN - USE False
FIRE_ONLY_ONCE = True

# ЕСЛИ СОБЫТИЕ ДОЛЖНО ВЫЗЫВАТЬСЯ ТОЛЬКО ПО ТРЕБОВАНИЮ, А НЕ ПО СОВПАДЕНИЮ УСЛОВИЙ - ИСПОЛЬЗУЙ True / IF THE EVENT MUST BE ACTIVATED ONLY BY DEMAND AND NOT BY CONDITOINS - USE True
IS_TRIGGERED_ONLY = True

# ============================================================
# КОД - НЕ МЕНЯТЬ / CODE - DO NOT EDIT
# ============================================================

import os
import re
import sys

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[INFO] Создана директория: {directory}")

def read_existing_content(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def has_add_namespace(content, namespace):
    if not content:
        return False
    pattern = rf'^add_namespace\s*=\s*{re.escape(namespace)}\s*$'
    return bool(re.search(pattern, content, re.MULTILINE))

def generate_event(num, namespace, picture, fire_once, triggered):
    return f"""country_event = {{
	id = {namespace}.{num}
	title = {namespace}.{num}.t
	desc = {namespace}.{num}.d
	picture = {picture}
	fire_only_once = yes
	is_triggered_only = yes
	option = {{
		name = {namespace}.{num}.a
	}}
}}"""

def generate_events_file(content, namespace, count, start, picture, fire_once, triggered):
    namespace_line = f"add_namespace = {namespace}"
    
    new_events = []
    for i in range(start, start + count):
        new_events.append(generate_event(i, namespace, picture, fire_once, triggered))
    
    if not content or not content.strip():
        result = [namespace_line, "", *new_events]
        return '\n'.join(result)
    
    has_ns = has_add_namespace(content, namespace)
    
    result = []
    if not has_ns:
        result.append(namespace_line)
        result.append("")
    
    result.append(content.rstrip())
    result.append("")
    result.extend(new_events)
    
    return '\n'.join(result)

def write_event_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[INFO] Файл сохранён: {file_path}")

def main():
    print("=" * 60)
    print("Скрипт 3: Генерация каркаса событий")
    print("=" * 60)
    print()
    
    print("[INFO] Настройки:")
    print(f"       - Файл событий: {EVENT_FILE_PATH}")
    print(f"       - Количество событий: {EVENT_COUNT}")
    print(f"       - Стартовый номер: {START_NUMBER}")
    print(f"       - Неймспейс: {NAMESPACE}")
    print()
    
    if EVENT_COUNT < 1:
        print("[ERROR] Количество событий должно быть > 0")
        return
    
    ensure_directory_exists(EVENT_FILE_PATH)
    existing_content = read_existing_content(EVENT_FILE_PATH)
    
    if existing_content:
        print("[INFO] Файл существует.")
    else:
        print("[INFO] Файл не существует. Будет создан новый.")
    
    new_content = generate_events_file(existing_content, NAMESPACE, EVENT_COUNT, START_NUMBER,
                                        DEFAULT_PICTURE, FIRE_ONLY_ONCE, IS_TRIGGERED_ONLY)
    
    write_event_file(EVENT_FILE_PATH, new_content)
    
    print()
    print(f"[SUCCESS] Создано событий: {EVENT_COUNT}")
    print(f"[INFO] Номера: {START_NUMBER} - {START_NUMBER + EVENT_COUNT - 1}")
    print("=" * 60)

if __name__ == "__main__":
    main()