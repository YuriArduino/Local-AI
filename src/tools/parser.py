"""
Parser de linhas de texto para ReviewRaw e leitura de arquivos .txt.
Lê um arquivo .txt e retorna uma lista de ReviewRaw.
"""

import logging
import re
from pathlib import Path
from typing import List
from src.models import ReviewRaw
# Importa as funções de utilidade de texto
from src.tools.text_utils import normalize_whitespace, detect_language

logger = logging.getLogger(__name__)

def parse_single_review_string(full_review_text: str) -> ReviewRaw:
    """
    Converte uma string de resenha completa (potencialmente multi-linha) em um objeto ReviewRaw.
    """
    parts = full_review_text.strip().split("$", 2)

    id_, user, text = "invalid_id", "Invalid Format", ""

    if len(parts) >= 2:
        # Assume que o formato é pelo menos ID$TEXTO
        id_, text_content = parts[0], parts[1]
        user = "Unknown User" # Padrão para o caso de 2 partes

        if len(parts) == 3:
            # Caminho feliz: ID$User$Text
            user, text = parts[1], parts[2]
        else:
            # Caso de 2 partes: ID$UserText
            # Tenta encontrar um nome de usuário razoável (ex: duas primeiras palavras)
            # Esta é uma heurística e pode ser ajustada.
            potential_user = " ".join(text_content.split()[:2])
            if len(potential_user) < 30: # Evita que a resenha inteira vire o nome do usuário
                user = potential_user
                text = " ".join(text_content.split()[2:])
            else:
                text = text_content # Mantém o usuário como "Unknown"
            log_msg = (
                "Linha mal formatada encontrada (provavelmente faltando delimitador '$'). "
                "Tentando inferir usuário e texto. Linha: '%s...'"
            )
            logger.warning(log_msg, full_review_text[:70])
    else:
        # Caso completamente quebrado
        text = full_review_text.strip()
        logger.error(
            "Linha completamente mal formatada não pôde ser parseada. Linha: '%s...'",
             full_review_text[:70]
        )

    cleaned_text = normalize_whitespace(text)
    detected_lang = detect_language(cleaned_text)

    return ReviewRaw(
        id=id_.strip(),
        user=user.strip(),
        text=cleaned_text,
        language=detected_lang
    )

def read_reviews_from_file(file_path: Path) -> List[ReviewRaw]:
    """
    Lê um arquivo .txt de resenhas, lidando corretamente com entradas que
    abrangem múltiplas linhas.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"O arquivo de resenhas não foi encontrado em: {file_path}")

    reviews: List[ReviewRaw] = []
    current_review_lines: List[str] = []

    # Expressão regular para detectar o início de uma nova resenha (ex: "12345$...")
    review_start_pattern = re.compile(r"^\d+\$.*")

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Verifica se a linha atual marca o início de uma NOVA resenha
            if review_start_pattern.match(line) and current_review_lines:
                # Se sim, processa a resenha que acabamos de coletar
                full_review_text = " ".join(current_review_lines)
                reviews.append(parse_single_review_string(full_review_text))

                # Inicia uma nova resenha
                current_review_lines = [line.strip()]
            else:
                # Se não, é uma linha de continuação ou a primeira linha do arquivo
                current_review_lines.append(line.strip())

    # Não se esqueça de processar a última resenha do arquivo após o loop
    if current_review_lines:
        full_review_text = " ".join(current_review_lines)
        reviews.append(parse_single_review_string(full_review_text))

    return reviews
