"""
Funções utilitárias pequenas e compartilhadas.
"""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def safe_json_load(text: str) -> Dict[str, Any]:
    """
    Tenta carregar uma string como JSON de forma segura.

    Args:
        text: A string que se espera ser um JSON.

    Returns:
        Um dicionário se o parsing for bem-sucedido, ou um dicionário vazio em caso de erro.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Usar str(text) para o log, garantindo que funcione mesmo se a entrada não for string.
        logger.warning("Falha ao decodificar JSON. Resposta do LLM: %s", str(text)[:200])
        return {}
    except (TypeError, RecursionError) as e:
        logger.error("Erro ao decodificar JSON (tipo inválido ou recursão excessiva): %s", e)
        return {}
