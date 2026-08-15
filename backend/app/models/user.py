from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class User(Base):
    """
    Representa um usuário que poderá acessar o sistema.
    """

    # ID , nome, email, senha, ativo e data de criação do usuário, para user basico

    __tablename__ = "users"

    # Identificador único do usuário.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Nome exibido na aplicação.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Email utilizado no login.
    # Unique impede dois usuários com o mesmo email.
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    # O hash da senha entra junto com a autenticação.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Permite desativar um usuário sem apagá-lo do banco.
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Data de criação do usuário.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )