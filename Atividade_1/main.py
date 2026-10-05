from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from domain import Aluno, Endereco, Escola, Professor

app = FastAPI(
    title="Sistema Escolar - Trabalho Prático 01",
    description="Composição (Escola◆Sala), Associação (Professor—Escola) "
                "e Agregação (Aluno◇Endereço).",
)

# "Banco de dados" em memória
escolas: dict[int, Escola] = {}
professores: dict[int, Professor] = {}
alunos: dict[int, Aluno] = {}
enderecos_avulsos: dict[int, Endereco] = {}  


# Schemas
class EscolaIn(BaseModel):
    nome: str
    cnpj: str


class SalaIn(BaseModel):
    numero: str
    capacidade: int


class ProfessorIn(BaseModel):
    nome: str
    cpf: str
    disciplina: str


class EnderecoIn(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str


class AlunoIn(BaseModel):
    nome: str
    matricula: str
    data_nascimento: str
    endereco: EnderecoIn


class EnderecoUpdate(BaseModel):
    rua: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None


# Serializers
def _endereco(e: Optional[Endereco]):
    if e is None:
        return None
    return {**{k: v for k, v in vars(e).items()}, "formatado": e.formatar()}


def _sala(s, escola_id: int):
    return {"id": s.id, "numero": s.numero, "capacidade": s.capacidade,
            "escola_id": escola_id}


def _escola(e: Escola):
    return {"id": e.id, "nome": e.nome, "cnpj": e.cnpj,
            "salas": [_sala(s, e.id) for s in e.salas],
            "capacidade_total": e.capacidade_total(),
            "professores": [p.id for p in e.professores]}


def _professor(p: Professor):
    return {"id": p.id, "nome": p.nome, "cpf": p.cpf,
            "disciplina": p.disciplina, "escolas": [e.id for e in p.escolas]}


def _aluno(a: Aluno):
    return {"id": a.id, "nome": a.nome, "matricula": a.matricula,
            "data_nascimento": a.data_nascimento,
            "endereco": _endereco(a.endereco)}


def _obter(repo: dict, id_: int, nome: str):
    if id_ not in repo:
        raise HTTPException(404, f"{nome} {id_} não encontrado(a).")
    return repo[id_]


# Escola + Salas
@app.post("/escolas", status_code=201, tags=["Escola (composição)"])
def criar_escola(dados: EscolaIn):
    escola = Escola(dados.nome, dados.cnpj)
    escolas[escola.id] = escola
    return _escola(escola)


@app.get("/escolas", tags=["Escola (composição)"])
def listar_escolas():
    return [_escola(e) for e in escolas.values()]


@app.get("/escolas/{escola_id}", tags=["Escola (composição)"])
def obter_escola(escola_id: int):
    return _escola(_obter(escolas, escola_id, "Escola"))


@app.delete("/escolas/{escola_id}", tags=["Escola (composição)"])
def fechar_escola(escola_id: int):
    """Fecha a escola: as salas deixam de existir; os professores permanecem."""
    escola = _obter(escolas, escola_id, "Escola")
    qtd_salas = len(escola.salas)
    escola.encerrar()
    del escolas[escola_id]
    return {"mensagem": "Escola fechada.", "salas_destruidas": qtd_salas}


@app.post("/escolas/{escola_id}/salas", status_code=201, tags=["Escola (composição)"])
def criar_sala(escola_id: int, dados: SalaIn):
    escola = _obter(escolas, escola_id, "Escola")
    try:
        sala = escola.adicionar_sala(dados.numero, dados.capacidade)
    except ValueError as erro:
        raise HTTPException(400, str(erro))
    return _sala(sala, escola.id)


@app.get("/escolas/{escola_id}/salas", tags=["Escola (composição)"])
def listar_salas_da_escola(escola_id: int):
    escola = _obter(escolas, escola_id, "Escola")
    return [_sala(s, escola.id) for s in escola.salas]


@app.delete("/escolas/{escola_id}/salas/{sala_id}", tags=["Escola (composição)"])
def remover_sala(escola_id: int, sala_id: int):
    escola = _obter(escolas, escola_id, "Escola")
    if not escola.remover_sala(sala_id):
        raise HTTPException(404, "Sala não encontrada nesta escola.")
    return {"mensagem": "Sala removida."}


@app.get("/salas", tags=["Escola (composição)"])
def listar_todas_as_salas():
    """Salas não têm repositório próprio: só são alcançadas através das escolas."""
    return [_sala(s, e.id) for e in escolas.values() for s in e.salas]


# Professor — Escola
@app.post("/professores", status_code=201, tags=["Professor (associação)"])
def criar_professor(dados: ProfessorIn):
    prof = Professor(dados.nome, dados.cpf, dados.disciplina)
    professores[prof.id] = prof
    return _professor(prof)


@app.get("/professores", tags=["Professor (associação)"])
def listar_professores():
    return [_professor(p) for p in professores.values()]


@app.get("/professores/{prof_id}", tags=["Professor (associação)"])
def obter_professor(prof_id: int):
    return _professor(_obter(professores, prof_id, "Professor"))


@app.delete("/professores/{prof_id}", tags=["Professor (associação)"])
def remover_professor(prof_id: int):
    prof = _obter(professores, prof_id, "Professor")
    prof.desvincular_de_todas()
    del professores[prof_id]
    return {"mensagem": "Professor removido; as escolas continuam existindo."}


@app.post("/professores/{prof_id}/escolas/{escola_id}", tags=["Professor (associação)"])
def vincular_professor(prof_id: int, escola_id: int):
    prof = _obter(professores, prof_id, "Professor")
    escola = _obter(escolas, escola_id, "Escola")
    prof.lecionar_em(escola)
    return _professor(prof)


@app.delete("/professores/{prof_id}/escolas/{escola_id}", tags=["Professor (associação)"])
def desvincular_professor(prof_id: int, escola_id: int):
    prof = _obter(professores, prof_id, "Professor")
    escola = _obter(escolas, escola_id, "Escola")
    prof.deixar_escola(escola)
    return _professor(prof)


# Aluno e Endereço
@app.post("/alunos", status_code=201, tags=["Aluno (agregação)"])
def cadastrar_aluno(dados: AlunoIn):
    aluno = Aluno.cadastrar(dados.nome, dados.matricula, dados.data_nascimento,
                            **dados.endereco.model_dump())
    alunos[aluno.id] = aluno
    return _aluno(aluno)


@app.get("/alunos", tags=["Aluno (agregação)"])
def listar_alunos():
    return [_aluno(a) for a in alunos.values()]


@app.get("/alunos/{aluno_id}", tags=["Aluno (agregação)"])
def obter_aluno(aluno_id: int):
    return _aluno(_obter(alunos, aluno_id, "Aluno"))


@app.patch("/alunos/{aluno_id}/endereco", tags=["Aluno (agregação)"])
def atualizar_endereco(aluno_id: int, dados: EnderecoUpdate):
    aluno = _obter(alunos, aluno_id, "Aluno")
    aluno.atualizar_endereco(**dados.model_dump(exclude_none=True))
    return _aluno(aluno)


@app.delete("/alunos/{aluno_id}", tags=["Aluno (agregação)"])
def remover_aluno(aluno_id: int):
    aluno = _obter(alunos, aluno_id, "Aluno")
    endereco = aluno.remover()
    del alunos[aluno_id]
    if endereco:
        enderecos_avulsos[endereco.id] = endereco
    return {"mensagem": "Aluno removido; endereço preservado.",
            "endereco_preservado": _endereco(endereco)}


@app.get("/enderecos-avulsos", tags=["Aluno (agregação)"])
def listar_enderecos_avulsos():
    return [_endereco(e) for e in enderecos_avulsos.values()]
