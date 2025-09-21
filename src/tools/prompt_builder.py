"""
Builder de prompts para o LLM.
"""
from src.models import ReviewRaw

def build_json_prompt(review: ReviewRaw) -> str:
    """
    Constrói um prompt para o LLM solicitando uma resposta em formato JSON
    com todos os campos necessários para um objeto ReviewProcessed.

    Args:
        review: O objeto ReviewRaw com os dados da resenha original.
    """
    # --- MELHORIA: Prompt mais detalhado que pede todos os campos necessários ---
    return (
        f"Sua tarefa é analisar a resenha de um aplicativo e retornar um objeto JSON.\n"
        f"A resenha original foi escrita por '{review.user}' e o texto é: \"{review.text}\".\n\n"
        f"O JSON de saída deve ter EXATAMENTE as seguintes chaves:\n"
        f"  - \"user\": string (use o valor '{review.user}')\n"
        f"  - \"original\": string (use o valor \"{review.text}\")\n"
        "  - \"translation_pt\": string (a tradução da resenha para o português do Brasil)\n"
        "  - \"sentiment\": string (deve ser 'positive', 'negative' ou 'neutral')\n\n"
        "Responda APENAS com o objeto JSON, sem nenhum texto ou formatação adicional."
    )
