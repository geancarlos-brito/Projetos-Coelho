from fastapi import FastAPI

from app.routers import categorias, movimentacoes, produtos

app = FastAPI(
    title="Gerenciador de Estoque",
    description="Controle de categorias, produtos e movimentações de estoque.",
    version="1.0.0",
)

app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)


@app.get("/", tags=["Health"])
def raiz():
    return {"status": "ok", "docs": "/docs"}
