from datetime import date

from models.cliente import Cliente
from models.condutor import Condutor
from models.enums import StatusContrato
from models.veiculo import Veiculo


class Contrato:
    _proximo_id = 1

    def __init__(self, cliente: Cliente, veiculo: Veiculo,
                 data_inicio: date, data_fim_prevista: date,
                 nome_condutor: str, cnh_condutor: str):
        self.id = Contrato._proximo_id
        Contrato._proximo_id += 1

        # ASSOCIAÇÃO: Cliente e Veiculo existem independentemente do Contrato
        self.cliente = cliente
        self.veiculo = veiculo

        self.data_inicio = data_inicio
        self.data_fim_prevista = data_fim_prevista
        self.status = StatusContrato.ATIVO

        # COMPOSIÇÃO: o Contrato INSTANCIA o Condutor. Ninguém de fora cria
        # nem guarda esse objeto; ele nasce e morre junto com o Contrato.
        self.condutor = Condutor(nome_condutor, cnh_condutor)

    def calcular_valor_total(self) -> float:
        dias = max((self.data_fim_prevista - self.data_inicio).days, 1)
        return dias * self.veiculo.calcular_diaria()

    @property
    def valor_total(self) -> float:
        return self.calcular_valor_total()

    def finalizar(self) -> None:
        self.status = StatusContrato.FINALIZADO

    def cancelar(self) -> None:
        self.status = StatusContrato.CANCELADO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": self.cliente.nome,
            "veiculo": self.veiculo.placa,
            "data_inicio": self.data_inicio,
            "data_fim_prevista": self.data_fim_prevista,
            "valor_total": self.valor_total,
            "status": self.status,
            "condutor": self.condutor.to_dict(),
        }
