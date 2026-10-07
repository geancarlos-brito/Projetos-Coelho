from fastapi import APIRouter, HTTPException

import database as db
from models import PessoaFisica, PessoaJuridica
from schemas import ClienteIn

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", status_code=201)
def criar_cliente(dados: ClienteIn):
    classe = PessoaFisica if dados.tipo == "fisica" else PessoaJuridica
    cliente = classe(dados.nome, dados.documento, dados.telefone)
    if not cliente.documento_valido():
        raise HTTPException(422, "Documento inválido para o tipo de cliente.")
    if cliente.documento in db.clientes:
        raise HTTPException(409, "Documento já cadastrado.")
    db.clientes[cliente.documento] = cliente
    return cliente.to_dict()


@router.get("")
def listar_clientes():
    return [c.to_dict() for c in db.clientes.values()]
