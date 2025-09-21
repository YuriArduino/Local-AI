"""
Testes unitários para o módulo processor.

Estes testes não fazem chamadas de rede e validam a lógica de
parsing e validação da função `map_llm_response_to_processed`.
"""

import pytest
from src.models import ReviewProcessed
from src.processor import map_llm_response_to_processed

# Casos de teste com diferentes tipos de respostas do LLM
TEST_CASES = [
    # 1. Caso de sucesso com JSON perfeito
    (
        "perfect_json",
        '''
        {
            "user": "John Doe",
            "original": "This app is great!",
            "translation_pt": "Este aplicativo é ótimo!",
            "sentiment": "positive"
        }
        ''',
        "John Doe", "positive", "Este aplicativo é ótimo!"
    ),
    # 2. Caso com JSON mal formatado (vírgula extra)
    (
        "malformed_json",
        '{"user": "Jane Doe", "sentiment": "neutral"},,',
        "ERRO_PARSING", "neutral", "A resposta do LLM não pôde ser decodificada."
    ),
    # 3. Caso com campo obrigatório faltando ('sentiment')
    (
        "missing_field",
        '{"user": "Peter Pan", "original": "I hate it.", "translation_pt": "Eu odeio isso."}',
        "Peter Pan", "neutral", "Eu odeio isso."
    ),
    # 4. Caso com valor inválido para 'sentiment'
    (
        "invalid_value",
        '''
        {
            "user": "Wendy",
            "original": "Amazing!",
            "translation_pt": "Incrível!",
            "sentiment": "happy"
        }
        ''',
        "Wendy", "neutral", "Incrível!"
    ),
    # 5. Caso com uma string vazia como resposta
    (
        "empty_string",
        "",
        "ERRO_PARSING", "neutral", "A resposta do LLM não pôde ser decodificada."
    ),
    # 6. Caso com JSON que não corresponde ao modelo (chaves diferentes)
    (
        "mismatched_keys",
        '{"username": "Hook", "review": "Bad form!", "feeling": "negative"}',
        "ERRO_VALIDACAO", "neutral", "Dados de tradução ausentes ou inválidos."
    ),
]

@pytest.mark.parametrize(
    "test_name, llm_response, expected_user, expected_sentiment, expected_translation",
    TEST_CASES
)
def test_map_llm_response_to_processed(
    test_name: str,
    llm_response: str,
    expected_user: str,
    expected_sentiment: str,
    expected_translation: str
):
    """
    Testa a função map_llm_response_to_processed com vários cenários.

    Args:
        test_name: Um identificador descritivo para o caso de teste.
        llm_response: A string de resposta simulada do LLM.
        expected_user: O valor esperado para o campo 'user'.
        expected_sentiment: O valor esperado para o campo 'sentiment'.
        expected_translation: O valor esperado para o campo 'translation_pt'.
    """
    # Executa a função que está sendo testada
    result = map_llm_response_to_processed(llm_response)

    # Valida se a função SEMPRE retorna um objeto do tipo correto
    assert isinstance(result, ReviewProcessed), f"[{test_name}] O resultado não é uma instância de ReviewProcessed."

    # Valida os campos do objeto retornado
    assert result.user == expected_user, f"[{test_name}] Falha na validação do usuário."
    assert result.sentiment == expected_sentiment, f"[{test_name}] Falha na validação do sentimento."
    assert result.translation_pt == expected_translation, f"[{test_name}] Falha na validação da tradução."
    # O campo 'original' deve ser igual ao valor extraído ou ao fallback
    if expected_user not in ("ERRO_PARSING", "ERRO_VALIDACAO"):
        assert result.original not in (
            "ERRO_PARSING",
            "ERRO_VALIDACAO",
        ), f"[{test_name}] Falha na validação do campo original."
    else:
        assert result.original in (
            "ERRO_PARSING",
            "ERRO_VALIDACAO",
        ), f"[{test_name}] Falha na validação do campo original."
