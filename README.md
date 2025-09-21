### README.md (Versão Final Atualizada)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# Desafio Final — Pipeline de Análise de Sentimento de Resenhas

Este projeto implementa um pipeline de ponta a ponta que baixa resenhas de aplicativos em múltiplos idiomas, as enriquece usando um LLM local (LM Studio / Ollama) e gera saídas de análise estruturadas. O sistema é construído com foco em robustez, testabilidade e boas práticas de engenharia de software.

---

## 🔎 Visão Geral

O pipeline executa as seguintes etapas de forma automatizada:

1.  **Download dos Dados:** Baixa o arquivo de resenhas (`.txt`) de uma URL.
2.  **Parsing e Enriquecimento:** Lê cada linha (`ID$Usuário$Resenha`), aplica limpeza de texto e detecta o idioma original.
3.  **Análise com IA:** Envia cada resenha a um LLM local, solicitando uma análise detalhada em formato JSON.
4.  **Validação e Estruturação:** Valida rigorosamente as respostas do LLM usando **Pydantic V2**, garantindo a integridade dos dados e tratando respostas mal formatadas.
5.  **Geração de Saídas:** Salva os dados enriquecidos em `outputs/processed.json` e um resumo executivo em `outputs/summary.txt`.

---

## 🏆 Destaques & Boas Práticas

*   **Validação Robusta com Pydantic V2:** Utiliza modelos Pydantic com validadores customizados para garantir que todos os dados, desde a entrada até a saída, sejam limpos e consistentes.
*   **Cliente LLM Resiliente:** O `LLMClient` usa a funcionalidade de **retry nativo com backoff exponencial** da biblioteca `openai`, tornando o pipeline resiliente a falhas temporárias de rede ou da API.
*   **Testes Abrangentes (Pytest):** O projeto possui uma suíte de testes unitários e de integração que cobre parsing, validação, operações de arquivo e a comunicação real com o LLM.
*   **Configuração Profissional com `.env`:** Centraliza todas as configurações (chaves de API, caminhos, parâmetros do LLM) em um arquivo `.env`, mantendo o código limpo e seguro.
*   **Qualidade de Código:** O código segue as diretrizes da PEP 8 e foi validado com linters para garantir alta legibilidade e manutenibilidade.

---

## ✅ Estrutura do Projeto

```
project_root/
├─ README.md
├─ LICENSE
├─ requirements.txt
├─ .env.example             # Exemplo de arquivo de configuração
├─ data/
│  └─ raw/
├─ outputs/
│  ├─ processed.json
│  └─ summary.txt
├─ src/
│  ├─ config.py              # Carrega e valida configurações com pydantic-settings
│  ├─ logging_config.py      # Configuração do logger (fuso BR)
│  ├─ models.py              # Modelos Pydantic V2 (ReviewRaw, ReviewProcessed)
│  ├─ llm_client.py          # Cliente resiliente para a API do LLM
│  ├─ processor.py           # Valida respostas do LLM e analisa resultados
│  ├─ tools/
│  │  ├─ parser.py           # Lê, limpa e enriquece os dados brutos
│  │  ├─ prompt_builder.py   # Constrói prompts dinâmicos e detalhados
│  │  └─ text_utils.py       # Funções de limpeza de texto e detecção de idioma
│  └─ utils/
│     ├─ file_ops.py         # Funções de alto nível para salvar arquivos
│     ├─ helpers.py          # Utilitários (ex: safe_json_load aprimorado)
│     └─ loader.py           # Módulo para download de arquivos
├─ scripts/
│  └─ run_pipeline.py        # Orquestrador principal do pipeline
└─ tests/
   ├─ test_loader.py
   ├─ test_parser.py
   ├─ test_processor.py
   └─ test_llm_integration.py
```

---

## 🛠 Requisitos

*   Python 3.10+
*   Um servidor de LLM local (LM Studio ou Ollama) rodando com um modelo de chat.

Instale as dependências com `pip`:
```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```
# Pydantic e Configurações
pydantic>=2.0
pydantic-settings
python-dotenv

# Cliente LLM e HTTP
openai>=1.0
requests

# Análise de Texto
langdetect

# Utilitários
pytz

# Testes
pytest
```

---

## ⚙️ Configuração

### 1. Crie o arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` (você pode copiar o `.env.example`). Preencha com as informações do seu servidor LLM local:

```ini
# Configurações do LLM
LLM_BASE_URL="http://127.0.0.1:1234/v1"
LLM_API_KEY="lm-studio" # ou a chave que seu servidor exigir
LLM_MODEL="google/gemma-2-9b-it" # o modelo que você carregou no servidor

# Parâmetros de Resiliência e Geração
LLM_TIMEOUT=60
LLM_MAX_RETRIES=3
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=512

# Configurações de Logging
LOG_LEVEL="INFO"
```

### 2. Ambiente Virtual (Recomendado)

```bash
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

---

## ▶️ Como Rodar o Pipeline Completo

1.  Certifique-se de que seu servidor LLM (LM Studio / Ollama) está rodando.
2.  Execute o script principal como um módulo a partir da **raiz do projeto**:

```bash
python -m scripts.run_pipeline
```
A execução como módulo (`-m`) é importante para que as importações de `src` funcionem corretamente.

---

## 📄 Formato dos Dados de Saída

### `processed.json`

O arquivo de saída principal, contendo uma lista de objetos JSON com a análise detalhada de cada resenha:

```json
[
  {
    "user": "Safoan Riyad",
    "original": ")'aimais bien ChatgpT. Mais la derniére mise 4 jour a tout gaché. Elle a tout oublié.",
    "translation_pt": "Eu gosto mais do ChatGPT. Mas a última atualização arruinou tudo. Ela esqueceu de tudo.",
    "sentiment": "negative",
    "language": "fr",
    "intensity": "Alta",
    "aspects": [
      "atualização",
      "funcionalidade",
      "qualidade"
    ],
    "explanation": "A resenha expressa forte insatisfação com a atualização mais recente, indicando que ela causou perda de funcionalidades e impactou negativamente a experiência do usuário."
  }
]
```

### `summary.txt`

Um resumo executivo contendo a contagem de sentimentos e o texto original de todas as resenhas concatenadas.

---

## 🧠 Prompt Utilizado

O pipeline constrói um prompt dinâmico e detalhado para extrair o máximo de informação do LLM, incluindo a dica de idioma detectado para melhorar a precisão:

```
Sua tarefa é fazer uma análise detalhada da resenha de um aplicativo e retornar um objeto JSON.
O idioma original da resenha foi detectado como 'fr'.

Resenha original: ")'aimais bien ChatgpT. Mais la derniére mise 4 jour a tout gaché. Elle a tout oublié."

O JSON de saída deve ter EXATAMENTE as seguintes chaves:
  - "translation_pt": string (a tradução da resenha para o português do Brasil).
  - "sentiment": string (deve ser 'positive', 'negative' ou 'neutral').
  - "intensity": string (a intensidade do sentimento: 'Alta', 'Média' ou 'Baixa').
  - "aspects": uma lista de 1 a 3 palavras-chave em português que resumem os pontos principais (ex: ["usabilidade", "bugs", "preço"]).
  - "explanation": uma frase curta em português explicando o porquê da classificação de sentimento.

Responda APENAS com o objeto JSON, sem nenhum texto ou formatação adicional.
```

---

## Licença

Este projeto está licenciado sob a Licença MIT — veja o arquivo [LICENSE](LICENSE) para mais detalhes.
