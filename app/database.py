import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "data" / "cyberdesk.db"

def conectar_db():
    conexao = sqlite3.connect(DATABASE_PATH) # Abre uma conexão com o arquivo SQLite
    conexao.row_factory = sqlite3.Row # Comando que permite acessar os resultados de consultas utilizando nomes de colunas, ao invés de somente posições numéricas
    return conexao

# Função que cria uma tabela no banco somente se ela não existir ainda, garantindo a persistência
# Define um ID único para cada incidente
# Armazena automaticamente data e hora UTC da criação
def criar_tabelas():
    with conectar_db() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                categoria TEXT NOT NULL,
                severidade TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Aberto',
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
    conexao.commit()

