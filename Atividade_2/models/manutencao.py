from datetime import date


class Manutencao:
    def __init__(self, data: date, tipo_servico: str, custo: float):
        self.data = data
        self.tipo_servico = tipo_servico
        self.custo = custo

    def resumo(self) -> str:
        return f"{self.data:%d/%m/%Y} - {self.tipo_servico} (R$ {self.custo:.2f})"

    def custo_acima_de(self, limite: float) -> bool:
        return self.custo > limite

    def to_dict(self) -> dict:
        return {"data": self.data, "tipo_servico": self.tipo_servico, "custo": self.custo}
