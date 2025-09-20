"""
Builder de prompts para o LLM.
"""

def build_json_prompt(review_text: str) -> str:
    return (
        "Por favor responda APENAS com JSON válido contendo as chaves:\n"
        "  - translation_pt: string (tradução para português)\n"
        "  - sentiment: one of [positive, negative, neutral]\n\n"
        f"Resenha: \"{review_text}\"\n\n"
        "Responda somente com JSON. Não adicione texto extra."
    )
