[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


# Desafio Final — Pipeline de Processamento de Resenhas (JetGPT)

README para o projeto que baixa um `.txt` de resenhas, faz parsing, envia cada resenha a um LLM local (LM Studio / Ollama), valida/normaliza com **Pydantic v2**, e gera saídas consolidadas (`processed.json` + `summary.txt`).

---

## 🔎 Visão geral

Este repositório orquestra um pipeline simples e robusto:

1. Baixa a base de dados (`resenhas_app.txt`) para `data/raw/`.
2. Lê e parseia cada linha no formato `ID$Usuário$Resenha`.
3. Para cada resenha, envia um prompt ao LLM local pedindo **JSON** com `translation_pt` e `sentiment`.
4. Valida e representa dados com **Pydantic v2** (`ReviewRaw`, `ReviewProcessed`).
5. Salva os resultados em `outputs/processed.json` e um resumo em `outputs/summary.txt`.

---

## ✅ Estrutura do projeto (resumida)

```
project_root/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ data/
│  └─ raw/
├─ outputs/
│  ├─ processed.json
│  └─ summary.txt
├─ src/
│  ├─ __init__.py
│  ├─ config.py                    # leitura de variáveis e caminhos
│  ├─ logging_config.py            # configuração do logger (fuso BR)
│  ├─ models.py                    # pydantic v2 models
│  ├─ llm_client.py                # wrapper do OpenAI / LLM local
│  ├─ processor.py                 # mapeamento LLM -> ReviewProcessed, análise
│  │
│  ├─ tools/                       # funções utilitárias de domínio (parsing, prompts)
│  │  ├─ __init__.py
│  │  ├─ parser.py                 # parsing de linhas txt -> modelos brutos
│  │  ├─ prompt_builder.py         # montar prompt consistente para o LLM
│  │  └─ text_utils.py             # limpeza de texto, normalização, detect-language
│  │
│  └─ utils/                       # funções infra/IO/serialização genéricas
│     ├─ __init__.py
│     ├─ io.py                     # salvar/ler JSON/TXT/CSV
│     ├─ file_ops.py               # helpers para paths, criação de pastas, unique names
│     └─ helpers.py                # pequenas funções compartilhadas (ex: safe_json_load)
├─ scripts/
│  └─ run_pipeline.py
└─ tests/
   └─ test_parser.py
```

---

## 🛠 Requisitos (mínimos)

* Python 3.10+
* Bibliotecas (instale via `pip`):

```bash
pip install -r requirements.txt
```

Exemplo de `requirements.txt`:

```
pydantic>=2.0
openai
requests
pytz
pandas
```

---

## ⚙️ Configuração

### 1) Virtualenv (opcional, recomendado)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 2) Configurar LLM local

Você pode configurar a URL/API key diretamente em `src/llm_client.py` ou, preferível, via variáveis de ambiente que você leia em `src/config.py`.

Recomendações de variáveis (exemplo):

* `LLM_BASE_URL` — ex.: `http://127.0.0.1:1234/v1`
* `LLM_API_KEY` — ex.: `lm-studio`
* `LLM_MODEL` — ex.: `google/gemma-3n-e4b`

Exportando (bash):

```bash
export LLM_BASE_URL="http://127.0.0.1:1234/v1"
export LLM_API_KEY="lm-studio"
export LLM_MODEL="google/gemma-3n-e4b"
```

> Se preferir, apenas edite os valores padrão em `src/llm_client.py`.

---

## ▶️ Como rodar (pipeline completo)

1. Configure as variáveis (ou edite `src/llm_client.py`).
2. Execute o orquestrador a partir da raiz do projeto:

```bash
python -m scripts.run_pipeline
```

Esse script fará:

* baixar o `resenhas_app.txt` para `data/raw/` (DocumentLoader),
* ler e parsear o arquivo (reader),
* enviar prompts ao LLM (llm\_client),
* mapear respostas para modelos Pydantic (processor),
* salvar `outputs/processed.json` e `outputs/summary.txt` (utils).

---

## 📄 Formato dos dados

### Entrada (`.txt`)

Cada linha segue:

```
ID$Usuário$Resenha
```

Ex.: `53409593$Safoan Riyad$)'aimais bien ChatgpT...`

No `reader` usamos `split("$", 2)` para garantir que a resenha possa conter `$`.

### Saída (`processed.json`)

Lista de objetos com esse modelo (Pydantic v2):

```json
[
  {
    "user": "Safoan Riyad",
    "original": ")'aimais bien ChatgpT. Mais la derniére mise 4 jour a tout gaché. Elle a tout oublié.",
    "translation_pt": "Eu gostava mais do ChatGPT. Mas a última atualização arruinou tudo. Ela esqueceu de tudo.",
    "sentiment": "negative",
    "language": "fr",
    "intensity": "Alta",
    "aspects": [
      "atualização",
      "regressão de funcionalidade"
    ],
    "explanation": "O usuário expressa forte insatisfação com a última atualização, que removeu funcionalidades ou conhecimento prévio."
  },
  ...
]
```

### Resumo (`summary.txt`)

Contém:

* contagem por sentimento (positive / negative / neutral)
* string concatenada com todas as resenhas (separador configurável)

---

## 🧠 Prompt sugerido (muito importante)

Peça explicitamente **apenas JSON** para facilitar parsing. Exemplo (já usado no `scripts/run_pipeline.py`):

```
Por favor retorne um JSON com chaves 'translation_pt' e 'sentiment' para a resenha abaixo.

Resenha: "TEXTO_DA_RESENHA"

Responda somente com JSON. 'sentiment' deve ser 'positive', 'negative' ou 'neutral'.
```

Se o LLM responder fora do formato JSON, o `processor` aplica fallback (sentiment = `neutral`) — mas é melhor garantir respostas JSON.

---

## 🧩 Observações & boas práticas

* **Pydantic v2**: usamos `model_dump()` para serializar os modelos.
* **Robustez no parsing**: linhas mal-formatadas são logadas e preenchidas com strings vazias quando possível.
* **Logging**: `src/logging_config.py` configura logs no fuso `America/Sao_Paulo`.
* **Batching**: o `LLMClient.batch_process` faz uma chamada por prompt. Se sua API suportar batch nativo, optimize para reduzir latência.
* **Rate limits / retry**: dependendo do LLM local e do número de resenhas, considere adicionar retries/exponential backoff no client.

---

## 🔧 Problemas comuns & solução rápida

* **Arquivo não baixado**: verifique URL (use `?raw=true` em GitHub) e conectividade. O `DocumentLoader` já adiciona `?raw=true` quando detecta `github.com`.
* **Erros de decodificação**: abrimos arquivos com `encoding='utf-8', errors='ignore'` para evitar falhas com caracteres estranhos.
* **LLM retornando texto, não JSON**: ajuste o prompt para reforçar "Responda somente com JSON" e reduza temperatura. Use `temperature=0.0`.

---

## Próximos passos / melhorias sugeridas

* Implementar retries e controle de taxa (backoff) no `LLMClient`.
* Adicionar testes unitários para `reader.parse_line_to_raw` e para validações Pydantic.
* Exportar outputs adicionais (CSV, análises por idioma, top N palavras).
* Automatizar import para Trello (ex.: criar checklist de progresso com base no `summary.txt`) — se quiser, posso gerar esse script.

---

## Licença

Este projeto está licenciado sob a Licença MIT — veja o arquivo [LICENSE](LICENSE) para mais detalhes.
