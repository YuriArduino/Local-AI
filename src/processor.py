"""
Processa, valida e analisa as resenhas.
"""
import logging
from collections import Counter
from typing import Iterable, Tuple

from pydantic import ValidationError
from src.models import ReviewRaw, ReviewProcessed
from src.utils.helpers import safe_json_load

logger = logging.getLogger(__name__)

def map_llm_response_to_processed(review_raw: ReviewRaw, llm_response: str) -> ReviewProcessed:
    """
    Converte a resposta JSON do LLM em um objeto ReviewProcessed validado,
    usando o objeto ReviewRaw original como a fonte da verdade.
    """
    data = safe_json_load(llm_response)

    try:
        # Garante que a resposta do LLM seja um dicionário para desempacotamento.
        if not isinstance(data, dict):
            raise TypeError(f"A resposta do LLM não é um dicionário, mas sim um {type(data).__name__}.")

        processed_review = ReviewProcessed(
            user=review_raw.user,
            original=review_raw.text,
            **data
        )
        logger.info("Resposta do LLM validada com sucesso para o usuário: %s", processed_review.user)
        return processed_review
    except (ValidationError, TypeError) as e:
        logger.warning(
            "Erro de validação ou tipo para o usuário '%s'. JSON recebido: %s. Erros: %s",
            review_raw.user, data, e
        )
        # Fallback: usa o review_raw como fonte da verdade para os dados originais.
        translation = "Dados de tradução ausentes ou inválidos."
        if isinstance(data, dict):
            translation = data.get("translation_pt", translation)

        return ReviewProcessed(
            user=review_raw.user,
            original=review_raw.text,
            translation_pt=translation,
            sentiment="neutral"
        )

def analyze_reviews(processed: Iterable[ReviewProcessed], separator: str = " || ") -> Tuple[Counter, str]:
    """Analisa uma lista de resenhas processadas para contar sentimentos e concatenar textos."""
    processed_list = list(processed)
    logger.info("Analisando %d resenhas processadas...", len(processed_list))
    counts = Counter(r.sentiment for r in processed_list)
    all_texts = separator.join(f"{r.user}: {r.original}" for r in processed_list)
    logger.info("Contagem de sentimentos: %s", counts)
    return counts, all_texts
