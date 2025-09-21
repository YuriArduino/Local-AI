"""
Teste de integração para validar a comunicação com o LLM.

Este teste faz uma chamada real à API do LLM.
Para executá-lo:
1. Certifique-se de que o servidor LLM (ex: LM Studio) está rodando.
2. Marque-o com `pytest.mark.integration` para poder rodá-lo separadamente.
   Ex: `pytest -m integration`
"""
import logging
import json
import pytest
from openai import APIError, APIConnectionError
from pydantic import ValidationError

from src.models import ReviewRaw, ReviewProcessed
from src.tools.prompt_builder import build_json_prompt
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)

# Dados de teste
TEST_REVIEWS = [
    ReviewRaw(
        id="1",
        user="John Doe",
        text="This app is absolutely fantastic! Works perfectly."
    ),
    ReviewRaw(
        id="2",
        user="Maria Silva",
        text="Não gostei. Muito lento e trava o tempo todo."
    ),
    ReviewRaw(
        id="3",
        user="Pierre Martin",
        text="C'est une application correcte, mais elle pourrait être améliorée."
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
        assert len(responses) == len(TEST_REVIEWS), "O número de respostas não corresponde ao de prompts."

        for i, response_text in enumerate(responses):
            logger.info("Validando resposta %d...", i + 1)
            try:
                # Remove blocos de markdown, se existirem
                response_text = response_text.strip()
                if response_text.startswith("```"):
                    # Remove o início do bloco
                    response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text
                    # Remove o fim do bloco
                    response_text = response_text.rsplit('```', 1)[0].strip()

                # 1. Valida se a resposta é um JSON válido
                parsed_json = json.loads(response_text)

                # 2. Valida o conteúdo usando o modelo Pydantic
                processed_review = ReviewProcessed(**parsed_json)

                # 3. Valida se os dados originais foram preservados
                original_review = TEST_REVIEWS[i]
                assert processed_review.user == original_review.user
                assert processed_review.original == original_review.text
                assert processed_review.sentiment in ["positive", "negative", "neutral"]
            except json.JSONDecodeError:
                pytest.fail(f"A resposta {i+1} não é um JSON válido: {response_text[:200]}...")
            except ValidationError as e:
                pytest.fail(
                    f"A resposta {i+1} falhou na validação do Pydantic: {e}\n"
                    f"Resposta: {response_text[:200]}..."
                )

    except (APIConnectionError, APIError) as e:
        pytest.fail(
            "Falha na comunicação com o LLM. Verifique se o servidor está "
            f"rodando e acessível. Erro: {e}"
        )

    logger.info("--- Teste de integração com o LLM finalizado com sucesso ---")
