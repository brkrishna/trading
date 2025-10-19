import csv
import json
from pathlib import Path
from typing import List, Dict

def write_candidates_csv(path: Path, candidates: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not candidates:
        with open(path, 'w', newline='') as f:
            f.write('')
        return
    keys = list(candidates[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for c in candidates:
            writer.writerow({k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in c.items()})

def write_candidates_json(path: Path, candidates: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(candidates, f, indent=2, default=str)
