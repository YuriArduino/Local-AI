"""
Testes para o parser de resenhas em `src.tools.parser`.
"""
from pathlib import Path

import pytest

from src.models import ReviewRaw
from src.tools.parser import read_reviews_from_file

# Conteúdo de exemplo para o arquivo de teste
# Inclui casos normais, linha em branco, linha com '$' no texto, e linha mal-formatada
DUMMY_CONTENT = (
    "123$UserA$This is a great app!\n"
    "456$UserB$Não gostei, muito lento.\n"
    "789$UserC$J'aime bien, mais...\n"
    "\n"  # Linha em branco para testar se é ignorada
    "101$UserD$This review contains a $ dollar sign.\n"
    "MalformedLineWithoutSeparator\n"
)

def test_read_reviews_from_file_success(tmp_path: Path):
    """
    Testa a leitura e o parsing de um arquivo de resenhas bem-sucedido.
    Verifica se o número de resenhas está correto e se os dados são parseados como esperado.
    """
    # 1. Cria um arquivo de teste em um diretório temporário fornecido pelo pytest
    test_file_path = tmp_path / "resenhas_teste.txt"
    test_file_path.write_text(DUMMY_CONTENT, encoding="utf-8")

    # 2. Executa a função a ser testada
    reviews = read_reviews_from_file(test_file_path)

    # 3. Verifica os resultados com asserts
    # A linha em branco deve ser ignorada, então esperamos 5 resenhas.
    assert len(reviews) == 5

    # Verifica a primeira resenha
    assert isinstance(reviews[0], ReviewRaw)
    assert reviews[0].id == "123"
    assert reviews[0].user == "UserA"
    assert reviews[0].text == "This is a great app!"

    # Verifica a resenha que contém um '$'
    assert reviews[3].id == "101"
    assert reviews[3].user == "UserD"
    assert reviews[3].text == "This review contains a $ dollar sign."

    # Verifica como a linha mal-formatada foi tratada pelo parser
    assert reviews[4].id == "MalformedLineWithoutSeparator"
    assert reviews[4].user == ""
    assert reviews[4].text == ""

def test_read_reviews_from_non_existent_file():
    """
    Testa se a função levanta FileNotFoundError para um arquivo que não existe.
    """
    non_existent_path = Path("non_existent_dir/non_existent_file.txt")

    # Verifica se a exceção correta é levantada usando o gerenciador de contexto do pytest
    with pytest.raises(FileNotFoundError, match="O arquivo de resenhas não foi encontrado"):
        read_reviews_from_file(non_existent_path)
