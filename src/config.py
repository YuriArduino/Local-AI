"""
Configuração do projeto.
"""

from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()  # carrega .env da raiz do projeto

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "raw"))
OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", PROJECT_ROOT / "outputs"))

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemma-3n-e4b")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


