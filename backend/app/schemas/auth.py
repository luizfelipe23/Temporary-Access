from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """
    Dados necessários para criar um novo usuário.
    """

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128,
    )


class UserResponse(BaseModel):
    """
    # Dados retornados ao consultar um usuário, a senha não é retornada por segurança. Isso permite que a senha não seja exposta em nenhuma resposta da API. (evitar hackers)
    """

    id: int
    name: str
    email: EmailStr
    active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """
    Credenciais necessárias para autenticar um usuário.
    """

    email: EmailStr

    password: str


class TokenResponse(BaseModel):
    """
    Resposta retornada após um login bem-sucedido.
    """

    access_token: str

    token_type: str = "bearer"