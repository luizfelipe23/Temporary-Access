from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.user import User  # importa o modelo de usuário para que o SQLAlchemy possa criar a tabela no banco de dados.
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Temporary Access API",
    version="0.1.0",
)

app.include_router(auth_router)

@app.get("/health")
def health_check():
    """
    Endpoint utilizado para verificar se a API está funcionando.
    """
    return {
        "status": "ok",
        "service": "temporary-access-api",
    }