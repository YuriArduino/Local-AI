"""
Testes para o DocumentLoader em src.utils.loader.
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from src.utils.loader import DocumentLoader


def test_document_loader_initialization(tmp_path: Path):
    """Testa se o diretório de persistência é criado na inicialização."""
    persist_dir = tmp_path / "test_data"
    assert not persist_dir.exists()

    loader = DocumentLoader(str(persist_dir))

    assert persist_dir.exists()
    assert persist_dir.is_dir()
    assert loader.persist_dir == persist_dir


@pytest.mark.parametrize(
    "input_url, expected_url",
    [
        ("https://github.com/user/repo/blob/main/file.txt", "https://github.com/user/repo/blob/main/file.txt?raw=true"),
        ("https://github.com/user/repo/blob/main/file.txt?raw=true", "https://github.com/user/repo/blob/main/file.txt?raw=true"),
        ("https://raw.githubusercontent.com/user/repo/main/file.txt", "https://raw.githubusercontent.com/user/repo/main/file.txt"),
        ("https://example.com/file.txt", "https://example.com/file.txt"),
    ]
)
def test_prepare_github_url(input_url: str, expected_url: str):
    """Testa a lógica de adicionar '?raw=true' a URLs do GitHub."""
    loader = DocumentLoader("dummy_dir")  # o diretório não importa aqui
    prepared_url = loader.prepare_github_url(input_url)
    assert prepared_url == expected_url


def test_carregar_success(tmp_path: Path, mocker):
    """Testa o download e salvamento bem-sucedido de um arquivo."""
    # Mock da resposta do requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "conteúdo do arquivo"
    mock_response.raise_for_status.return_value = None

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    loader = DocumentLoader(str(tmp_path))
    urls = ["http://example.com/testfile.txt"]

    downloaded_files = loader.carregar(urls)

    # Verifica se a chamada de rede foi feita
    mock_get.assert_called_once_with("http://example.com/testfile.txt", timeout=30)

    # Verifica se o arquivo foi salvo corretamente
    expected_file = tmp_path / "testfile.txt"
    assert downloaded_files == [expected_file]
    assert expected_file.exists()
    assert expected_file.read_text(encoding="utf-8") == "conteúdo do arquivo"


def test_carregar_file_already_exists(tmp_path: Path, mocker):
    """Testa se o download é pulado se o arquivo já existir."""
    # Cria um arquivo pré-existente
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("conteúdo antigo", encoding="utf-8")

    mock_get = mocker.patch("requests.get")

    loader = DocumentLoader(str(tmp_path))
    urls = ["http://example.com/existing.txt"]

    downloaded_files = loader.carregar(urls)

    # Verifica se a chamada de rede NÃO foi feita
    mock_get.assert_not_called()

    # Verifica se o caminho do arquivo existente é retornado
    assert downloaded_files == [existing_file]
    # Verifica se o conteúdo não foi alterado
    assert existing_file.read_text(encoding="utf-8") == "conteúdo antigo"


def test_carregar_download_failure(tmp_path: Path, mocker, caplog):
    """Testa o comportamento em caso de falha no download (RequestException)."""
    # Mock do requests.get para levantar uma exceção
    mock_get = mocker.patch("requests.get", side_effect=requests.RequestException("Erro de rede"))

    loader = DocumentLoader(str(tmp_path))
    urls = ["http://example.com/failed.txt"]

    downloaded_files = loader.carregar(urls)

    # Verifica se a chamada de rede foi tentada
    mock_get.assert_called_once()

    # Verifica se nenhum arquivo foi retornado
    assert not downloaded_files

    # Verifica se o arquivo não foi criado
    assert not (tmp_path / "failed.txt").exists()

    # Verifica se o erro foi logado
    assert "Falha ao baixar" in caplog.text
    assert "Erro de rede" in caplog.text


def test_carregar_multiple_urls_mixed_results(tmp_path: Path, mocker, caplog):
    """Testa o download de múltiplos arquivos com sucessos e falhas."""
    # Mock para simular respostas diferentes para URLs diferentes
    def mock_get_logic(url, _timeout):
        if "success.txt" in url:
            mock_response = MagicMock()
            mock_response.text = "sucesso"
            mock_response.raise_for_status.return_value = None
            return mock_response
        if "failure.txt" in url:
            raise requests.RequestException("Falha no download")
        raise AssertionError(f"URL inesperada para requests.get: {url}")

    mocker.patch("requests.get", side_effect=mock_get_logic)

    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("já estava aqui", encoding="utf-8")

    loader = DocumentLoader(str(tmp_path))
    urls = ["http://example.com/success.txt", "http://example.com/failure.txt", "http://example.com/existing.txt"]
    downloaded_files = loader.carregar(urls)

    expected_files = [tmp_path / "success.txt", existing_file]
    assert set(downloaded_files) == set(expected_files)
    assert (tmp_path / "success.txt").read_text(encoding="utf-8") == "sucesso"
    assert not (tmp_path / "failure.txt").exists()
    assert "Falha ao baixar de 'http://example.com/failure.txt'" in caplog.text
