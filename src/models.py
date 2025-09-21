"""
Modelos de dados para o projeto.
"""

from typing import Any, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class ReviewRaw(BaseModel):
    """Representa uma linha crua do .txt: ID$Usuário$Resenha"""
    id: str = Field(..., description="ID do usuário no dataset")
    user: str = Field(..., description="Nome do usuário")
    text: str = Field(..., description="Texto da resenha original")
    language: str = Field(..., description="Idioma detectado do texto original (ex: 'en', 'pt')")

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }

    @field_validator("id", "user", "text", mode="before")
    @classmethod
    def ensure_str(cls, v: Any) -> str:
        """Garante que o valor de entrada seja uma string.

        Este validador é aplicado antes da análise do Pydantic e converte
        valores para string. Se o valor for `bytes`, ele é decodificado.
        Se for `None`, é convertido para uma string vazia.

        Args:
            v: O valor do campo a ser validado.

        Returns:
            O valor convertido para string.
        """
        if v is None:
            return ""
        if isinstance(v, bytes):
            return v.decode('utf-8', errors='ignore')
        return str(v)

class ReviewProcessed(BaseModel):
    """Representa a saída processada / final que será salva em JSON"""
    user: str
    original: str
    translation_pt: str
    sentiment: Literal["positive", "negative", "neutral"]

    # --- NOVOS CAMPOS DE ANÁLISE ---
    language: str = Field(
        ..., description="Idioma detectado do texto original (ex: 'en', 'pt')"
    )
    intensity: Literal["Alta", "Média", "Baixa"] = Field(
        ..., description="A intensidade do sentimento expresso."
    )
    aspects: List[str] = Field(
        default_factory=list,
        description="Lista de palavras-chave ou aspectos mencionados na resenha.",
    )
    explanation: str = Field(
        ...,
        description="Uma breve explicação em português sobre a análise de sentimento.",
    )

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }

    @model_validator(mode='before')
    @classmethod
    def normalize_llm_input(cls, data: Any) -> Any:
        """Limpa e normaliza os dados brutos vindos do LLM antes da validação."""
        if not isinstance(data, dict):
            return data

        # Converte "aspects" de string para lista, se necessário
        if 'aspects' in data and isinstance(data['aspects'], str):
            data['aspects'] = [a.strip() for a in data['aspects'].split(',') if a.strip()]

        # Garante que a intensidade esteja correta, com um fallback inteligente
        if 'intensity' in data and isinstance(data['intensity'], str):
            valid_intensities = {"Alta", "Média", "Baixa"}
            capitalized_intensity = data['intensity'].capitalize()
            if capitalized_intensity in valid_intensities:
                data['intensity'] = capitalized_intensity
            else:
                # Fallback inteligente baseado no sentimento (se disponível)
                sentiment = data.get('sentiment')
                data['intensity'] = "Média" if sentiment != "neutral" else "Baixa"
        return data

class ReviewsList(BaseModel):
    """Modelo para uma lista de resenhas processadas."""
    items: List[ReviewProcessed]
