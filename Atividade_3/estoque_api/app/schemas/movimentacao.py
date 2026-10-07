from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MovimentacaoCreate(BaseModel):
    produto_id: int = Field(gt=0)
    tipo: Literal["entrada", "saida"]
    quantidade: int = Field(gt=0)
    motivo: str | None = Field(default=None, max_length=200)


class MovimentacaoUpdate(BaseModel):
    # Só o motivo pode ser corrigido; tipo e quantidade alterariam o saldo.
    motivo: str | None = Field(default=None, max_length=200)


class MovimentacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    tipo: str
    quantidade: int
    motivo: str | None
    criado_em: datetime
