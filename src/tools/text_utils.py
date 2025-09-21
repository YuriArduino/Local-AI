"""
Funções utilitárias para manipulação e limpeza de texto.

Estas funções são genéricas e não possuem conhecimento sobre o
domínio da aplicação (resenhas, sentimentos, etc.).
"""
import re
import unicodedata
import logging
from langdetect import detect, LangDetectException

def normalize_whitespace(text: str) -> str:
    """
    Substitui múltiplos espaços, tabulações e quebras de linha por um único espaço.

    Args:
        text: A string de entrada.

    Returns:
        A string com o espaçamento normalizado.
    """
    return re.sub(r'\s+', ' ', text).strip()

def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove caracteres especiais, exceto pontuação básica se especificado.

    Args:
        text: A string de entrada.
        keep_punctuation: Se True, mantém pontuações comuns (., !, ?).

    Returns:
        A string limpa.
    """
    # Normaliza para decompor caracteres acentuados (ex: 'é' -> 'e' + '´')
    nfkd_form = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    if keep_punctuation:
        # Mantém letras, números, espaços e pontuação básica
        return re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    else:
        # Mantém apenas letras, números e espaços
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """
    Detecta o idioma principal de um texto usando a biblioteca langdetect.

    Retorna o código do idioma (ex: 'en', 'pt', 'fr') ou 'unknown' em caso de erro.

    Args:
        text: O texto a ser analisado.

    Returns:
        O código do idioma detectado ou 'unknown' se a detecção falhar.
    """
    # A detecção de idioma é pouco confiável em textos muito curtos.
    # Retorna 'unknown' para textos com menos de 10 caracteres não-espaço
    # para evitar falsos positivos como o que ocorreu no teste.
    if len(text.strip()) < 10:
        logger.debug("Texto muito curto para detecção de idioma confiável: '%s'", text)
        return "unknown"

    try:
        # Retorna apenas os 2 primeiros caracteres (ex: 'en' em vez de 'en-US')
        return detect(text)[:2]
    except LangDetectException:
        # Retorna 'unknown' se o texto for muito curto ou a detecção falhar
        logger.debug("langdetect não conseguiu determinar o idioma para o texto: '%s'", text[:50])
        return "unknown"
