from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Movimentacao, Produto
from app.schemas.movimentacao import (
    MovimentacaoCreate,
    MovimentacaoResponse,
    MovimentacaoUpdate,
)

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


def _buscar_ou_404(db: Session, movimentacao_id: int) -> Movimentacao:
    movimentacao = db.get(Movimentacao, movimentacao_id)
    if movimentacao is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Movimentação não encontrada")
    return movimentacao


@router.post(
    "/", response_model=MovimentacaoResponse, status_code=status.HTTP_201_CREATED
)
def registrar_movimentacao(dados: MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = db.get(Produto, dados.produto_id)
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto informado não existe")

    if dados.tipo == "entrada":
        produto.quantidade += dados.quantidade
    else:
        if dados.quantidade > produto.quantidade:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Estoque insuficiente: disponível {produto.quantidade}, "
                f"solicitado {dados.quantidade}",
            )
        produto.quantidade -= dados.quantidade

    movimentacao = Movimentacao(**dados.model_dump())
    db.add(movimentacao)
    db.commit()  # saldo do produto e movimentação são gravados juntos
    db.refresh(movimentacao)
    return movimentacao


@router.get("/", response_model=list[MovimentacaoResponse])
def listar_movimentacoes(
    produto_id: int | None = None,
    tipo: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    consulta = select(Movimentacao)
    if produto_id is not None:
        consulta = consulta.where(Movimentacao.produto_id == produto_id)
    if tipo is not None:
        consulta = consulta.where(Movimentacao.tipo == tipo)
    consulta = consulta.order_by(Movimentacao.id.desc()).offset(skip).limit(limit)
    return db.scalars(consulta).all()


@router.get("/{movimentacao_id}", response_model=MovimentacaoResponse)
def obter_movimentacao(movimentacao_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, movimentacao_id)


@router.patch("/{movimentacao_id}", response_model=MovimentacaoResponse)
def corrigir_motivo(
    movimentacao_id: int, dados: MovimentacaoUpdate, db: Session = Depends(get_db)
):
    movimentacao = _buscar_ou_404(db, movimentacao_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(movimentacao, campo, valor)
    db.commit()
    db.refresh(movimentacao)
    return movimentacao
