"""
Teste unitário para a função detect_language em text_utils.py.
"""

import pytest
from src.tools.text_utils import detect_language

# Casos de teste para a função detect_language
DETECT_LANGUAGE_CASES = [
    ("This is a wonderful library.", "en"),
    ("Eu amo pizza e programação.", "pt"),
    ("Je suis très content de ce produit.", "fr"),
    ("Das ist eine sehr gute Idee.", "de"),
    ("Esto es una prueba en español.", "es"),
    # Caso com texto muito curto, que deve falhar a detecção
    ("Hi", "unknown"),
    # Caso com texto sem palavras reconhecíveis
    ("1234567890!@#$%^&*", "unknown"),
    # Caso com string vazia
    ("", "unknown"),
    # Caso com texto em japonês
    ("これは日本語のテストです。", "ja"),
]

@pytest.mark.parametrize("text, expected_language", DETECT_LANGUAGE_CASES)
def test_detect_language(text: str, expected_language: str):
    """
    Testa a função detect_language com diferentes idiomas e casos de borda.

    Args:
        text: O texto de entrada para a função.
        expected_language: O código de idioma esperado como saída.
    """
    detected_lang = detect_language(text)
    assert detected_lang == expected_language
