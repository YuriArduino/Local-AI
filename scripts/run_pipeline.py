"""
Script principal para executar o pipeline completo de processamento de resenhas.

Este script orquestra as seguintes etapas:
1. Baixa o arquivo de dados de uma URL.
2. Lê e parseia o arquivo .txt para objetos `ReviewRaw`.
3. Envia os prompts para o LLM e recebe as respostas em JSON.
4. Processa, valida, analisa e salva os resultados.
"""
import logging
from pathlib import Path
from typing import List, Optional

# 1. IMPORTS NO TOPO DO ARQUIVO (Resolve C0415)
from src.config import settings
from src.llm_client import LLMClient
from src.logging_config import configure_logging
from src.models import ReviewRaw
from src.processor import analyze_reviews, map_llm_response_to_processed
from src.tools.parser import read_reviews_from_file
from src.tools.prompt_builder import build_json_prompt
from src.utils.file_ops import save_processed_json, save_summary_txt
from src.utils.loader import DocumentLoader

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

# 2. DIVISÃO EM FUNÇÕES MENORES (Resolve R0914 e R0915)

def download_data() -> Optional[Path]:
    """Etapa 1: Baixa o arquivo de dados da URL configurada."""
    logger.info("Etapa 1: Baixando o arquivo de dados...")
    doc_loader = DocumentLoader(persist_dir=str(settings.RAW_DATA_DIR))
    downloaded_files = doc_loader.carregar([settings.REVIEWS_URL])

    if not downloaded_files:
        logger.error("❌ Nenhum arquivo foi baixado. Encerrando o pipeline.")
        return None

    reviews_file_path = downloaded_files[0]
    logger.info("✅ Arquivo salvo em: %s", reviews_file_path)
    return reviews_file_path

def process_with_llm(raw_reviews: List[ReviewRaw]) -> List[str]:
    """Etapa 2: Constrói prompts e obtém respostas do LLM."""
    logger.info("Etapa 2: Construindo prompts e processando com o LLM...")
    prompts = [build_json_prompt(review) for review in raw_reviews]
    logger.info("✅ %d prompts construídos.", len(prompts))

    logger.info("Enviando prompts para o LLM (pode levar um tempo)...")
    llm_client = LLMClient()
    llm_responses = llm_client.batch_process(prompts)
    logger.info("✅ Respostas do LLM recebidas.")
    return llm_responses

def validate_and_analyze(raw_reviews: List[ReviewRaw], llm_responses: List[str]):
    """Etapa 3: Valida, analisa e salva os resultados finais."""
    logger.info("Etapa 3: Validando, analisando e salvando os resultados...")

    processed_reviews = [
        map_llm_response_to_processed(raw_review, llm_resp)
        for raw_review, llm_resp in zip(raw_reviews, llm_responses)
    ]
    logger.info("✅ %d respostas processadas e validadas.", len(processed_reviews))

    counts, concatenated_text = analyze_reviews(processed_reviews)
    logger.info("✅ Análise concluída. Contagem de sentimentos: %s", dict(counts))

    json_path = settings.OUTPUTS_DIR / "processed.json"
    summary_path = settings.OUTPUTS_DIR / "summary.txt"

    save_processed_json(processed_reviews, json_path)
    save_summary_txt(counts, concatenated_text, summary_path)
    logger.info("✅ Arquivos salvos em: %s", settings.OUTPUTS_DIR)

def main():
    """Orquestra a execução do pipeline."""
    configure_logging()
    logger.info("=================================================")
    logger.info("🚀 INICIANDO O PIPELINE DE PROCESSAMENTO DE RESENHAS 🚀")
    logger.info("=================================================")

    # Etapa 1: Download
    reviews_file_path = download_data()
    if not reviews_file_path:
        return

    # Etapa 2: Leitura
    try:
        raw_reviews = read_reviews_from_file(reviews_file_path)
        logger.info("✅ %d resenhas lidas e enriquecidas com sucesso.", len(raw_reviews))
    except FileNotFoundError:
        logger.error("❌ Arquivo de resenhas não encontrado em %s.", reviews_file_path)
        return

    # Etapa 3: Processamento com LLM
    llm_responses = process_with_llm(raw_reviews)

    # Etapa 4: Análise e Salvamento
    validate_and_analyze(raw_reviews, llm_responses)

    logger.info("=================================================")
    logger.info("🎉 PIPELINE CONCLUÍDO COM SUCESSO! 🎉")
    logger.info("=================================================")

if __name__ == "__main__":
    main()
