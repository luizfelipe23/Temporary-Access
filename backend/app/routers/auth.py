from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse
from app.services.password_service import hash_password


# Todas as rotas deste arquivo começarão com /api/auth.
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Cria um novo usuário no sistema.
    """

    # Verifica se já existe um usuário utilizando esse email.
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Nunca salvamos a senha original.
    # Primeiro geramos o hash e só depois persistimos o usuário. # isso é importante para que a senha original nunca seja armazenada no banco de dados.
    password_hash = hash_password(user_data.password)

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
    )


    db.add(user)

    db.commit() # salva no banco de dados

    db.refresh(user) # id do banco

    return user