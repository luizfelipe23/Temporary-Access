from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Credential(Base):

    __tablename__ = "credentials"

    # Identificador interno da credencial.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Chave usada posteriormente para validar o acesso.
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Usuário responsável pela criação da credencial, utilizar o mesmo modelo de usuário para criar a credencial, para que possamos rastrear quem criou a credencial.
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # Momento em que a credencial foi criada.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Momento em que a credencial perde a validade.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # Permite invalidar a credencial manualmente antes da expiração.
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )