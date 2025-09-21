"""
Script para processar prompts com um modelo LLM.
"""
import logging
from typing import List
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)

from src.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """Cliente para interagir com um modelo de linguagem grande (LLM) via API compatível com OpenAI."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None):
        _base_url = base_url or settings.LLM_BASE_URL
        _api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        self.client = OpenAI(base_url=_base_url, api_key=_api_key, timeout=settings.LLM_TIMEOUT)

    def batch_process(
        self,
        prompts: List[str],
        temperature: float | None = None,
    ) -> List[str]:
        """Envia uma lista de prompts e retorna as respostas brutas do LLM."""
        outputs = []
        for i, p in enumerate(prompts):
            try:
                logger.info("Processando prompt %d de %d...", i + 1, len(prompts))
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        # Removido o system prompt para ser mais direto, o prompt do usuário já é bem específico
                        {"role": "user", "content": p},
                    ],
                    temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                    # --- MELHORIA: Força o LLM a responder em modo JSON ---
                    # Caso a API suporte, usar este parâmetro para garantir que a resposta seja um JSON válido.
                    #  response_format={"type": "json_object"},
                )
                text = resp.choices[0].message.content
                outputs.append(text)
            # --- MELHORIA: Captura erros fatais (conexão, auth) e aborta o batch ---
            except (APIConnectionError, AuthenticationError, APITimeoutError) as e:
                logger.critical(
                    "Erro fatal de comunicação com o LLM no prompt %d. Abortando. Erro: %s",
                    i + 1,
                    e,
                )
                # Re-lança a exceção para que o chamador (pipeline/teste) possa lidar com isso.
                raise
            # --- MELHORIA: Captura outros erros de API (ex: prompt inválido) e continua ---
            except APIError as e:
                logger.error("Ocorreu um erro na API do LLM no prompt %d: %s", i + 1, e)
                # Retorna um JSON de erro para não quebrar o pipeline
                error_json = '{"translation_pt": "ERRO NA API", "sentiment": "neutral", "user": "ERRO", "original": "ERRO"}'
                outputs.append(error_json)

        logger.info("Processados %d prompts pelo LLM.", len(outputs))
        return outputs
