import sqlite3
from contextlib import asynccontextmanager, closing

from fastapi import FastAPI, HTTPException, status # Importa a classe necessária da lib fastapi para a aplicação
# Inicializar o ambiente virtual --> .\.venv\Scripts\Activate.ps1
# python -m uvicorn app.main:app --reload --> Comando para executar a API localmente, o --reload reinicia o servidor quando os arquivos Python são alterados (Só sera utilizado durante o desenvolvimento)

from app.database import criar_tabelas, conectar_db
from app.models import IncidenteCreate, IncidenteUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas() # A função de criar tabelas é chamada na inicialização, antes da aplicação começar a atender requisições
    yield

# Cria a instância principal da API e define algumas informações que aparecerão na documentação
app = FastAPI(
    title="CyberDesk API",
    description = "API para gerenciamento de chamados de incidentes de cybersecurity",
    version = "1.0.0",
    lifespan = lifespan # Mecanismo responsável por executar operações durante a inicialização e o encerramento da API
)


@app.get("/") # Registra um endpoint principal da API (no caminho root)
def home():
    return{
        "aplicacao": "CyberDesk API",
        "status": "online"
    }

@app.get("/health") # Registra um endpoint usado para verificar se a aplicação está respondendo
def health_check():
    return{
        "status": "healthy"
    }

# CREATE - Cadastra o Incidente
@app.post("/incidentes", status_code=status.HTTP_201_CREATED)
def criar_incidente(incidente: IncidenteCreate):
    with closing(conectar_db()) as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO incidentes
            (titulo, descricao, categoria, severidade, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                incidente.titulo,
                incidente.descricao,
                incidente.categoria,
                incidente.severidade,
                "Aberto"
            )
        )

        incidente_id = cursor.lastrowid
        conexao.commit()

        registro = conexao.execute(
            "SELECT * FROM incidentes WHERE id = ?",
            (incidente_id,)
        ).fetchone()

        return dict(registro)

# READ - Listar Incidentes
@app.get("/incidentes")
def listar_incidentes():
    with closing(conectar_db()) as conexao:
        registros = conexao.execute(
            "SELECT * FROM incidentes ORDER BY id"
        ).fetchall()

        return [dict(registro) for registro in registros]

# READ - Consultar Incidente por ID
@app.get("/incidentes/{incidente_id}")
def buscar_incidente(incidente_id: int):

    with closing(conectar_db()) as conexao:
        registro = conexao.execute(
            "SELECT * FROM incidentes WHERE id = ?",
            (incidente_id,)
        ).fetchone()

        if registro is None:
            raise HTTPException(
                status_code = 404,
                detail="Incidente nao encontrado."
            )

        return dict(registro)

# UPDATE - Atualizar incidente
@app.put("/incidentes/{incidente_id}")
def atualizar_incidente(
    incidente_id: int,
    incidente: IncidenteUpdate
):
    with closing(conectar_db()) as conexao:
        cursor = conexao.execute(
            """
            UPDATE incidentes
            SET titulo = ?,
            descricao = ?,
            categoria = ?,
            severidade = ?,
            status = ?
        WHERE id = ?
        """,
        (
            incidente.titulo,
            incidente.descricao,
            incidente.categoria,
            incidente.severidade,
            incidente.status,
            incidente_id
        )
    )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Incidente nao encontrado."
            )

        conexao.commit()

        registro = conexao.execute(
            "SELECT * FROM incidentes WHERE id = ?",
            (incidente_id,)
        ).fetchone()

        return dict(registro)

# DELETE - Excluir Incidente
@app.delete("/incidentes/{incidente_id}")
def excluir_incidente(incidente_id: int):
    with closing(conectar_db()) as conexao:
        cursor = conexao.execute(
            "DELETE FROM incidentes WHERE id = ?",
            (incidente_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Incidente nao encontrado."
            )
        conexao.commit()

        return {"mensagem": "Incidente excluido com sucesso."}

