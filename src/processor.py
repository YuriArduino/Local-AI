"""
Processa, valida e analisa as resenhas.
"""
import logging
from collections import Counter
from typing import List, Tuple

from pydantic import ValidationError
from src.models import ReviewProcessed
from src.utils.helpers import safe_json_load

logger = logging.getLogger(__name__)

def map_llm_response_to_processed(llm_response: str) -> ReviewProcessed:
    """
    Converte a resposta em string JSON do LLM em um objeto ReviewProcessed validado.

    Esta função é o coração da validação:
    1. Recebe a resposta do LLM.
    2. Converte a string para um dicionário Python.
    3. Usa o Pydantic para validar a estrutura e os valores do dicionário.
    4. Retorna um objeto de fallback em caso de qualquer erro.
    """
    # 1. Tenta carregar a string como um dicionário de forma segura
    data = safe_json_load(llm_response)
    if not data:
        logger.warning("A resposta do LLM não é um JSON válido ou está vazia. Usando fallback.")
        return ReviewProcessed(
            user="ERRO_PARSING",
            original="ERRO_PARSING",
            translation_pt="A resposta do LLM não pôde ser decodificada.",
            sentiment="neutral"
        )

    # 2. Tenta validar os dados com o modelo Pydantic
    try:
        # Pydantic faz a validação de campos, tipos e valores aqui
        processed_review = ReviewProcessed(**data)
        logger.info("Resposta do LLM validada com sucesso para o usuário: %s", processed_review.user)
        return processed_review
    except ValidationError as e:
        logger.warning(
            "Erro de validação Pydantic. JSON recebido: %s. Erros: %s", data, e
        )
        # Cria um objeto de fallback usando os dados que conseguiu extrair
        return ReviewProcessed(
            user=data.get("user", "ERRO_VALIDACAO"),
            original=data.get("original", "ERRO_VALIDACAO"),
            translation_pt=data.get("translation_pt", "Dados de tradução ausentes ou inválidos."),
            sentiment="neutral" # 'neutral' é o fallback mais seguro
        )

def analyze_reviews(processed: List[ReviewProcessed], separator: str = " || ") -> Tuple[Counter, str]:
    """
    Analisa uma lista de resenhas processadas para contar sentimentos e concatenar textos.
    (Esta é a sua função original, que está perfeita).
    """
    logger.info("Analisando %d resenhas processadas...", len(processed))
    counts = Counter(r.sentiment for r in processed)
    all_texts = separator.join(f"{r.user}: {r.original}" for r in processed)
    logger.info("Contagem de sentimentos: %s", counts)
    return counts, all_texts
