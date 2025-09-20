"""
Modelos de dados para o projeto.
"""

from typing import List
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
    def ensure_str(cls, v):
        # Garante string (decodifica bytes se necessário)
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
    sentiment: str = Field(..., description="positive | negative | neutral")

    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }

class ReviewsList(BaseModel):
    items: List[ReviewProcessed]
