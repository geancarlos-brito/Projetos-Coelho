"""
Ponto de entrada da aplicação - Locadora de Veículos.

Executar:
    pip install fastapi uvicorn
    python main.py

Documentação interativa: http://127.0.0.1:8000/docs
"""
import uvicorn
from fastapi import FastAPI

from routers import clientes, contratos, veiculos

app = FastAPI(title="Locadora de Veículos", version="1.0")

app.include_router(veiculos.router)
app.include_router(clientes.router)
app.include_router(contratos.router)


@app.get("/", tags=["Início"])
def raiz():
    return {"mensagem": "API da Locadora no ar. Acesse /docs para testar."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
