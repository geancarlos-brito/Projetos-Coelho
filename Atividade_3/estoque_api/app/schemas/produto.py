from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    sku: str = Field(min_length=2, max_length=40)
    preco: float = Field(gt=0)
    estoque_minimo: int = Field(default=0, ge=0)
    categoria_id: int = Field(gt=0)


class ProdutoUpdate(BaseModel):
    # A quantidade não é editável aqui: só muda por movimentações.
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    sku: str | None = Field(default=None, min_length=2, max_length=40)
    preco: float | None = Field(default=None, gt=0)
    estoque_minimo: int | None = Field(default=None, ge=0)
    categoria_id: int | None = Field(default=None, gt=0)


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sku: str
    preco: float
    quantidade: int
    estoque_minimo: int
    categoria_id: int
