from fastapi import APIRouter, HTTPException

import database as db
from models import Caminhao, Carro, Manutencao, Moto
from schemas import ManutencaoIn, VeiculoIn

router = APIRouter(prefix="/veiculos", tags=["Veículos e manutenções"])


@router.post("", status_code=201)
def criar_veiculo(dados: VeiculoIn):
    if dados.placa in db.veiculos:
        raise HTTPException(409, "Placa já cadastrada.")
    base = (dados.placa, dados.modelo, dados.ano, dados.valor_diaria)
    if dados.tipo == "carro":
        v = Carro(*base, num_portas=dados.num_portas)
    elif dados.tipo == "moto":
        v = Moto(*base, cilindradas=dados.cilindradas)
    else:
        v = Caminhao(*base, capacidade_carga_kg=dados.capacidade_carga_kg)
    db.veiculos[v.placa] = v
    return v.to_dict()


@router.get("")
def listar_veiculos():
    return [v.to_dict() for v in db.veiculos.values()]


@router.post("/{placa}/manutencoes", status_code=201)
def registrar_manutencao(placa: str, dados: ManutencaoIn):
    veiculo = db.veiculos.get(placa)
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")
    # AGREGAÇÃO: a Manutencao é criada aqui fora e entregue ao Veiculo
    manutencao = Manutencao(dados.data, dados.tipo_servico, dados.custo)
    veiculo.registrar_manutencao(manutencao)
    return manutencao.to_dict()


@router.get("/{placa}/manutencoes")
def historico_manutencoes(placa: str):
    veiculo = db.veiculos.get(placa)
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado.")
    return {
        "placa": placa,
        "custo_total": veiculo.custo_total_manutencoes(),
        "historico": [m.to_dict() for m in veiculo.manutencoes],
    }
