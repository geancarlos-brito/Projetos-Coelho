from abc import ABC, abstractmethod


class Cliente(ABC):
    def __init__(self, nome: str, documento: str, telefone: str):
        self.nome = nome
        self.documento = documento
        self.telefone = telefone

    @abstractmethod
    def documento_valido(self) -> bool:
        ...

    def atualizar_telefone(self, novo: str) -> None:
        self.telefone = novo

    def to_dict(self) -> dict:
        return {
            "tipo": self.__class__.__name__,
            "nome": self.nome,
            "documento": self.documento,
            "telefone": self.telefone,
        }


class PessoaFisica(Cliente):
    def documento_valido(self) -> bool:  # validação simplificada (CPF)
        return len(self.documento) == 11 and self.documento.isdigit()


class PessoaJuridica(Cliente):
    def documento_valido(self) -> bool:  # validação simplificada (CNPJ)
        return len(self.documento) == 14 and self.documento.isdigit()
