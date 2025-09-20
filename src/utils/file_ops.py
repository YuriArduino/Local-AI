"""
Script para salvar dados processados em JSON e texto.
"""

import json
from pathlib import Path
from typing import Iterable
from src.models import ReviewProcessed
    
def save_processed_json(reviews: Iterable[ReviewProcessed], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        data = [r.model_dump() for r in reviews]  # pydantic v2 -> model_dump()
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_summary_txt(counts, concatenated: str, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("Contagem de sentiments:\n")
        for k, v in counts.items():
            f.write(f"{k}: {v}\n")
        f.write("\nConcatenado:\n")
        f.write(concatenated)
