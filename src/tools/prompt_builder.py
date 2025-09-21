
"""
Funções para construir prompts consistentes para o LLM.
"""
from src.models import ReviewRaw

def build_json_prompt(review: ReviewRaw) -> str:
    """
    Constrói um prompt para o LLM, informando o idioma de origem
    para melhorar a precisão da tradução e análise.
    """

    if review.language != "unknown":
        language_hint = f"O idioma original da resenha foi detectado como '{review.language}'."
    else:
        language_hint = "O idioma original da resenha não foi detectado com certeza."

    return (
        f"Analise a resenha de aplicativo abaixo e retorne um objeto JSON.\n"
        f"{language_hint}\n"
        f"Resenha original: \"{review.text}\"\n\n"
        f"O JSON de saída deve ter EXATAMENTE as seguintes chaves:\n"
        "  - \"translation_pt\": string (a tradução da resenha para o português do Brasil)\n"
        "  - \"sentiment\": string (deve ser 'positive', 'negative' ou 'neutral')\n\n"
        "Responda APENAS com o objeto JSON, sem nenhum texto ou formatação adicional."
    )
