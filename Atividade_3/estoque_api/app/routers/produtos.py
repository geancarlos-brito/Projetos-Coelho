from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Categoria, Movimentacao, Produto
from app.schemas.movimentacao import MovimentacaoResponse
from app.schemas.produto import ProdutoCreate, ProdutoResponse, ProdutoUpdate

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _buscar_ou_404(db: Session, produto_id: int) -> Produto:
    produto = db.get(Produto, produto_id)
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
    return produto


def _garantir_categoria(db: Session, categoria_id: int):
    if db.get(Categoria, categoria_id) is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Categoria informada não existe"
        )


def _garantir_sku_livre(db: Session, sku: str, ignorar_id: int | None = None):
    existente = db.scalar(select(Produto).where(Produto.sku == sku))
    if existente and existente.id != ignorar_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "SKU já cadastrado")


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    _garantir_categoria(db, dados.categoria_id)
    _garantir_sku_livre(db, dados.sku)
    produto = Produto(**dados.model_dump())  # quantidade inicia em 0
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(
    categoria_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    consulta = select(Produto)
    if categoria_id is not None:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    return db.scalars(consulta.offset(skip).limit(limit)).all()


# Precisa vir antes de "/{produto_id}" para não ser lida como um id.
@router.get("/baixo-estoque", response_model=list[ProdutoResponse])
def listar_produtos_com_estoque_baixo(db: Session = Depends(get_db)):
    consulta = select(Produto).where(Produto.quantidade <= Produto.estoque_minimo)
    return db.scalars(consulta).all()


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, produto_id)


@router.get("/{produto_id}/movimentacoes", response_model=list[MovimentacaoResponse])
def listar_movimentacoes_do_produto(produto_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, produto_id).movimentacoes


@router.patch("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)
):
    produto = _buscar_ou_404(db, produto_id)
    campos = dados.model_dump(exclude_unset=True)
    if campos.get("categoria_id") is not None:
        _garantir_categoria(db, campos["categoria_id"])
    if campos.get("sku"):
        _garantir_sku_livre(db, campos["sku"], ignorar_id=produto_id)
    for campo, valor in campos.items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = _buscar_ou_404(db, produto_id)
    if db.scalar(
        select(Movimentacao.id).where(Movimentacao.produto_id == produto_id).limit(1)
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Produto possui movimentações e não pode ser removido",
        )
    db.delete(produto)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
