"""
Testes para o parser de resenhas em `src.tools.parser`.
"""
from pathlib import Path

import pytest

from src.models import ReviewRaw
from src.tools.parser import read_reviews_from_file

# Conteúdo de exemplo para o arquivo de teste
# Inclui casos normais, linha em branco, linha com '$' no texto, e linha mal-formatada
# E agora, um caso de resenha que se estende por múltiplas linhas.
DUMMY_CONTENT = (
    "123$UserA$This is a great app!\n"
    "456$UserB$Não gostei, muito lento.\n"
    # Resenha 789 se estende por múltiplas linhas
    "789$UserC$J'aime bien, mais...\n"
    "cette partie est sur une nouvelle ligne.\n"
    "\n"  # Linha em branco deve ser ignorada na junção
    "101$UserD$This review contains a $ dollar sign.\n"
    # Esta linha será anexada à resenha 101, pois não corresponde ao início de uma nova resenha.
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
    # Com a lógica de multi-linha, esperamos 4 resenhas:
    # 1. UserA, 2. UserB, 3. UserC (multi-linha), 4. UserD (com a linha mal-formada anexada)
    assert len(reviews) == 4

    # Verifica a primeira resenha
    assert isinstance(reviews[0], ReviewRaw)
    assert reviews[0].id == "123"
    assert reviews[0].user == "UserA"
    assert reviews[0].text == "This is a great app!"

    # Verifica a resenha multi-linha (UserC)
    assert reviews[2].id == "789"
    assert reviews[2].user == "UserC"
    assert reviews[2].text == "J'aime bien, mais... cette partie est sur une nouvelle ligne."

    # Verifica como a resenha 101 foi tratada, agora incluindo a linha seguinte
    assert reviews[3].id == "101"
    assert reviews[3].user == "UserD"
    assert (
        reviews[3].text == "This review contains a $ dollar sign. MalformedLineWithoutSeparator"
    )

def test_read_reviews_from_non_existent_file():
    """
    Testa se a função levanta FileNotFoundError para um arquivo que não existe.
    """
    non_existent_path = Path("non_existent_dir/non_existent_file.txt")

    # Verifica se a exceção correta é levantada usando o gerenciador de contexto do pytest
    with pytest.raises(FileNotFoundError, match="O arquivo de resenhas não foi encontrado"):
        read_reviews_from_file(non_existent_path)
