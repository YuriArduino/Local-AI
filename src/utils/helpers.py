"""
Funções utilitárias pequenas e compartilhadas.
"""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def safe_json_load(text: str) -> Dict[str, Any]:
    """
    Tenta carregar uma string como JSON de forma segura, limpando-a primeiro.

    Esta função é projetada para lidar com respostas de LLMs que podem
    envolver o JSON em blocos de código Markdown (```json ... ```) ou
    adicionar texto explicativo. Ela extrai o conteúdo entre o primeiro '{'
    e o último '}'.

    Args:
        text: A string que se espera conter um JSON.

    Returns:
        Um dicionário se o parsing for bem-sucedido, ou um dicionário vazio em caso de erro.
    """
    try:
        # Encontra o início e o fim do objeto JSON na string
        start_index = text.find('{')
        end_index = text.rfind('}')

        if start_index != -1 and end_index != -1:
            # Extrai a substring que parece ser o JSON
            json_str = text[start_index : end_index + 1]
            return json.loads(json_str)
        else:
            # Se não encontrar um objeto JSON, retorna vazio
            logger.warning(
                "Nenhum objeto JSON ('{...}') encontrado na resposta do LLM: %s", text[:200]
            )
            return {}

    except json.JSONDecodeError:
        logger.warning(
            "Falha ao decodificar JSON extraído. Resposta do LLM: %s", text[:200]
        )
        return {}
    except (TypeError, RecursionError) as e:
        logger.error(
            "Erro ao decodificar JSON (tipo inválido ou recursão excessiva): %s", e
        )
        return {}
