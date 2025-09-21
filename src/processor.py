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
    usando o objeto ReviewRaw original como a fonte da verdade para os
    dados originais.
    """
    data = safe_json_load(llm_response)

    try:
        # Pydantic fará a maior parte do trabalho de validação e limpeza
        processed_review = ReviewProcessed(
            user=review_raw.user,
            original=review_raw.text,
            language=review_raw.language,  # Passa o idioma
            **data
        )
        logger.info(
            "Análise detalhada do LLM validada para o usuário: %s", processed_review.user
        )
        return processed_review
    except ValidationError as e:
        logger.warning(
            "Erro de validação Pydantic para o usuário '%s'. Erros: %s", review_raw.user, e
        )
        # O fallback agora inclui os novos campos
        return ReviewProcessed(
            user=review_raw.user,
            original=review_raw.text,
            translation_pt=data.get(
                "translation_pt", "Dados de tradução ausentes ou inválidos."
            ),
            sentiment="neutral",
            language=review_raw.language,
            intensity="Baixa",  # Fallback seguro
            aspects=[],  # Fallback seguro
            explanation="Falha na análise detalhada do LLM."  # Fallback seguro
        )

def analyze_reviews(
    processed: Iterable[ReviewProcessed],
    separator: str = " || "
) -> Tuple[Counter, str]:
    """
    Analisa uma lista de resenhas processadas para contar sentimentos e concatenar textos.
    """
    processed_list = list(processed)
    logger.info("Analisando %d resenhas processadas...", len(processed_list))
    counts = Counter(r.sentiment for r in processed_list)
    all_texts = separator.join(f"{r.user}: {r.original}" for r in processed_list)
    logger.info("Contagem de sentimentos: %s", counts)
    return counts, all_texts
