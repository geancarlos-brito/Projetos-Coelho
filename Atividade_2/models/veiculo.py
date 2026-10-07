from abc import ABC, abstractmethod

from models.manutencao import Manutencao


class Veiculo(ABC):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float):
        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.valor_diaria = valor_diaria
        # AGREGAÇÃO: o Veiculo guarda manutenções criadas fora dele
        self._manutencoes: list[Manutencao] = []

    @abstractmethod
    def calcular_diaria(self) -> float:
        """Valor da diária considerando a regra de cada tipo de veículo."""

    def registrar_manutencao(self, manutencao: Manutencao) -> None:
        """AGREGAÇÃO: recebe um objeto Manutencao já existente."""
        self._manutencoes.append(manutencao)

    def custo_total_manutencoes(self) -> float:
        return sum(m.custo for m in self._manutencoes)

    @property
    def manutencoes(self) -> list[Manutencao]:
        return list(self._manutencoes)

    def to_dict(self) -> dict:
        return {
            "tipo": self.__class__.__name__.lower(),
            "placa": self.placa,
            "modelo": self.modelo,
            "ano": self.ano,
            "valor_diaria": self.valor_diaria,
            "diaria_calculada": self.calcular_diaria(),
        }


class Carro(Veiculo):
    def __init__(self, placa, modelo, ano, valor_diaria, num_portas: int = 4):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.num_portas = num_portas

    def calcular_diaria(self) -> float:
        return self.valor_diaria

    def to_dict(self) -> dict:
        return {**super().to_dict(), "num_portas": self.num_portas}


class Moto(Veiculo):
    def __init__(self, placa, modelo, ano, valor_diaria, cilindradas: int = 150):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.cilindradas = cilindradas

    def calcular_diaria(self) -> float:
        return self.valor_diaria

    def to_dict(self) -> dict:
        return {**super().to_dict(), "cilindradas": self.cilindradas}


class Caminhao(Veiculo):
    TAXA_ADICIONAL = 0.10  # regra assumida: +10% por ser veículo pesado

    def __init__(self, placa, modelo, ano, valor_diaria, capacidade_carga_kg: float = 0):
        super().__init__(placa, modelo, ano, valor_diaria)
        self.capacidade_carga_kg = capacidade_carga_kg

    def calcular_diaria(self) -> float:
        return round(self.valor_diaria * (1 + self.TAXA_ADICIONAL), 2)

    def to_dict(self) -> dict:
        return {**super().to_dict(), "capacidade_carga_kg": self.capacidade_carga_kg}
