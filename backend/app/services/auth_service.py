from datetime import datetime, timedelta, timezone

import jwt

from app.models.user import User
from app.services.password_service import password_hasher

# Por enquanto usamos uma chave fixa apenas para desenvolvimento.
# mudar pra variável de ambiente depois, para não expor a chave no código.
JWT_SECRET = "development-secret-change-me"

# Algoritmo utilizado para assinar os tokens, teste
JWT_ALGORITHM = "HS256"

# Tempo de validade do access token.
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    return password_hasher.verify(password, password_hash)


def create_access_token(user: User) -> str:
    """
    Cria um JWT contendo a identidade básica do usuário.
    """

    now = datetime.now(timezone.utc)

    # Define quando o token deverá expirar, a base do código é o tempo atual + 30 minutos.
    expires_at = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expires_at,
        "iat": now,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )