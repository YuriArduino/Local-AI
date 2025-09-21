"""
Parser de linhas de texto para ReviewRaw e leitura de arquivos .txt.
Lê um arquivo .txt e retorna uma lista de ReviewRaw.
"""

from pathlib import Path
from typing import List
from src.models import ReviewRaw

def parse_txt_line(line: str) -> ReviewRaw:
    """
    Converte uma única linha do arquivo .txt em um objeto ReviewRaw.
    Lida com linhas que podem ter menos de 3 partes.
    Args:
        line: Uma linha do arquivo .txt no formato "ID$Usuário$Resenha".
    """
    # split max 2 para permitir "$" na resenha
    parts = line.strip().split("$", 2)
    # Garante que a lista tenha sempre 3 elementos para desempacotamento seguro
    if len(parts) < 3:
        parts.extend([""] * (3 - len(parts)))  # Preenche com strings vazias se necessário
    id_, user, text = parts
    return ReviewRaw(id=id_, user=user, text=text)

def read_reviews_from_file(file_path: Path) -> List[ReviewRaw]:
    """
    Lê um arquivo .txt de resenhas e retorna uma lista de objetos ReviewRaw.

    Args:
        file_path: O caminho (Path) para o arquivo .txt.

    Returns:
        Uma lista de objetos ReviewRaw, um para cada linha válida no arquivo.
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado no caminho especificado.
    """
    if not file_path.is_file():
        # Lança um erro claro se o arquivo não existir
        raise FileNotFoundError(f"O arquivo de resenhas não foi encontrado em: {file_path}")

    reviews: List[ReviewRaw] = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Ignora linhas em branco
            if line.strip():
                review_raw = parse_txt_line(line)
                reviews.append(review_raw)
    return reviews
