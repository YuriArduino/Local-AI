"""
Testes para as operações de salvamento de arquivos em `file_ops`.
"""
import json
from collections import Counter
from pathlib import Path

# Importa os modelos e as funções que vamos testar
from src.models import ReviewProcessed
from src.utils.file_ops import save_processed_json, save_summary_txt

def test_save_processed_json(tmp_path: Path):
    """
    Testa a função save_processed_json.

    Verifica se o arquivo JSON é criado e se seu conteúdo corresponde
    aos dados de entrada.

    Args:
        tmp_path (Path): Uma fixture do pytest que fornece um diretório temporário.
    """
    # 1. Prepara os dados de entrada
    reviews_to_save = [
        ReviewProcessed(user="UserA", original="Great!", translation_pt="Ótimo!", sentiment="positive"),
        ReviewProcessed(user="UserB", original="Bad.", translation_pt="Ruim.", sentiment="negative"),
    ]
    # Define o caminho do arquivo de saída dentro do diretório temporário
    output_file = tmp_path / "processed.json"

    # 2. Executa a função que está sendo testada
    save_processed_json(reviews_to_save, output_file)

    # 3. Valida o resultado
    assert output_file.exists(), "O arquivo JSON não foi criado."

    with output_file.open("r", encoding="utf-8") as f:
        saved_data = json.load(f)

    expected_data = [
        {"user": "UserA", "original": "Great!", "translation_pt": "Ótimo!", "sentiment": "positive"},
        {"user": "UserB", "original": "Bad.", "translation_pt": "Ruim.", "sentiment": "negative"},
    ]
    assert saved_data == expected_data, "O conteúdo do arquivo JSON está incorreto."

def test_save_summary_txt(tmp_path: Path):
    """
    Testa a função save_summary_txt.

    Verifica se o arquivo de texto do sumário é criado e se seu conteúdo
    está formatado corretamente.

    Args:
        tmp_path (Path): Uma fixture do pytest que fornece um diretório temporário.
    """
    # 1. Prepara os dados de entrada
    counts = Counter({"positive": 10, "negative": 5, "neutral": 2})
    concatenated_text = "UserA: Review1 || UserB: Review2"
    output_file = tmp_path / "summary.txt"

    # 2. Executa a função que está sendo testada
    save_summary_txt(counts, concatenated_text, output_file)

    # 3. Valida o resultado
    assert output_file.exists(), "O arquivo de sumário não foi criado."

    saved_content = output_file.read_text(encoding="utf-8")

    # Verifica se as partes essenciais estão no conteúdo
    assert "Contagem de sentimentos:" in saved_content
    assert "positive: 10" in saved_content
    assert "negative: 5" in saved_content
    assert "neutral: 2" in saved_content
    assert "\nConcatenado:\n" in saved_content
    assert "UserA: Review1 || UserB: Review2" in saved_content
