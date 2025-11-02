from pathlib import Path
from hoi4dev import CCL2Dict, Dict2CCL

pathlist = Path("../common/decisions").glob("*.*")
decisions = {}

default_ai = {'base' : 1}

for path in pathlist:
    with open(path, 'r', encoding='utf-8') as f:
        decisions = CCL2Dict(f.read())
    print(path)
    for cat in decisions:
        for name in decisions[cat]:
            decision = decisions[cat][name]
            if decision == []: continue
            if not 'ai_will_do' in decision:
                try:
                    decision['ai_will_do'] = default_ai
                except:
                    print(decision)
                    exit()
    output = Dict2CCL(decisions)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(output)
