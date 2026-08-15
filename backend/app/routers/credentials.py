from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db
from app.models.credential import Credential
from app.models.user import User
from app.schemas.credential import (
    CredentialCreate,
    CredentialResponse,
    CredentialValidationRequest,
    CredentialValidationResponse,
)
from app.services.credential_service import (
    calculate_expiration,
    generate_credential_token,
    validate_credential,
)


# Todas as rotas deste arquivo começam com /api/credentials.
router = APIRouter(
    prefix="/api/credentials",
    tags=["Credentials"],
)


@router.post(
    "",
    response_model=CredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_credential(
    credential_data: CredentialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera uma nova credencial temporária para o usuário autenticado.
    """

    # Gera uma chave aleatória criptograficamente segura.
    token = generate_credential_token()

    # Calcula a data e hora em que a credencial irá expirar.
    expires_at = calculate_expiration(
        credential_data.expires_in_minutes
    )

    # Cria a credencial associando-a ao usuário autenticado.
    credential = Credential(
        token=token,
        created_by=current_user.id,
        expires_at=expires_at,
    )

    # Adiciona a credencial à sessão do banco.
    db.add(credential)

    # Persiste a nova credencial.
    db.commit()

    # Atualiza o objeto com os valores gerados pelo banco,
    # como o ID e created_at.
    db.refresh(credential)

    return credential


@router.get(
    "",
    response_model=list[CredentialResponse],
)
def list_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lista somente as credenciais criadas pelo usuário autenticado.
    """

    return (
        db.query(Credential)
        .filter(
            Credential.created_by == current_user.id,
        )
        .order_by(
            Credential.created_at.desc(),
        )
        .all()
    )


@router.post(
    "/validate",
    response_model=CredentialValidationResponse,
)
def validate_credential_route(
    validation_data: CredentialValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Valida uma credencial sem exigir autenticação.

    Essa rota é pública porque a pessoa que apresenta a chave
    não precisa estar autenticada no sistema.
    """

    # Procura a credencial utilizando o token informado.
    credential = (
        db.query(Credential)
        .filter(
            Credential.token == validation_data.token,
        )
        .first()
    )

    # Se a chave não existir no banco, não existe credencial válida.
    if credential is None:
        return CredentialValidationResponse(
            valid=False,
            status="not_found",
        )

    # Executa as regras de negócio:
    # - verifica se foi revogada;
    # - verifica se expirou;
    # - retorna o estado atual.
    is_valid, credential_status = validate_credential(
        credential,
    )

    return CredentialValidationResponse(
        valid=is_valid,
        status=credential_status,
        expires_at=credential.expires_at,
        created_at=credential.created_at,
    )


@router.get(
    "/{credential_id}",
    response_model=CredentialResponse,
)
def get_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna uma credencial específica do usuário autenticado.
    """

    credential = (
        db.query(Credential)
        .filter(
            Credential.id == credential_id,
            Credential.created_by == current_user.id,
        )
        .first()
    )

    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    return credential


@router.post(
    "/{credential_id}/revoke",
    response_model=CredentialResponse,
)
def revoke_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revoga uma credencial antes da sua expiração.
    """

    credential = (
        db.query(Credential)
        .filter(
            Credential.id == credential_id,
            Credential.created_by == current_user.id,
        )
        .first()
    )

    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )

    # Evita realizar a mesma operação duas vezes.
    if credential.revoked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential already revoked",
        )

    # Marca a credencial como inválida imediatamente.
    credential.revoked = True

    # Persiste a alteração.
    db.commit()

    # Atualiza o objeto antes de devolvê-lo.
    db.refresh(credential)

    return credential