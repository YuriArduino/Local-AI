"""
Modelos de dados para o projeto.
"""

from typing import Any, List, Literal
from pydantic import BaseModel, Field, field_validator

class ReviewRaw(BaseModel):
    """Representa uma linha crua do .txt: ID$Usuário$Resenha"""
    id: str = Field(..., description="ID do usuário no dataset")
    user: str = Field(..., description="Nome do usuário")
    text: str = Field(..., description="Texto da resenha original")

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

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }

class ReviewsList(BaseModel):
    """Modelo para uma lista de resenhas processadas."""
    items: List[ReviewProcessed]
