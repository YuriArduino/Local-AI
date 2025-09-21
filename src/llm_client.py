"""
Script para processar prompts com um modelo LLM.
"""
import logging
from typing import List
from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
)

from src.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """Cliente para interagir com um modelo de linguagem grande (LLM) via API compatível com OpenAI."""

    def __init__(
    self,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None
):
        _base_url = base_url or settings.LLM_BASE_URL
        _api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        self.client = OpenAI(
            base_url=_base_url,
            api_key=_api_key,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
        )

    def batch_process(
        self,
        prompts: List[str],
        temperature: float | None = None,
    ) -> List[str]:
        """Envia uma lista de prompts e retorna as respostas brutas do LLM."""
        logger.info(
            "Iniciando processamento em lote com max_retries=%d.",
            self.client.max_retries,
        )
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
                outputs.append(text or "") # Garante que não seja None
            except AuthenticationError as e:
                # Erro de autenticação é fatal. Aborta o batch.
                logger.critical(
                    "Erro de autenticação com a API do LLM. Verifique sua API Key. Abortando. Erro: %s", e
                )
                raise
            except APIConnectionError as e: # Também captura APITimeoutError
                # Erros de conexão/timeout após as tentativas. Loga e continua.
                logger.error(
                    "Não foi possível conectar ao LLM para o prompt %d após %d tentativas. Erro: %s",
                    i + 1,
                    self.client.max_retries,
                    e,
                )
                outputs.append('{"translation_pt": "ERRO DE CONEXÃO", "sentiment": "neutral"}')
            except APIError as e:
                # Outros erros de API (ex: rate limit, bad request). Loga e continua.
                logger.error("Ocorreu um erro na API do LLM no prompt %d: %s", i + 1, e)
                # Retorna um JSON de erro para não quebrar o pipeline.
                # O processador usará isso como fallback.
                outputs.append('{"translation_pt": "ERRO NA API", "sentiment": "neutral"}')

        logger.info("Processados %d prompts pelo LLM.", len(outputs))
        return outputs
