
import json
from pathlib import Path
from typing import Any

def load_json(path: Path):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(path)

def next_id(records):
    return max([int(r.get("id", 0)) for r in records] or [0]) + 1

def append_record(path: Path, record):
    data = load_json(path)
    data.append(record)
    save_json(path, data)

def update_record(path: Path, record_id, replacement):
    data = load_json(path)
    for i, record in enumerate(data):
        if record.get("id") == record_id:
            data[i] = replacement
            break
    save_json(path, data)

def delete_record(path: Path, record_id):
    data = [r for r in load_json(path) if r.get("id") != record_id]
    save_json(path, data)
