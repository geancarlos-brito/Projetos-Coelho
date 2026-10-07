from enum import Enum


class StatusContrato(str, Enum):
    ATIVO = "ativo"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"
