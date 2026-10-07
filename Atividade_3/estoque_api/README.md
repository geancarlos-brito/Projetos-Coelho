# Gerenciador de Estoque

## Modelo de negócio
API para controle de estoque de uma loja: produtos são organizados em **categorias** e cada entrada ou saída de mercadoria é registrada como uma **movimentação**, que atualiza automaticamente o saldo do produto.

## Entidades e relacionamentos

```
Categoria 1 ────< N Produto 1 ────< N Movimentação
```

| Entidade     | Atributos |
|--------------|-----------|
| Categoria    | id, nome (único), descricao |
| Produto      | id, nome, sku (único), preco, quantidade, estoque_minimo, categoria_id (FK) |
| Movimentação | id, produto_id (FK), tipo (`entrada` ou `saida`), quantidade, motivo, criado_em |

Regras de negócio:
- A quantidade de um produto começa em 0 e só muda por movimentações (não é editável via PATCH).
- Uma saída maior que o saldo disponível é recusada (409).
- Produto só é criado se a categoria existir; movimentação só é criada se o produto existir (404).
- Categoria com produtos e produto com movimentações não podem ser removidos (409).

## Estrutura
```
app/
  core/       configuração e conexão com o banco
  models/     modelos SQLAlchemy
  schemas/    schemas Pydantic (Create / Update / Response)
  routers/    endpoints
  main.py
alembic/      migrações
```

## Como rodar
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

alembic upgrade head             # cria o banco (estoque.db) via migração
uvicorn app.main:app --reload
```
Swagger: http://127.0.0.1:8000/docs

Para gerar uma nova migração após alterar os modelos:
```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```
O banco padrão é SQLite; para outro banco defina `DATABASE_URL`.

## Endpoints

| Método | Rota                              | Descrição |
|--------|-----------------------------------|-----------|
| POST   | /categorias/                      | Cria categoria (201) |
| GET    | /categorias/                      | Lista categorias |
| GET    | /categorias/{id}                  | Consulta categoria (404) |
| GET    | /categorias/{id}/produtos         | Produtos da categoria |
| PATCH  | /categorias/{id}                  | Atualiza categoria |
| DELETE | /categorias/{id}                  | Remove (409 se tiver produtos) |
| POST   | /produtos/                        | Cria produto; valida categoria (404) |
| GET    | /produtos/                        | Lista produtos (filtro `categoria_id`) |
| GET    | /produtos/baixo-estoque           | Produtos com quantidade ≤ estoque mínimo |
| GET    | /produtos/{id}                    | Consulta produto |
| GET    | /produtos/{id}/movimentacoes      | Histórico do produto |
| PATCH  | /produtos/{id}                    | Atualiza produto |
| DELETE | /produtos/{id}                    | Remove (409 se tiver movimentações) |
| POST   | /movimentacoes/                   | Registra entrada/saída; valida produto (404) e saldo (409) |
| GET    | /movimentacoes/                   | Lista (filtros `produto_id`, `tipo`) |
| GET    | /movimentacoes/{id}               | Consulta movimentação |
| PATCH  | /movimentacoes/{id}               | Corrige apenas o motivo |

Códigos usados: 201, 204, 404, 409 e 422 (validação Pydantic).
