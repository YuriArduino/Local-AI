"""
Configuração do projeto usando pydantic-settings para validação
e carregamento automático de variáveis de ambiente.

Todas as configurações são acessíveis através do objeto `settings`.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Define a raiz do projeto. É a única variável "global" necessária.
#    É o diretório que contém 'src', 'data', 'outputs', etc.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Define e valida todas as configurações do aplicativo.
    Lê automaticamente de um arquivo .env na raiz do projeto e de variáveis de ambiente.
    """
    # 2. Configura o Pydantic para ler o arquivo .env da raiz do projeto.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis extras no .env que não estão no modelo
    )

    # --- Configurações do LLM (lidas do .env) ---
    # Pydantic valida e converte os tipos automaticamente.
    LLM_BASE_URL: str = "http://127.0.0.1:1234/v1"
    LLM_API_KEY: str = "lm-studio"
    LLM_MODEL: str = "google/gemma-3n-e4b"
    LLM_TIMEOUT: int = 30
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 512

    # --- Configurações de Logging (lidas do .env) ---
    LOG_LEVEL: str = "INFO"

    # --- Caminhos do Projeto (derivados do PROJECT_ROOT) ---
    # Estes campos não vêm do .env, são calculados aqui.
    # Disponibilizamos todos os caminhos através do objeto `settings` para consistência.
    PROJECT_ROOT: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / "data"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    SRC_DIR: Path = PROJECT_ROOT / "src"


# 3. Cria uma única instância das configurações para ser usada em todo o projeto.
#    Importe `settings` de src.config em outros módulos.
settings = Settings()
