from pathlib import Path
from hoi4dev import CCL2Dict, Dict2CCL

pathlist = Path("../history/states").rglob("*")
state_json = {}

for path in pathlist:
    with open(path, 'r', encoding='utf-8') as f:
        state_json = CCL2Dict(f.read())
    if 'resources' in state_json['state']:
        resources = state_json['state']['resources']
        for k in resources:
            resources[k] = resources[k] // 2
        state_json['state']['resources'] = resources
    output = Dict2CCL(state_json)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(output)
