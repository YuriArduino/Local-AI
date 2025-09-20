"""
Script para configurar logs com horário de Brasília (UTC-3).
"""

import logging
from datetime import datetime
import pytz

brasilia_tz = pytz.timezone("America/Sao_Paulo")

class TZFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=brasilia_tz)
        return dt.strftime(datefmt or "%Y-%m-%d %H:%M:%S")

def configure_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(TZFormatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
