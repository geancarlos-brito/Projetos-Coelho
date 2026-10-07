from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Categoria, Produto
from app.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.schemas.produto import ProdutoResponse

router = APIRouter(prefix="/categorias", tags=["Categorias"])


def _buscar_ou_404(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Categoria não encontrada")
    return categoria


def _garantir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None):
    existente = db.scalar(select(Categoria).where(Categoria.nome == nome))
    if existente and existente.id != ignorar_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Categoria já cadastrada")


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    _garantir_nome_livre(db, dados.nome)
    categoria = Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("/", response_model=list[CategoriaResponse])
def listar_categorias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).offset(skip).limit(limit)).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, categoria_id)


@router.get("/{categoria_id}/produtos", response_model=list[ProdutoResponse])
def listar_produtos_da_categoria(categoria_id: int, db: Session = Depends(get_db)):
    return _buscar_ou_404(db, categoria_id).produtos


@router.patch("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)
):
    categoria = _buscar_ou_404(db, categoria_id)
    campos = dados.model_dump(exclude_unset=True)
    if campos.get("nome"):
        _garantir_nome_livre(db, campos["nome"], ignorar_id=categoria_id)
    for campo, valor in campos.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = _buscar_ou_404(db, categoria_id)
    if db.scalar(select(Produto.id).where(Produto.categoria_id == categoria_id).limit(1)):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Categoria possui produtos e não pode ser removida",
        )
    db.delete(categoria)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
