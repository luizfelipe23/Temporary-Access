from datetime import datetime

from pydantic import BaseModel, Field


class CredentialCreate(BaseModel):
    """
    Dados necessários para gerar uma credencial.
    """

    expires_in_minutes: int = Field(
        default=10,
        ge=1,
        le=1440,
    )


class CredentialResponse(BaseModel):
    """
    Dados retornados ao cliente após a criação.
    """

    id: int
    token: str
    created_at: datetime
    expires_at: datetime
    revoked: bool

    class Config:
        from_attributes = True


class CredentialValidationRequest(BaseModel):
    """
    Chave que será apresentada para validação.
    """

    token: str = Field(
        min_length=1,
        max_length=255,
    )


class CredentialValidationResponse(BaseModel):
    """
    Resultado da validação da credencial.
    """

    valid: bool
    status: str
    expires_at: datetime | None = None
    created_at: datetime | None = None