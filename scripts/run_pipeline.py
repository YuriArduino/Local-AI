"""
Script para executar o pipeline completo.
"""

from src.config import settings
from pathlib import Path
from src.logging_config import configure_logging
from loader import DocumentLoader
from src.tools.parser import read_reviews_from_file
from src.llm_client import LLMClient
from src.utils.file_ops import save_processed_json, save_summary_txt
from src.processor import map_llm_response_to_processed, analyze_reviews
# Você pode gerenciar os caminhos aqui ou via config.py
# from src.config import DATA_DIR, OUTPUTS_DIR

# --- Definição de caminhos (exemplo, pode vir do config.py) ---
# Adiciona uma forma de encontrar a raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RAW_DATA_DIR = DATA_DIR / "raw"

def main():
    """
    Orquestra o pipeline de processamento de resenhas.
    """
    configure_logging() # Configura o logger primeiro

    # 1. Baixar os dados
    urls = ["https://raw.githubusercontent.com/YuriArduino/Estudos_Artificial_Intelligence/main/Dados/resenhas_app.txt"]
    loader = DocumentLoader(persist_dir=str(RAW_DATA_DIR))

    print("Baixando arquivos...")
    arquivos_baixados = loader.carregar(urls)
    if not arquivos_baixados:
        print("Nenhum arquivo foi baixado. Encerrando.")
        return

    txt_path = Path(arquivos_baixados[0])

    # 2. Ler e parsear o arquivo .txt para objetos ReviewRaw
    print(f"Lendo e parseando o arquivo: {txt_path}")
    # Chama a função com o nome correto
    raw_reviews = read_reviews_from_file(txt_path)
    print(f"{len(raw_reviews)} resenhas lidas.")

    # 3. Preparar prompts para o LLM
    print("Construindo prompts para o LLM...")
    prompts = []
    for r in raw_reviews:
        # Usando o campo 'text' do seu modelo ReviewRaw
        p = (
            f"Por favor retorne um JSON com chaves 'translation_pt' e 'sentiment' para a resenha abaixo.\n\n"
            f"Resenha: \"{r.text}\"\n\n"
            "Responda somente com JSON. 'sentiment' deve ser 'positive', 'negative' ou 'neutral'."
        )
        prompts.append(p)

    # 4. Chamar o LLM em batch
    print("Enviando resenhas para o LLM...")
    llm = LLMClient() # Assume que está configurado para o LLM local
    llm_outputs = llm.batch_process(prompts)
    print("Respostas do LLM recebidas.")

    # 5. Mapear respostas do LLM para objetos ReviewProcessed
    print("Processando e validando as respostas...")
    processed_reviews = []
    for raw, out in zip(raw_reviews, llm_outputs):
        proc = map_llm_response_to_processed(user=raw.user, original=raw.text, llm_response=out)
        processed_reviews.append(proc)

    # 6. Analisar resultados e salvar os arquivos de saída
    print("Analisando e salvando os resultados...")
    counts, concatenated = analyze_reviews(processed_reviews, separator=" || ")

    # Define os caminhos de saída
    json_output_path = OUTPUTS_DIR / "processed.json"
    summary_output_path = OUTPUTS_DIR / "summary.txt"

    save_processed_json(processed_reviews, json_output_path)
    save_summary_txt(counts, concatenated, summary_output_path)

    print("-" * 50)
    print("Pipeline concluído com sucesso!")
    print(f"Resultados salvos em: {OUTPUTS_DIR}")
    print("-" * 50)


if __name__ == "__main__":
    main()
