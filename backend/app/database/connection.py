from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# O banco ficará dentro da pasta data, os dados vao ficar dentro do volume do container, para que não se percam ao reiniciar o container.
DATABASE_URL = "sqlite:///./data/temporary_access.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    """
    Abre uma sessão com o banco para uma requisição
    e garante que ela seja fechada ao terminar.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# Caso não termine a sessão, o banco de dados pode ficar bloqueado e não permitir novas conexões. !!!!!!!!!!!!!