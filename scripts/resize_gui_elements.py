#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт: Массовый масштабатор окон и контейнеров интерфейса (.gui) HOI4
Sons of Mobius Development Tools (Версия с точечным парсингом строк)
"""

import os
import re
import shutil
from pathlib import Path

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ ТОЛЬКО ТУТ
# ============================================================

TARGET_GUI_FILE = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017/interface/countrytechtreeview.gui"

RESIZE_TARGETS = {
    "technology_tech_stat_item": (15, 0),        # Изменяем на +15 по ширине
    "countrytechtreeview": (50, 50),             # Проверим главное окно для кучи
}

# ============================================================
# КОД СКРИПТА
# ============================================================

def main():
    print("=" * 60)
    print("[START] Запуск Точечного Масштабатора интерфейса")
    print("=" * 60)

    gui_path = Path(TARGET_GUI_FILE)

    if not gui_path.exists():
        print(f"[ERROR] Файл интерфейса не найден по пути:\n        {TARGET_GUI_FILE}")
        return

    if not RESIZE_TARGETS:
        print("[WARN] Список RESIZE_TARGETS пуст.")
        return

    print(f"[INFO] Целевой файл: {gui_path.name}")
    
    backup_path = gui_path.with_suffix(gui_path.suffix + ".bak")
    print(f"[INFO] Создаем бэкап файла в: {backup_path.name}")
    shutil.copyfile(gui_path, backup_path)

    with open(gui_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    success_count = 0

    print("-" * 60)
    print("[PROCESS] Начинаем поиск контейнеров...")
    print("-" * 60)

    for container_name, (mod_width, mod_height) in RESIZE_TARGETS.items():
        if mod_width == 0 and mod_height == 0:
            continue

        found_container = False
        changed = False

        name_pattern = re.compile(r'name\s*=\s*"' + re.escape(container_name) + r'"')

        for i in range(len(lines)):
            line = lines[i]
            
            if line.strip().startswith("#"):
                continue

            if name_pattern.search(line):
                found_container = True
                
                # Ищем size вниз от имени (в пределах 15 строк)
                for j in range(max(0, i - 5), min(len(lines), i + 15)):
                    size_line = lines[j]
                    
                    if "size" in size_line and not size_line.strip().startswith("#"):
                        # Извлекаем числа через простые регулярки без привязки к %
                        w_match = re.search(r"width\s*=\s*([0-9%]+)", size_line)
                        h_match = re.search(r"height\s*=\s*([0-9%]+)", size_line)
                        
                        if w_match and h_match:
                            w_str = w_match.group(1).strip()
                            h_str = h_match.group(1).strip()
                            
                            # Пропускаем, если там проценты (динамический размер)
                            if "%" in w_str or "%" in h_str:
                                continue
                            
                            # Считаем новые значения
                            new_w = str(int(w_str) + mod_width)
                            new_h = str(int(h_str) + mod_height)
                            
                            # Делаем точную замену подстроки в строке
                            new_line = size_line
                            new_line = re.sub(r"width\s*=\s*" + w_str, f"width={new_w}", new_line)
                            new_line = re.sub(r"height\s*=\s*" + h_str, f"height={new_h}", new_line)
                            
                            lines[j] = new_line
                            print(f"[SUCCESS] Изменен '{container_name}': W({w_str} -> {new_w}), H({h_str} -> {new_h})")
                            changed = True
                            success_count += 1
                            break
                if changed:
                    break

        if not found_container:
            print(f"[WARN] Контейнер '{container_name}' вообще не обнаружен в файле.")
        elif not changed:
            print(f"[WARN] Контейнер '{container_name}' пропущен (размер в % или нет жесткого size).")

    if success_count > 0:
        with open(gui_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("-" * 60)
        print(f"[FINISH] Обработка завершена. Успешно изменено: {success_count}")
    else:
        print("-" * 60)
        print("[INFO] Ни один контейнер не изменен.")
    print("=" * 60)

if __name__ == "__main__":
    main()