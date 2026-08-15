from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.user import User  #chave para criar as tabelas do banco de dados , manter msm que não esteja sendo usado.
from app.models.credential import Credential  # chaves para criar as tabelas do banco de dados
from app.routers.auth import router as auth_router
from app.routers.credentials import router as credentials_router


# Cria as tabelas que ainda não existem.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Temporary Access API",
    version="0.1.0",
)


# Registra as rotas de autenticação.
app.include_router(auth_router)

# Registra as rotas de credenciais.
app.include_router(credentials_router)


@app.get("/health")
def health_check():
    """
    Endpoint utilizado para verificar se a API está funcionando.
    """
    return {
        "status": "ok",
        "service": "temporary-access-api",
    }