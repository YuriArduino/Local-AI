
"""
Funções para construir prompts consistentes para o LLM.
"""
from src.models import ReviewRaw

def build_json_prompt(review: ReviewRaw) -> str:
    """
    Constrói um prompt detalhado para o LLM, solicitando uma análise completa
    da resenha, incluindo sentimento, intensidade, aspectos e uma explicação.
    """
    language_hint = f"O idioma original da resenha foi detectado como '{review.language}'."

    return (
        "Sua tarefa é fazer uma análise detalhada da resenha de um aplicativo e retornar um objeto JSON.\n"
        f"{language_hint}\n"
        f"Resenha original: \"{review.text}\"\n\n"
        "O JSON de saída deve ter EXATAMENTE as seguintes chaves:\n"
        "  - \"translation_pt\": string (a tradução da resenha para o português do Brasil).\n"
        "  - \"sentiment\": string (deve ser 'positive', 'negative' ou 'neutral').\n"
        "  - \"intensity\": string (a intensidade do sentimento: 'Alta', 'Média' ou 'Baixa').\n"
        "  - \"aspects\": uma lista de 1 a 3 palavras-chave em português que resumem os pontos principais (ex: [\"usabilidade\", \"bugs\", \"preço\"]).\n"
        "  - \"explanation\": uma frase curta em português explicando o porquê da classificação de sentimento.\n\n"
        "Responda APENAS com o objeto JSON, sem nenhum texto ou formatação adicional."
    )
