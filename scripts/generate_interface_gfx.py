#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт: Автоматическая генерация .gfx файла для текстур интерфейса HOI4
Sons of Mobius Development Tools

Что делает скрипт:
- Сканирует указанную папку с текстурами (.dds).
- Автоматически создает или перезаписывает .gfx файл интерфейса.
- Прописывает правильные пути относительно корневой папки мода.
"""

import os
from pathlib import Path

# ============================================================
# НАСТРОЙКИ / SETTINGS - ИЗМЕНЯЙТЕ ЗНАЧЕНИЯ ТОЛЬКО ТУТ
# ============================================================

# 1. Путь к корневой папке вашего мода (где лежат папки /gfx, /interface и т.д.)
MOD_FOLDER = r"C:/Users/Admin/Documents/Paradox Interactive/Hearts of Iron IV/mod/sonic017"

# 2. Папка, где лежат новые текстуры интерфейса (скрипт найдет файлы и внутри подпапок)
TEXTURES_FOLDER_NAME = "gfx/interface/production"

# 3. Путь и имя для создаваемого .gfx файла (обычно в папке /interface)
OUTPUT_GFX_FILE = "interface/som_production_generated.gfx"

# ============================================================
# КОД СКРИПТА - НЕ ИЗМЕНЯЙТЕ БЕЗ НЕОБХОДИМОСТИ
# ============================================================

def main():
    print("=" * 60)
    print("[START] Запуск генератора .gfx файлов интерфейса")
    print("=" * 60)

    # Превращаем пути в объекты Path для надежной работы во всех ОС
    base_mod = Path(MOD_FOLDER)
    target_textures = base_mod / TEXTURES_FOLDER_NAME
    output_file = base_mod / OUTPUT_GFX_FILE

    # ПРОВЕРКА 1: Существует ли папка мода
    if not base_mod.exists():
        print(f"[ERROR] Корневая папка мода не найдена по пути:\n        {MOD_FOLDER}")
        print("[INFO] Проверьте правильность пути в блоке НАСТРОЙКИ.")
        return

    # ПРОВЕРКА 2: Существует ли папка с текстурами
    if not target_textures.exists():
        print(f"[ERROR] Папка с текстурами не найдена:\n        {target_textures}")
        print("[INFO] Убедитесь, что папка TEXTURES_FOLDER_NAME указана верно.")
        return

    # Поиск всех файлов .dds (включая вложенные папки)
    print(f"[INFO] Сканирование папки: {TEXTURES_FOLDER_NAME}...")
    dds_files = list(target_textures.rglob("*.dds"))
    print(f"[INFO] Найдено текстур (.dds): {len(dds_files)}")

    if not dds_files:
        print("[WARN] В указанной папке нет файлов .dds. Создавать .gfx не из чего.")
        return

    # Подготовка содержимого .gfx файла
    lines = []
    lines.append("spriteTypes = {")
    lines.append("") # Пустая строка для красоты

    # Обработка каждой найденной текстуры
    for file_path in dds_files:
        # Имя спрайта для HOI4 (например: GFX_production_bg)
        # file_path.stem берет только имя файла без .dds
        sprite_name = f"GFX_{file_path.stem}"
        
        # Относительный путь для HOI4 (например: gfx/interface/production/bg.dds)
        # .as_posix() гарантирует правильные слэши '/' в файле игры
        relative_texture_path = file_path.relative_to(base_mod).as_posix()

        # Формируем блок spriteType с лаконичными отступами
        lines.append("\tspriteType = {")
        lines.append(f'\t\tname = "{sprite_name}"')
        lines.append(f'\t\ttexturefile = "{relative_texture_path}"')
        lines.append("\t}")
        lines.append("") # Отступ между блоками

    lines.append("}")

    # Сборка всего текста в одну строку
    gfx_content = "\n".join(lines)

    # Создаем папку для .gfx файла, если её вдруг нет (например, /interface)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Запись готового файла
    print(f"[INFO] Запись данных в файл: {OUTPUT_GFX_FILE}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(gfx_content)

    print()
    print(f"[SUCCESS] Файл успешно сгенерирован и сохранен!")
    print(f"[SUCCESS] Путь: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()