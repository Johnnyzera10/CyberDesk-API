# Comando para efetuar os testes automatizados --> python -m pytest tests/test_api.py -v

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import database

@pytest.fixture
def client(tmp_path, monkeypatch):
    banco_test = tmp_path / "teste_cyberdesk.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        banco_test
    )

    with TestClient(app) as client:
        yield client

def test_health(client):
    
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_criar_incidente(client):

    # Dados fictícios para cadastro
    novo_incidente = {
        "titulo": "Tentativa de Brute Force",
        "descricao": "Multiplas tentativas de login SSH",
        "categoria": "Autenticacao",
        "severidade": "Alta"
    }

    # Envia a requisição POST
    response = client.post(
        "/incidentes",
        json=novo_incidente
    )

    # Verifica o código HTTP
    assert response.status_code == 201

    # Converte a resposta em um dicionário
    dados = response.json()

    # Verifica os campos retornados
    assert dados["titulo"] == novo_incidente["titulo"]
    assert dados["severidade"] == "Alta"
    assert dados["status"] == "Aberto"
    assert isinstance(dados["id"], int)


def test_listar_incidentes(client):

    # Dados de um incidente fictício
    novo_incidente = {
        "titulo": "Acesso Nao Autorizado",
        "descricao": "Tentativa de acesso a sistema interno",
        "categoria": "Controle de Acesso",
        "severidade": "Alta"
    }

    # Cadastra um incidente no banco temporário
    cadastro = client.post(
        "/incidentes",
        json=novo_incidente
    )

    assert cadastro.status_code == 201

    # Consulta todos os incidentes cadastrados
    response = client.get("/incidentes")

    # Verifica se a requisição foi bem-sucedida
    assert response.status_code == 200

    # Converte o JSON retornado em uma lista Python
    incidentes = response.json()

    # Verifica se existe exatamente um incidente
    assert len(incidentes) == 1

    # Verifica se os dados correspondem ao cadastro
    assert incidentes[0]["titulo"] == "Acesso Nao Autorizado"
    assert incidentes[0]["categoria"] == "Controle de Acesso"
    assert incidentes[0]["status"] == "Aberto"


def test_buscar_incidente(client):

    # Dados fictícios de um incidente
    novo_incidente = {
        "titulo": "Phishing Corporativo",
        "descricao": "Email suspeito enviado a colaboradores",
        "categoria": "Engenharia Social",
        "severidade": "Alta"
    }

    # Cadastra o incidente no banco temporário
    cadastro = client.post(
        "/incidentes",
        json=novo_incidente
    )

    assert cadastro.status_code == 201

    # Recupera o ID gerado pelo SQLite
    incidente_id = cadastro.json()["id"]
    print("\nID cadastrado:", incidente_id)
    print("Resposta do POST:", cadastro.json())

    listagem = client.get("/incidentes")
    print("Incidentes encontrados:", listagem.json())

    # Consulta o incidente utilizando seu ID
    response = client.get(
        f"/incidentes/{incidente_id}"
    )

    print("URL consultada:", response.request.url)
    print("Status HTTP:", response.status_code)
    print("Resposta GET:", response.json())

    # Verifica o código HTTP
    assert response.status_code == 200

    # Converte a resposta JSON em dicionário
    dados = response.json()

    # Verifica os dados retornados
    assert dados["id"] == incidente_id
    assert dados["titulo"] == "Phishing Corporativo"
    assert dados["categoria"] == "Engenharia Social"
    assert dados["status"] == "Aberto"


def test_atualizar_incidente(client):

    # Dados iniciais do incidente
    novo_incidente = {
        "titulo": "Tentativa de Brute Force",
        "descricao": "Multiplas tentativas de login SSH",
        "categoria": "Autenticacao",
        "severidade": "Alta"
    }

    # Cadastra o incidente
    cadastro = client.post(
        "/incidentes",
        json=novo_incidente
    )

    assert cadastro.status_code == 201

    incidente_id = cadastro.json()["id"]

    # Prepara os dados atualizados
    dados_atualizados = {
        **novo_incidente,
        "status": "Resolvido"
    }

    # Atualiza o incidente
    response = client.put(
        f"/incidentes/{incidente_id}",
        json=dados_atualizados
    )

    # Verifica o resultado do PUT
    assert response.status_code == 200
    assert response.json()["status"] == "Resolvido"

    # Consulta novamente para confirmar a persistência
    consulta = client.get(
        f"/incidentes/{incidente_id}"
    )

    assert consulta.status_code == 200
    assert consulta.json()["status"] == "Resolvido"


def test_excluir_incidente(client):

    # Dados fictícios do incidente
    novo_incidente = {
        "titulo": "Malware Detectado",
        "descricao": "Arquivo malicioso identificado no endpoint",
        "categoria": "Malware",
        "severidade": "Alta"
    }

    # Cadastra o incidente
    cadastro = client.post(
        "/incidentes",
        json=novo_incidente
    )

    assert cadastro.status_code == 201

    incidente_id = cadastro.json()["id"]

    # Exclui o incidente cadastrado
    response = client.delete(
        f"/incidentes/{incidente_id}"
    )

    # Verifica se a exclusão foi bem-sucedida
    assert response.status_code == 200

    assert response.json() == {
        "mensagem": "Incidente excluido com sucesso."
    }

    # Tenta consultar o incidente excluído
    consulta = client.get(
        f"/incidentes/{incidente_id}"
    )

    # Confirma que o registro não existe mais
    assert consulta.status_code == 404
    assert consulta.json()["detail"] == "Incidente nao encontrado."


def test_incidente_inexistente(client):

    # Consulta um incidente que não existe
    response = client.get("/incidentes/99999")

    # Verifica o código HTTP 404
    assert response.status_code == 404

    # Confirma a mensagem retornada pela API
    assert response.json() == {
        "detail": "Incidente nao encontrado."
    }


def test_validacao_severidade(client):

    # Dados com uma severidade inválida
    incidente_invalido = {
        "titulo": "Tentativa de Brute Force",
        "descricao": "Multiplas tentativas de login SSH",
        "categoria": "Autenticacao",
        "severidade": "Extrema"
    }

    # Tenta cadastrar o incidente
    response = client.post(
        "/incidentes",
        json=incidente_invalido
    )

    # Verifica se a API rejeitou os dados inválidos
    assert response.status_code == 422

    # Consulta os registros do banco temporário
    consulta = client.get("/incidentes")

    # Confirma que nenhum incidente foi cadastrado
    assert consulta.status_code == 200
    assert consulta.json() == []