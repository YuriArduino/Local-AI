"""
Funções de alto nível para salvar os artefatos de saída do pipeline.

Este módulo conhece os modelos de dados da aplicação (ex: ReviewProcessed)
e formata os dados antes de delegar a escrita para o módulo `io` genérico.
"""

import logging
from collections import Counter
from pathlib import Path
from typing import Iterable

from src.models import ReviewProcessed
from src.utils.io import save_json, save_text


logger = logging.getLogger(__name__)


class FileOpsError(Exception):
    """Exceção personalizada para erros de operações de arquivo."""

def save_processed_json(reviews: Iterable[ReviewProcessed], path: Path):
    """Salva uma lista de resenhas processadas em um arquivo JSON."""
    # 1. Prepara os dados (converte modelos Pydantic para dicionários)
    data_to_save = [r.model_dump() for r in reviews]
    # 2. Delega a escrita para a função genérica de salvar JSON
    save_json(data_to_save, path)
    logger.info("Arquivo JSON processado salvo em: %s", path)


def save_summary_txt(counts: Counter, concatenated: str, path: Path):
    """Salva a contagem de sentimentos e o texto concatenado em um arquivo de texto."""
    # 1. Formata o conteúdo do sumário como uma única string
    summary_parts = ["Contagem de sentimentos:"]
    summary_parts.extend(f"{k}: {v}" for k, v in counts.items())
    summary_parts.append("\nConcatenado:")
    summary_parts.append(concatenated)
    summary_content = "\n".join(summary_parts)
    # 2. Delega a escrita para a função genérica de salvar texto
    save_text(summary_content, path)
    logger.info("Arquivo de sumário salvo em: %s", path)
