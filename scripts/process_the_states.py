import os
import re

# ==============================================================================
# НАСТРОЙКИ СКРИПТА
# ==============================================================================

STATES_DIR = r"C:\Users\Admin\Documents\Paradox Interactive\Hearts of Iron IV\mod\sonic017\history\states"
TARGET_STATES = [471, 472, 473, 474, 475, 476, 435, 436, 437, 438, 414]

NEW_STATE_CATEGORY = None
MODIFY_MANPOWER = 0

REMOVE_CORES = []
ADD_CORES = ["KUE"]
REMOVE_CLAIMS = []
ADD_CLAIMS = []

MODIFY_RESOURCES = {
    "steel": 0
}

MODIFY_BUILDINGS = {
    "infrastructure": 0
}

NEW_OWNER = "KUE"

# ==============================================================================
# РАБОЧИЙ КОД
# ==============================================================================

def update_block_content(lines, start_idx, end_idx, modify_dict):
    """Обновляет или добавляет значения внутри существующего KV-блока (resources/buildings)."""
    block_lines = lines[start_idx+1:end_idx]
    updated_block = []
    present_keys = set()

    # Изменяем существующие ключи
    for line in block_lines:
        match = re.search(r'([\w_]+)\s*=\s*(-?\d+)', line)
        if match:
            key, val = match.group(1), int(match.group(2))
            if key in modify_dict:
                present_keys.add(key)
                new_val = max(0, val + modify_dict[key])
                if new_val > 0: # 0 удаляем для оптимизации
                    line = re.sub(r'=\s*-?\d+', f'= {new_val}', line)
                    updated_block.append(line)
                continue
        updated_block.append(line)

    # Добавляем новые ключи, которых не было в блоке
    for key, mod_val in modify_dict.items():
        if key not in present_keys and mod_val > 0:
            # Пытаемся сохранить отступ
            indent = "\t\t\t" if "buildings" in lines[start_idx] else "\t\t"
            updated_block.append(f"{indent}{key} = {mod_val}\n")

    return lines[:start_idx+1] + updated_block + lines[end_idx:]


def find_block_bounds(lines, block_name, parent_start=0, parent_end=None):
    """Ищет индексы начала и конца блока с учётом вложенности."""
    if parent_end is None:
        parent_end = len(lines)
        
    for idx in range(parent_start, parent_end):
        line = lines[idx].strip()
        # Исключаем комментарии
        if line.startswith("#"):
            continue
        if block_name in line and "{" in line:
            # Нашли начало, ищем закрывающую скобку
            brace_count = 1
            for end_idx in range(idx + 1, len(lines)):
                c_line = lines[end_idx]
                brace_count += c_line.count('{') - c_line.count('}')
                if brace_count == 0:
                    return idx, end_idx
    return None, None


def process_state_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Извлекаем ID для проверки на всякий случай
    state_id = None
    for line in lines:
        if not line.strip().startswith("#"):
            match = re.search(r'\bid\s*=\s*(\d+)', line)
            if match:
                state_id = int(match.group(1))
                break

    # Ищем границы главных блоков
    hist_start, hist_end = find_block_bounds(lines, "history")

    # 1. Изменение manpower
    if MODIFY_MANPOWER != 0:
        for idx, line in enumerate(lines):
            if "manpower" in line and "=" in line and not line.strip().startswith("#"):
                match = re.search(r'manpower\s*=\s*(\d+)', line)
                if match:
                    new_mp = max(1, round(int(match.group(1)) + MODIFY_MANPOWER))
                    lines[idx] = re.sub(r'=\s*\d+', f'= {new_mp}', line)
                    break

    # 2. Изменение state_category
    if NEW_STATE_CATEGORY:
        for idx, line in enumerate(lines):
            if "state_category" in line and "=" in line and not line.strip().startswith("#"):
                lines[idx] = re.sub(r'=\s*[\w_]+', f'= {NEW_STATE_CATEGORY}', line)
                break

    # 3. Изменение ресурсов (resources)
    if any(v != 0 for v in MODIFY_RESOURCES.values()):
        res_start, res_end = find_block_bounds(lines, "resources")
        if res_start is not None:
            lines = update_block_content(lines, res_start, res_end, MODIFY_RESOURCES)
            # Обновляем индексы истории, так как массив строк изменился
            hist_start, hist_end = find_block_bounds(lines, "history")

    # 4. Работа внутри блока history
    if hist_start is not None:
        history_lines = lines[hist_start:hist_end+1]
        
        # Новый owner
        if NEW_OWNER:
            for idx in range(hist_start, hist_end):
                if "owner" in lines[idx] and not lines[idx].strip().startswith("#"):
                    lines[idx] = re.sub(r'=\s*[\w_]+', f'= {NEW_OWNER}', lines[idx])
                    break

        # Удаление старых корок / претензий
        if REMOVE_CORES or REMOVE_CLAIMS:
            filtered_lines = []
            for line in lines[hist_start:hist_end]:
                clean = line.strip()
                if clean.startswith("add_core_of"):
                    core = clean.split("=")[1].strip()
                    if core in REMOVE_CORES:
                        continue
                if clean.startswith("add_claim_of"):
                    claim = clean.split("=")[1].strip()
                    if claim in REMOVE_CLAIMS:
                        continue
                filtered_lines.append(line)
            
            lines = lines[:hist_start] + filtered_lines + lines[hist_end:]
            hist_end = hist_start + len(filtered_lines)

        # Добавление новых корок / претензий
        # Проверяем, каких корок ещё нет в файле
        existing_history_text = "".join(lines[hist_start:hist_end])
        
        cores_to_add = [c for c in ADD_CORES if f"add_core_of = {c}" not in existing_history_text and f"add_core_of={c}" not in existing_history_text]
        claims_to_add = [c for c in ADD_CLAIMS if f"add_claim_of = {c}" not in existing_history_text and f"add_claim_of={c}" not in existing_history_text]

        if cores_to_add or claims_to_add:
            insertion_idx = hist_start + 1 # Вставляем сразу после открытия history = {
            added_entries = []
            for core in cores_to_add:
                added_entries.append(f"\t\tadd_core_of = {core}\n")
            for claim in claims_to_add:
                added_entries.append(f"\t\tadd_claim_of = {claim}\n")
            lines = lines[:insertion_idx] + added_entries + lines[insertion_idx:]
            hist_end += len(added_entries)

        # Изменение зданий (buildings) внутри history
        if any(v != 0 for v in MODIFY_BUILDINGS.values()):
            bld_start, bld_end = find_block_bounds(lines, "buildings", parent_start=hist_start, parent_end=hist_end)
            if bld_start is not None:
                lines = update_block_content(lines, bld_start, bld_end, MODIFY_BUILDINGS)

    # Сохраняем файл обратно
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def main():
    if not os.path.exists(STATES_DIR):
        print(f"[Ошибка] Указанный путь не существует: {STATES_DIR}")
        return

    print("Запуск безопасной обработки регионов...")
    processed_count = 0

    for filename in os.listdir(STATES_DIR):
        if filename.endswith(".txt"):
            match = re.match(r'^(\d+)', filename)
            if match:
                state_id = int(match.group(1))
                if state_id in TARGET_STATES:
                    filepath = os.path.join(STATES_DIR, filename)
                    try:
                        process_state_file(filepath)
                        print(f"-> Успешно изменен: {filename}")
                        processed_count += 1
                    except Exception as e:
                        print(f"[Ошибка] Не удалось обработать {filename}: {e}")

    print(f"\nВсего обработано файлов: {processed_count}")

if __name__ == "__main__":
    main()