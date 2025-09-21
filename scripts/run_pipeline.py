"""
Script principal para executar o pipeline completo de processamento de resenhas.

Este script orquestra as seguintes etapas:
1. Configura o logging.
2. (Opcional) Baixa o arquivo de dados de uma URL.
3. Lê e parseia o arquivo .txt para objetos `ReviewRaw`.
4. Constrói prompts para cada resenha.
5. Envia os prompts para o LLM e recebe as respostas em JSON.
6. Processa e valida cada resposta, convertendo-as em objetos `ReviewProcessed`.
7. Analisa a lista de resenhas processadas para gerar um sumário.
8. Salva a lista completa em `outputs/processed.json` e o sumário em `outputs/summary.txt`.
"""
import logging

# Módulos do projeto
from src.config import settings
from src.llm_client import LLMClient
from src.logging_config import configure_logging
from src.processor import analyze_reviews, map_llm_response_to_processed
from src.tools.parser import read_reviews_from_file
from src.tools.prompt_builder import build_json_prompt
from src.utils.file_ops import save_processed_json, save_summary_txt
from src.utils.loader import DocumentLoader

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

def main():
    """Orquestra a execução do pipeline."""
    # 1. Configuração inicial
    configure_logging()
    logger.info("=================================================")
    logger.info(" INICIANDO O PIPELINE DE PROCESSAMENTO DE RESENHAS")
    logger.info("=================================================")

    # 2. Download dos dados (usando config)
    logger.info("Etapa 1: Baixando o arquivo de dados...")
    doc_loader = DocumentLoader(persist_dir=str(settings.RAW_DATA_DIR))
    downloaded_files = doc_loader.carregar([settings.REVIEWS_URL])
    if not downloaded_files:
        logger.error("❌ Nenhum arquivo foi baixado. Encerrando o pipeline.")
        return

    reviews_file_path = downloaded_files[0]
    logger.info("✅ Arquivo salvo em: %s", reviews_file_path)

    # 3. Leitura e Parsing
    logger.info("Etapa 2: Lendo e parseando o arquivo de resenhas...")
    try:
        raw_reviews = read_reviews_from_file(reviews_file_path)
        logger.info("✅ %d resenhas lidas e enriquecidas com sucesso.", len(raw_reviews))
    except FileNotFoundError:
        logger.error("❌ Arquivo de resenhas não encontrado em %s. Encerrando.", reviews_file_path)
        return

    # 4. Construção de Prompts
    logger.info("Etapa 3: Construindo prompts para o LLM...")
    prompts = [build_json_prompt(review) for review in raw_reviews]
    logger.info("✅ %d prompts construídos.", len(prompts))

    # 5. Processamento pelo LLM
    logger.info("Etapa 4: Enviando prompts para o LLM (pode levar um tempo)...")
    llm_client = LLMClient()
    llm_responses = llm_client.batch_process(prompts)
    logger.info("✅ Respostas do LLM recebidas.")

    # 6. Validação e Mapeamento (usando list comprehension)
    logger.info("Etapa 5: Processando e validando as respostas do LLM...")
    processed_reviews = [
        map_llm_response_to_processed(raw_review, llm_resp)
        for raw_review, llm_resp in zip(raw_reviews, llm_responses)
    ]
    logger.info("✅ %d respostas processadas e validadas.", len(processed_reviews))

    # 7. Análise dos Resultados
    logger.info("Etapa 6: Analisando os resultados processados...")
    counts, concatenated_text = analyze_reviews(processed_reviews)
    logger.info("✅ Análise concluída. Contagem de sentimentos: %s", dict(counts))

    # 8. Salvamento dos Arquivos (usando config)
    logger.info("Etapa 7: Salvando os arquivos de saída...")
    json_path = settings.OUTPUTS_DIR / "processed.json"
    summary_path = settings.OUTPUTS_DIR / "summary.txt"

    save_processed_json(processed_reviews, json_path)
    save_summary_txt(counts, concatenated_text, summary_path)
    logger.info("✅ Arquivos salvos em: %s", settings.OUTPUTS_DIR)

    logger.info("=================================================")
    logger.info(" PIPELINE CONCLUÍDO COM SUCESSO! ")
    logger.info("=================================================")

if __name__ == "__main__":
    main()
