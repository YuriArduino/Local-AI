"""
Script para processar prompts com um modelo LLM.
"""

import logging
from openai import OpenAI
from typing import List

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", api_key: str = "lm-studio", model: str = "google/gemma-3n-e4b"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def batch_process(self, prompts: List[str], temperature: float = 0.0):
        """Enviar prompts (ex.: instruções + texto) e retornar respostas brutas.
           Implementação simples: faz uma chamada por prompt (você pode otimizar fazendo batch se a API suportar)."""
        outputs = []
        for p in prompts:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente de IA muito prestativo"},
                    {"role": "user", "content": p},
                ],
                temperature=temperature,
                max_tokens=512
            )
            # note: verifique a estrutura exata de resp na sua instalação (podem variar)
            text = resp.choices[0].message.content
            outputs.append(text)
        logger.info(f"Processados {len(outputs)} prompts pelo LLM.")
        return outputs
