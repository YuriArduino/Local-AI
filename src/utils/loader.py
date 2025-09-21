"""
Módulo para baixar arquivos de URLs.
"""
import logging
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Baixa arquivos de uma lista de URLs para um diretório local."""

    def __init__(self, persist_dir: str):
        """
        Inicializa o DocumentLoader.

        Args:
            persist_dir: O diretório onde os arquivos serão salvos.
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

    def prepare_github_url(self, url: str) -> str:
        """Adiciona `?raw=true` a URLs do GitHub se não for um link raw."""
        parsed = urlparse(url)
        if "github.com" in parsed.netloc and "raw.githubusercontent.com" not in parsed.netloc:
            if "raw=true" not in parsed.query:
                # Adiciona ?raw=true para obter o conteúdo bruto
                return f"{url}?raw=true"
        return url

    def carregar(self, urls: List[str]) -> List[Path]:
        """
        Baixa arquivos de uma lista de URLs.

        Args:
            urls: Uma lista de URLs para baixar.

        Returns:
            Uma lista de caminhos (Path) para os arquivos baixados.
        """
        downloaded_files: List[Path] = []
        for url in urls:
            try:
                filename = Path(urlparse(url).path).name
                filepath = self.persist_dir / filename

                if filepath.exists():
                    logger.info("Arquivo '%s' já existe. Pulando download.", filename)
                    downloaded_files.append(filepath)
                    continue

                download_url = self.prepare_github_url(url)
                logger.info("Baixando de '%s' para '%s'...", download_url, filepath)

                response = requests.get(download_url, timeout=30)
                response.raise_for_status()

                response.encoding = 'utf-8'
                with filepath.open("w", encoding="utf-8", errors="ignore") as f:
                    f.write(response.text)

                downloaded_files.append(filepath)
                logger.info("✅ Download de '%s' concluído.", filename)

            except requests.RequestException as e:
                logger.error("❌ Falha ao baixar de '%s': %s", url, e)
            except IOError as e:
                logger.error("❌ Falha ao salvar o arquivo '%s': %s", filepath, e)
        return downloaded_files
