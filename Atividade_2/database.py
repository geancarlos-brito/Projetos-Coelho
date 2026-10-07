"""'Banco de dados' em memória (dicionários). Os dados somem ao reiniciar a API."""
from models import Cliente, Contrato, Veiculo

veiculos: dict[str, Veiculo] = {}      # chave: placa
clientes: dict[str, Cliente] = {}      # chave: documento
contratos: dict[int, Contrato] = {}    # chave: id
