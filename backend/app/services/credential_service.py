from datetime import datetime, timedelta, timezone
import secrets

from app.models.credential import Credential


def generate_credential_token() -> str: #baseado na biblioteca secrets do python, que é segura para gerar tokens aleatórios.
    return secrets.token_urlsafe(18)


def calculate_expiration(expires_in_minutes: int) -> datetime:
    """
    Calcula o momento de expiração da credencial em UTC.
    """

    now = datetime.now(timezone.utc)

    return now + timedelta(
        minutes=expires_in_minutes,
    )


def validate_credential(
    credential: Credential,
) -> tuple[bool, str]:
    """
    Verifica se uma credencial pode ser utilizada.

    Retorna:
    - True + "active" quando válida.
    - False + motivo quando inválida.
    """

    # Credencial revogada perde a validade imediatamente.
    if credential.revoked:
        return False, "revoked"

    expires_at = credential.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    # Verifica se a validade já terminou.
    if expires_at <= datetime.now(timezone.utc):
        return False, "expired"

    return True, "active"