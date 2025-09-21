"""
Script para configurar logs com horário de Brasília (UTC-3).
"""

import logging
from datetime import datetime
import pytz

brasilia_tz = pytz.timezone("America/Sao_Paulo")

class TZFormatter(logging.Formatter):
    """Formatter de log que converte o timestamp para o fuso horário de Brasília."""
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        """Formata o tempo do registro para o fuso horário de Brasília.

        Args:
            record (logging.LogRecord): O registro de log a ser formatado.
            datefmt (str | None): A string de formato de data/hora.
                Se None, um padrão é usado.

        Returns:
            str: A string de data/hora formatada.
        """
        dt = datetime.fromtimestamp(record.created, tz=brasilia_tz)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

def configure_logging(level: int = logging.INFO) -> None:
    """Configura o logging global da aplicação.

    Define um handler que escreve no console (StreamHandler) com um
    formato personalizado que inclui timestamp no fuso horário de Brasília.
    Também silencia logs muito verbosos da biblioteca `urllib3`.

    Args:
        level (int): O nível de log a ser configurado (ex: logging.INFO, logging.DEBUG).
    """
    handler = logging.StreamHandler()
    handler.setFormatter(TZFormatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
