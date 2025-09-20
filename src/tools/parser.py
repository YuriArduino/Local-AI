"""
Parser de linhas de texto para ReviewRaw.
"""

from typing import Tuple
from src.models import ReviewRaw

def parse_txt_line(line: str) -> ReviewRaw:
    # split max 2 para permitir "$" na resenha
    parts = line.strip().split("$", 2)
    if len(parts) < 3:
        parts += [""] * (3 - len(parts))
    id_, user, text = parts
    return ReviewRaw(id=id_.strip(), user=user.strip(), text=text.strip())
