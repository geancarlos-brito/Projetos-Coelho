from fastapi import APIRouter, HTTPException

import database as db
from models import Contrato, StatusContrato
from schemas import ContratoIn

router = APIRouter(prefix="/contratos", tags=["Contratos"])


def _buscar(contrato_id: int) -> Contrato:
    contrato = db.contratos.get(contrato_id)
    if not contrato:
        raise HTTPException(404, "Contrato não encontrado.")
    return contrato


@router.post("", status_code=201)
def criar_contrato(dados: ContratoIn):
    cliente = db.clientes.get(dados.documento_cliente)
    veiculo = db.veiculos.get(dados.placa_veiculo)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")
    if dados.data_fim_prevista < dados.data_inicio:
        raise HTTPException(422, "Data de término anterior à data de início.")

    # Regra: um veículo não pode estar em dois contratos ativos ao mesmo tempo
    if any(c.veiculo is veiculo and c.status == StatusContrato.ATIVO
           for c in db.contratos.values()):
        raise HTTPException(409, "Veículo já está em um contrato ativo.")

    contrato = Contrato(cliente, veiculo, dados.data_inicio, dados.data_fim_prevista,
                        dados.nome_condutor, dados.cnh_condutor)
    if not contrato.condutor.cnh_valida():
        raise HTTPException(422, "CNH inválida.")
    db.contratos[contrato.id] = contrato
    return contrato.to_dict()


@router.get("/{contrato_id}")
def obter_contrato(contrato_id: int):
    return _buscar(contrato_id).to_dict()


@router.patch("/{contrato_id}/finalizar")
def finalizar_contrato(contrato_id: int):
    contrato = _buscar(contrato_id)
    contrato.finalizar()
    return contrato.to_dict()


@router.patch("/{contrato_id}/cancelar")
def cancelar_contrato(contrato_id: int):
    contrato = _buscar(contrato_id)
    contrato.cancelar()
    return contrato.to_dict()


@router.delete("/{contrato_id}")
def excluir_contrato(contrato_id: int):
    """COMPOSIÇÃO em ação: ao remover o contrato, o Condutor some junto
    (não existe nenhuma outra referência para ele)."""
    _buscar(contrato_id)
    del db.contratos[contrato_id]
    return {"mensagem": "Contrato e condutor associado removidos."}
