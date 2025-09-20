"""
Script para executar o pipeline completo.
"""

from src.logging_config import configure_logging
from loader import DocumentLoader
from src.tools.parser import parse_txt_line
from src.tools.prompt_builder import build_json_prompt
from src.llm_client import LLMClient
from src.utils.io import save_json, save_text
from src.processor import map_llm_response_to_processed, analyze_reviews
from src.config import DATA_DIR, OUTPUTS_DIR

def main():
    configure_logging()
    # 1) baixar
    urls = ["https://github.com/YuriArduino/Estudos_Artificial_Intelligence/blob/Dados/resenhas_app.txt"]
    loader = DocumentLoader(persist_dir="data/raw")
    arquivos = loader.carregar(urls)
    if not arquivos:
        return

    txt_path = arquivos[0]
    raw_reviews = read_txt_to_raw_reviews(txt_path)

    # 2) preparar prompts para LLM (p.ex., pedir JSON com translation_pt e sentiment)
    prompts = []
    for r in raw_reviews:
        # construir prompt que pede JSON estrito
        p = (
            f"Por favor retorne um JSON com chaves 'translation_pt' e 'sentiment' para a resenha abaixo.\n\n"
            f"Resenha: \"{r.text}\"\n\n"
            "Responda somente com JSON. 'sentiment' deve ser 'positive', 'negative' ou 'neutral'."
        )
        prompts.append(p)

    # 3) chamar LLM
    llm = LLMClient()
    llm_outputs = llm.batch_process(prompts, temperature=0.0)

    # 4) mapear para ReviewProcessed
    processed = []
    for raw, out in zip(raw_reviews, llm_outputs):
        proc = map_llm_response_to_processed(user=raw.user, original=raw.text, llm_response=out)
        processed.append(proc)

    # 5) analisar e salvar
    counts, concatenated = analyze_reviews(processed, separator=" || ")
    save_processed_json(processed, Path("outputs/processed.json"))
    save_summary_txt(counts, concatenated, Path("outputs/summary.txt"))

if __name__ == "__main__":
    main()
