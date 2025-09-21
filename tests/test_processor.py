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
# input_review_raw,
# llm_response,
# expected_sentiment,
# expected_translation,
# expected_intensity,
# expected_aspects,
# expected_explanation
# )

TEST_CASES = [
    # 1. Caso de sucesso com JSON perfeito
    (
        "perfect_json",
        ReviewRaw(id="1", user="John Doe", text="This app is great!", language="en"),
        '''{
            "translation_pt": "Este aplicativo é ótimo!",
            "sentiment": "positive",
            "intensity": "Alta",
            "aspects": ["usabilidade", "desempenho"],
            "explanation": "O usuário está muito satisfeito."
        }''',
        "positive", "Este aplicativo é ótimo!", "Alta", ["usabilidade", "desempenho"], "O usuário está muito satisfeito.",
    ),
    # 2. Caso com JSON mal formatado (vírgula extra)
    (
        "malformed_json",
        ReviewRaw(id="2", user="Jane Doe", text="Some original text.", language="en"),
        '{"sentiment": "neutral"},,',
        "neutral", "Dados de tradução ausentes ou inválidos.", "Baixa", [], "Falha na análise detalhada do LLM.",
    ),
    # 3. Caso com campo obrigatório faltando ('sentiment')
    (
        "missing_field",
        ReviewRaw(id="3", user="Peter Pan", text="I hate it.", language="en"),
        '{"translation_pt": "Eu odeio isso."}',
        "neutral", "Eu odeio isso.", "Baixa", [], "Falha na análise detalhada do LLM.",
    ),
    # 4. Caso com valor inválido para 'sentiment'
    (
        "invalid_value",
        ReviewRaw(id="4", user="Wendy", text="Amazing!", language="en"),
        '{"translation_pt": "Incrível!", "sentiment": "happy"}',
        "neutral", "Incrível!", "Baixa", [], "Falha na análise detalhada do LLM.",
    ),
    # 5. Caso com uma string vazia como resposta
    (
        "empty_string",
        ReviewRaw(id="5", user="Test User", text="Empty response test", language="en"),
        "",
        "neutral", "Dados de tradução ausentes ou inválidos.", "Baixa", [], "Falha na análise detalhada do LLM.",
    ),
    # 6. Caso com JSON que não corresponde ao modelo (chaves diferentes)
    (
        "mismatched_keys",
        ReviewRaw(id="6", user="Hook", text="Bad form!", language="en"),
        '{"feeling": "negative"}',
        "neutral", "Dados de tradução ausentes ou inválidos.", "Baixa", [], "Falha na análise detalhada do LLM.",
    ),
    # 7. Caso com 'intensity' inválida, deve usar fallback inteligente
    (
        "invalid_intensity",
        ReviewRaw(id="7", user="Smee", text="Very good!", language="en"),
        # Adicionamos os campos faltantes para que a validação passe após a normalização da intensidade.
        '''{
            "translation_pt": "Muito bom!",
            "sentiment": "positive",
            "intensity": "fortissima",
            "aspects": ["geral"],
            "explanation": "O usuário está satisfeito."
        }''',
        # O validador do modelo deve corrigir a intensidade para "Média" e o resto deve ser mantido.
        "positive", "Muito bom!", "Média", ["geral"], "O usuário está satisfeito.",
    ),
    # 8. Caso com 'aspects' como string, deve ser convertido para lista
    (
        "aspects_as_string",
        ReviewRaw(id="8", user="Tinkerbell", text="Fast and beautiful", language="en"),
        '{"translation_pt": "Rápido e bonito", "sentiment": "positive", "intensity": "Alta", "aspects": "desempenho, design", "explanation": "Satisfeito com a velocidade e aparência."}',
        "positive", "Rápido e bonito", "Alta", ["desempenho", "design"], "Satisfeito com a velocidade e aparência.",
    ),
]

@pytest.mark.parametrize(
    "test_name, review_input, llm_response, expected_sentiment, expected_translation, expected_intensity, expected_aspects, expected_explanation",
    TEST_CASES,
    ids=[c[0] for c in TEST_CASES],
)
def test_map_llm_response_to_processed(
    test_name: str,
    review_input: ReviewRaw,
    llm_response: str,
    expected_sentiment: str,
    expected_translation: str,
    expected_intensity: str,
    expected_aspects: list,
    expected_explanation: str,
):
    """
    Testa a função map_llm_response_to_processed com vários cenários.
    """
    # Executa a função que está sendo testada
    result = map_llm_response_to_processed(review_input, llm_response)

    # Valida se a função SEMPRE retorna um objeto do tipo correto
    assert isinstance(result, ReviewProcessed), f"[{test_name}] O resultado não é uma instância de ReviewProcessed."

    # Valida que os dados originais são sempre preservados
    assert result.user == review_input.user, f"[{test_name}] Falha na preservação do usuário."
    assert result.original == review_input.text, f"[{test_name}] Falha na preservação do texto original."
    assert result.language == review_input.language, f"[{test_name}] Falha na preservação do idioma."

    # Valida os campos processados
    assert result.sentiment == expected_sentiment, f"[{test_name}] Falha na validação do sentimento."
    assert result.translation_pt == expected_translation, f"[{test_name}] Falha na validação da tradução."
    assert result.intensity == expected_intensity, f"[{test_name}] Falha na validação da intensidade."
    assert result.aspects == expected_aspects, f"[{test_name}] Falha na validação dos aspectos."
    assert result.explanation == expected_explanation, f"[{test_name}] Falha na validação da explicação."

def test_analyze_reviews_logic():
    """
    Testa a lógica de análise da função analyze_reviews.

    Valida se a contagem de sentimentos e a concatenação de strings
    estão funcionando como esperado.
    """
    # 1. Cria uma lista de entrada de resenhas processadas
    processed_reviews_list = [
        ReviewProcessed(user="UserA", original="Great!", translation_pt="Ótimo!", sentiment="positive", language="en", intensity="Alta", aspects=["geral"], explanation="Bom"),
        ReviewProcessed(user="UserB", original="Bad.", translation_pt="Ruim.", sentiment="negative", language="en", intensity="Média", aspects=["geral"], explanation="Ruim"),
        ReviewProcessed(user="UserC", original="It's ok.", translation_pt="Está ok.", sentiment="neutral", language="en", intensity="Baixa", aspects=["geral"], explanation="Ok"),
        ReviewProcessed(user="UserD", original="Amazing!", translation_pt="Incrível!", sentiment="positive", language="en", intensity="Alta", aspects=["geral"], explanation="Ótimo"),
    ]

    # 2. Executa a função de análise
    counts, concatenated_string = analyze_reviews(processed_reviews_list, separator=" | ")

    # 3. Confere o resultado da contagem
    expected_counts = {"positive": 2, "negative": 1, "neutral": 1}
    assert counts == expected_counts, f"A contagem de sentimentos falhou. Esperado: {expected_counts}, Obtido: {counts}"

    # 4. Valida a string concatenada
    expected_string = "UserA: Great! | UserB: Bad. | UserC: It's ok. | UserD: Amazing!"
    assert concatenated_string == expected_string, "A string concatenada está incorreta."
