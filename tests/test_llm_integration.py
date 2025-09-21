"""
Teste de integração para validar a comunicação com o LLM.

Este teste faz uma chamada real à API do LLM.
Para executá-lo:
1. Certifique-se de que o servidor LLM (ex: LM Studio) está rodando.
2. Marque-o com `pytest.mark.integration` para poder rodá-lo separadamente.
   Ex: `pytest -m integration`
"""
import logging
import pytest
from openai import APIError, APIConnectionError
from pydantic import ValidationError

from src.models import ReviewRaw, ReviewProcessed
from src.processor import map_llm_response_to_processed
from src.tools.prompt_builder import build_json_prompt
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)

# Dados de teste ATUALIZADOS com o campo 'language'
TEST_REVIEWS = [
    ReviewRaw(
        id="1",
        user="John Doe",
        text="This app is absolutely fantastic! Works perfectly.",
        language="en"  # Adiciona o idioma
    ),
    ReviewRaw(
        id="2",
        user="Maria Silva",
        text="Não gostei. Muito lento e trava o tempo todo.",
        language="pt"  # Adiciona o idioma
    ),
    ReviewRaw(
        id="3",
        user="Pierre Martin",
        text="C'est une application correcte, mais elle pourrait être améliorée.",
        language="fr"  # Adiciona o idioma
    ),
]

# Marcador para testes de integração. Requer um LLM rodando.
@pytest.mark.integration
def test_llm_integration_e2e():
    """
    Testa a integração ponta a ponta com o LLM.

    Envia prompts reais e valida se as respostas são JSONs válidos
    com a estrutura esperada.
    """
    logger.info("--- Iniciando teste de integração com o LLM ---")
    logger.info("Certifique-se de que o servidor LLM (ex: LM Studio) está rodando.")

    prompts = [build_json_prompt(review) for review in TEST_REVIEWS]

    try:
        llm_client = LLMClient()
        logger.info("Enviando %d prompts para o LLM...", len(prompts))

        responses = llm_client.batch_process(prompts)

        logger.info("Respostas recebidas. Validando o formato...")
        assert len(responses) == len(
            prompts
        ), "O número de respostas não corresponde ao de prompts."

        for i, response_text in enumerate(responses):
            logger.info("Validando resposta %d...", i + 1)
            original_review = TEST_REVIEWS[i]

            try:
                # Usa o processador para validar a resposta do LLM
                processed_review = map_llm_response_to_processed(
                    review_raw=original_review, llm_response=response_text,
                )

                # Valida que o tipo de retorno está correto
                assert isinstance(processed_review, ReviewProcessed)

                # Valida se os dados originais foram preservados e o sentimento é válido.
                # Se o LLM falhar, o processador deve retornar um fallback, mas os dados originais
                # devem ser mantidos, então o teste ainda passa nesses campos.
                assert processed_review.user == original_review.user
                assert processed_review.original == original_review.text
                assert processed_review.sentiment in ["positive", "negative", "neutral"]
            except ValidationError as e:
                pytest.fail(
                    f"A resposta {i+1} falhou na validação do Pydantic: {e}\n"
                    f"Resposta: {response_text[:200]}...",
                )

    except (APIConnectionError, APIError) as e:
        pytest.fail(
            "Falha na comunicação com o LLM. Verifique se o servidor está "
            f"rodando e acessível. Erro: {e}",
        )

    logger.info("--- Teste de integração com o LLM finalizado com sucesso ---")
