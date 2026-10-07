class Condutor:
    def __init__(self, nome: str, cnh: str):
        self.nome = nome
        self.cnh = cnh

    def cnh_valida(self) -> bool:  # validação simplificada
        return len(self.cnh) == 11 and self.cnh.isdigit()

    def to_dict(self) -> dict:
        return {"nome": self.nome, "cnh": self.cnh}
