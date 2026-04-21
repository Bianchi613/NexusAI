"""Servico de autenticacao do portal."""

from dataclasses import dataclass

from fastapi import HTTPException, status

from backend.auth.email_service import (
    EmailDeliveryError,
    is_password_reset_email_configured,
    send_password_reset_email,
)
from backend.auth.auth_repository import AuthRepository
from backend.auth.auth_schema import (
    AuthStatusResponse,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterResponse,
    ResetPasswordResponse,
    TokenResponse,
)
from backend.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_SECRET_KEY,
    SECRET_KEY,
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES,
    create_password_reset_token,
    hash_password,
    verify_password_reset_token,
    verify_password,
    create_access_token,
)


_auth_repository = AuthRepository()


@dataclass(frozen=True)
class AuthRuntimeStatus:
    """Representa o estado operacional atual do modulo de auth."""

    response: AuthStatusResponse
    http_status: int


def build_auth_runtime_status() -> AuthRuntimeStatus:
    """Monta o status operacional da autenticacao para a API."""
    checks = {
        "jwt_secret_configured": bool(SECRET_KEY.strip()),
        "jwt_secret_not_default": SECRET_KEY != DEFAULT_SECRET_KEY,
        "jwt_secret_min_length": len(SECRET_KEY) >= 32,
        "access_token_expiration_valid": ACCESS_TOKEN_EXPIRE_MINUTES > 0,
    }
    ready = all(checks.values())

    if ready:
        note = "Auth pronto para operacao basica com bcrypt e JWT."
        status_value = "ready"
        http_status = status.HTTP_200_OK
    else:
        note = (
            "Auth funcional em desenvolvimento, mas degradado para operacao: "
            "configure JWT_SECRET_KEY forte e mantenha expiracao valida."
        )
        status_value = "degraded"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return AuthRuntimeStatus(
        response=AuthStatusResponse(
            status=status_value,
            ready=ready,
            provider="fastapi_custom",
            built_in_auth=False,
            checks=checks,
            note=note,
        ),
        http_status=http_status,
    )


def describe_auth_module() -> AuthStatusResponse:
    """Explica o estado atual do modulo de autenticacao."""
    return build_auth_runtime_status().response


def login(payload: LoginRequest) -> TokenResponse:
    """Autentica usuario e retorna JWT token."""
    normalized_email = payload.email.strip().lower()
    user = _auth_repository.get_active_user(normalized_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )
    
    # Verifica se a senha esta correta
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )
    
    # Gera token JWT
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


def register(email: str, name: str, password: str) -> RegisterResponse:
    """Registra um novo usuario no sistema."""
    normalized_email = email.strip().lower()
    normalized_name = name.strip()

    existing_user = _auth_repository.find_by_email(normalized_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{normalized_email}' ja cadastrado.",
        )
    
    password_hash = hash_password(password)
    user = _auth_repository.create(
        name=normalized_name,
        email=normalized_email,
        password_hash=password_hash,
        role="cliente",
    )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
    )


def request_password_reset(email: str) -> ForgotPasswordResponse:
    """Inicia o fluxo de redefinicao de senha."""
    normalized_email = email.strip().lower()
    user = _auth_repository.find_by_email(normalized_email)

    if user is None or not user.is_active:
        return ForgotPasswordResponse(
            message="Se o e-mail existir, o fluxo de redefinicao foi iniciado.",
        )

    reset_token = create_password_reset_token(user_id=user.id, email=user.email)

    if is_password_reset_email_configured():
        try:
            send_password_reset_email(recipient_email=user.email, token=reset_token)
        except EmailDeliveryError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Nao foi possivel enviar o e-mail de redefinicao agora.",
            ) from exc

        return ForgotPasswordResponse(
            message=(
                "Se o e-mail existir, enviamos um link de redefinicao de senha para a caixa de entrada."
            ),
        )

    return ForgotPasswordResponse(
        message=(
            "Solicitacao recebida. Neste ambiente, o token de redefinicao e retornado "
            "diretamente para concluir o fluxo no frontend."
        ),
        reset_token=reset_token,
        expires_in_minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES,
    )


def reset_password(*, token: str, new_password: str) -> ResetPasswordResponse:
    """Redefine a senha a partir de um token valido."""
    payload = verify_password_reset_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de redefinicao invalido ou expirado.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de redefinicao invalido.",
        )

    password_hash = hash_password(new_password)
    user = _auth_repository.update_password(int(user_id), password_hash)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario da redefinicao nao encontrado.",
        )

    return ResetPasswordResponse(message="Senha redefinida com sucesso.")
