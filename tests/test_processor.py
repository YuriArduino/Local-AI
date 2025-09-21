"""
Testes unitários para o módulo processor.

Estes testes não fazem chamadas de rede e validam a lógica de
parsing e validação da função `map_llm_response_to_processed`.
"""

import pytest
from src.models import ReviewRaw, ReviewProcessed
from src.processor import analyze_reviews, map_llm_response_to_processed

# Casos de teste com diferentes tipos de respostas do LLM
# Formato: (
# test_name,
# input_user,
# input_original,
# llm_response,
# expected_sentiment,
# expected_translation
# )

TEST_CASES = [
    # 1. Caso de sucesso com JSON perfeito
    (
        "perfect_json",
        "John Doe", "This app is great!",
        '{"translation_pt": "Este aplicativo é ótimo!", "sentiment": "positive"}',
        "positive", "Este aplicativo é ótimo!",
    ),
    # 2. Caso com JSON mal formatado (vírgula extra)
    (
        "malformed_json",
        "Jane Doe", "Some original text.",
        '{"sentiment": "neutral"},,',
        "neutral", "Dados de tradução ausentes ou inválidos.",
    ),
    # 3. Caso com campo obrigatório faltando ('sentiment')
    (
        "missing_field",
        "Peter Pan", "I hate it.",
        '{"translation_pt": "Eu odeio isso."}',
        "neutral", "Eu odeio isso.",
    ),
    # 4. Caso com valor inválido para 'sentiment'
    (
        "invalid_value",
        "Wendy", "Amazing!",
        '{"translation_pt": "Incrível!", "sentiment": "happy"}',
        "neutral", "Incrível!",
    ),
    # 5. Caso com uma string vazia como resposta
    (
        "empty_string",
        "Test User", "Empty response test",
        "",
        "neutral", "Dados de tradução ausentes ou inválidos.",
    ),
    # 6. Caso com JSON que não corresponde ao modelo (chaves diferentes)
    (
        "mismatched_keys",
        "Hook", "Bad form!",
        '{"feeling": "negative"}',
        "neutral", "Dados de tradução ausentes ou inválidos.",
    ),
]

@pytest.mark.parametrize(
    "test_name, input_user, input_original, llm_response, expected_sentiment, expected_translation",
    TEST_CASES,
    ids=[c[0] for c in TEST_CASES],
)
def test_map_llm_response_to_processed(
    test_name: str,
    input_user: str,
    input_original: str,
    llm_response: str,
    expected_sentiment: str,
    expected_translation: str
):
    """
    Testa a função map_llm_response_to_processed com vários cenários.
    """
    # Cria o objeto de entrada para o processador
    review_input = ReviewRaw(id="test-id", user=input_user, text=input_original, language="unknown")

    # Executa a função que está sendo testada
    result = map_llm_response_to_processed(review_input, llm_response)

    # Valida se a função SEMPRE retorna um objeto do tipo correto
    assert isinstance(result, ReviewProcessed), f"[{test_name}] O resultado não é uma instância de ReviewProcessed."

    # Valida que os dados originais são sempre preservados
    assert result.user == input_user, f"[{test_name}] Falha na preservação do usuário."
    assert result.original == input_original, f"[{test_name}] Falha na preservação do texto original."

    # Valida os campos processados
    assert result.sentiment == expected_sentiment, f"[{test_name}] Falha na validação do sentimento."
    assert result.translation_pt == expected_translation, f"[{test_name}] Falha na validação da tradução."

def test_analyze_reviews_logic():
    """
    Testa a lógica de análise da função analyze_reviews.

    Valida se a contagem de sentimentos e a concatenação de strings
    estão funcionando como esperado.
    """
    # 1. Cria uma lista de entrada de resenhas processadas
    processed_reviews_list = [
        ReviewProcessed(user="UserA", original="Great!", translation_pt="Ótimo!", sentiment="positive"),
        ReviewProcessed(user="UserB", original="Bad.", translation_pt="Ruim.", sentiment="negative"),
        ReviewProcessed(user="UserC", original="It's ok.", translation_pt="Está ok.", sentiment="neutral"),
        ReviewProcessed(user="UserD", original="Amazing!", translation_pt="Incrível!", sentiment="positive"),
    ]

    # 2. Executa a função de análise
    counts, concatenated_string = analyze_reviews(processed_reviews_list, separator=" | ")

    # 3. Confere o resultado da contagem
    expected_counts = {"positive": 2, "negative": 1, "neutral": 1}
    assert counts == expected_counts, f"A contagem de sentimentos falhou. Esperado: {expected_counts}, Obtido: {counts}"

    # 4. Valida a string concatenada
    expected_string = "UserA: Great! | UserB: Bad. | UserC: It's ok. | UserD: Amazing!"
    assert concatenated_string == expected_string, "A string concatenada está incorreta."
