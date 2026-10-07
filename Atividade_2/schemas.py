"""Schemas Pydantic: formato dos dados que a API recebe."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel


class VeiculoIn(BaseModel):
    tipo: Literal["carro", "moto", "caminhao"]
    placa: str
    modelo: str
    ano: int
    valor_diaria: float
    num_portas: Optional[int] = 4
    cilindradas: Optional[int] = 150
    capacidade_carga_kg: Optional[float] = 0


class ClienteIn(BaseModel):
    tipo: Literal["fisica", "juridica"]
    nome: str
    documento: str
    telefone: str


class ContratoIn(BaseModel):
    documento_cliente: str
    placa_veiculo: str
    data_inicio: date
    data_fim_prevista: date
    nome_condutor: str
    cnh_condutor: str


class ManutencaoIn(BaseModel):
    data: date
    tipo_servico: str
    custo: float
