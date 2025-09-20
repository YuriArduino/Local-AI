"""
Script para processar resenhas e extrair informações.
"""

import json
from collections import Counter
from typing import List, Tuple
from src.models import ReviewProcessed, ReviewsList, ReviewRaw
import logging

logger = logging.getLogger(__name__)

def map_llm_response_to_processed(user: str, original: str, llm_response: str) -> ReviewProcessed:
    """
    Espera que llm_response contenha JSON com as chaves:
    { "translation_pt": "...", "sentiment": "positive|negative|neutral" }
    Se a resposta não for JSON, tenta inferir (aqui simplificamos, ideal: pedir JSON no prompt).
    """
    try:
        payload = json.loads(llm_response)
        translation = payload.get("translation_pt", "")
        sentiment = payload.get("sentiment", "neutral")
    except Exception:
        # fallback: não conseguir parsear -> colocar como neutro e usar llm_response parcial
        translation = ""
        sentiment = "neutral"
    return ReviewProcessed(user=user, original=original, translation_pt=translation, sentiment=sentiment)

def analyze_reviews(processed: List[ReviewProcessed], separator: str = " || ") -> Tuple[Counter, str]:
    counts = Counter([r.sentiment for r in processed])
    all_texts = separator.join([f"{r.user}: {r.original}" for r in processed])
    return counts, all_texts
