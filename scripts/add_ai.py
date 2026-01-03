from pathlib import Path
import re

pathlist = Path("../common/national_focus").glob("*.*")

ai = r"""    ai_will_do = {
            base = 1
        }
    """

for path in pathlist:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
        ends = []
        it = re.finditer(r'^\s*(shared_)?focus\s*=\s*\{', code, flags=re.M)
        for focus in it:
            count = 1
            for i, c in enumerate(code[focus.end():], start=focus.end()):
                if c == '{':
                    count += 1
                if c == '}':
                    count -= 1
                if count == 0:
                    if re.search(r'ai_will_do', code[focus.end():i]) is None:
                        ends.append(i)
                    break
        for e in ends[::-1]:
            code = code[0:e] + ai + code[e:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
