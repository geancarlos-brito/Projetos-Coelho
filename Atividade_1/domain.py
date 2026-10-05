from __future__ import annotations

from itertools import count
from typing import Optional

_gerador_id = count(1)


def _novo_id() -> int:
    return next(_gerador_id)


# Endereço
class Endereco:
    def __init__(self, rua: str, numero: str, bairro: str, cidade: str,
                 estado: str, cep: str):
        self.id = _novo_id()
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def formatar(self) -> str:
        return (f"{self.rua}, {self.numero} - {self.bairro}, "
                f"{self.cidade}/{self.estado} - CEP {self.cep}")

    def atualizar(self, **campos) -> None:
        for chave, valor in campos.items():
            if valor is not None and hasattr(self, chave) and chave != "id":
                setattr(self, chave, valor)


# Aluno
class Aluno:
    def __init__(self, nome: str, matricula: str, data_nascimento: str,
                 endereco: Endereco):
        self.id = _novo_id()
        self.nome = nome
        self.matricula = matricula
        self.data_nascimento = data_nascimento
        self.endereco: Optional[Endereco] = endereco

    @classmethod
    def cadastrar(cls, nome: str, matricula: str, data_nascimento: str,
                  **dados_endereco) -> "Aluno":
        """O endereço é criado junto com o cadastro do aluno."""
        return cls(nome, matricula, data_nascimento, Endereco(**dados_endereco))

    def atualizar_endereco(self, **campos) -> None:
        if self.endereco:
            self.endereco.atualizar(**campos)

    def remover(self) -> Optional[Endereco]:
        """Remove o aluno, mas devolve o endereço para continuar existindo
        em outro contexto (ex.: relatórios). Isso é o que caracteriza a agregação."""
        endereco, self.endereco = self.endereco, None
        return endereco


# SalaDeAula
class SalaDeAula:
    def __init__(self, numero: str, capacidade: int):
        self.id = _novo_id()
        self.numero = numero
        self.capacidade = capacidade

    def tem_vaga(self, ocupacao_atual: int) -> bool:
        return ocupacao_atual < self.capacidade

    def alterar_capacidade(self, nova_capacidade: int) -> None:
        if nova_capacidade <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        self.capacidade = nova_capacidade


# Professor
class Professor:
    def __init__(self, nome: str, cpf: str, disciplina: str):
        self.id = _novo_id()
        self.nome = nome
        self.cpf = cpf
        self.disciplina = disciplina
        self.escolas: list["Escola"] = []

    def lecionar_em(self, escola: "Escola") -> None:
        if escola not in self.escolas:
            self.escolas.append(escola)
        if self not in escola.professores:
            escola.professores.append(self)

    def deixar_escola(self, escola: "Escola") -> None:
        if escola in self.escolas:
            self.escolas.remove(escola)
        if self in escola.professores:
            escola.professores.remove(self)

    def desvincular_de_todas(self) -> None:
        for escola in list(self.escolas):
            self.deixar_escola(escola)


# Escola
class Escola:
    def __init__(self, nome: str, cnpj: str):
        self.id = _novo_id()
        self.nome = nome
        self.cnpj = cnpj
        self._salas: list[SalaDeAula] = []      
        self.professores: list[Professor] = []  

    # composição
    @property
    def salas(self) -> list[SalaDeAula]:
        return list(self._salas)

    def adicionar_sala(self, numero: str, capacidade: int) -> SalaDeAula:
        """A escola cria a sala: ninguém de fora instancia a parte."""
        if any(s.numero == numero for s in self._salas):
            raise ValueError(f"Já existe a sala {numero} nesta escola.")
        sala = SalaDeAula(numero, capacidade)
        self._salas.append(sala)
        return sala

    def buscar_sala(self, sala_id: int) -> Optional[SalaDeAula]:
        return next((s for s in self._salas if s.id == sala_id), None)

    def remover_sala(self, sala_id: int) -> bool:
        sala = self.buscar_sala(sala_id)
        if sala:
            self._salas.remove(sala)
        return sala is not None

    def encerrar(self) -> None:
        """Fechar a escola destrói as salas; os professores continuam existindo."""
        self._salas.clear()
        for professor in list(self.professores):
            professor.deixar_escola(self)

    def capacidade_total(self) -> int:
        return sum(s.capacidade for s in self._salas)
