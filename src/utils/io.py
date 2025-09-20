"""
Utilitários para entrada e saída de dados.
"""

import json
from pathlib import Path
from typing import Iterable
from src.models import ReviewProcessed

def save_json(data: Iterable[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)

def save_text(text: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
