"""Envio de e-mails transacionais da autenticacao."""

from dataclasses import dataclass
from html import escape
from urllib.parse import quote

import requests

from backend.config.settings import settings


RESEND_PROVIDER = "resend"


class EmailDeliveryError(RuntimeError):
    """Falha esperada ao tentar entregar um e-mail transacional."""


@dataclass(frozen=True)
class EmailDeliveryResult:
    """Resultado enxuto do envio de e-mail."""

    delivered: bool
    provider: str
    message_id: str | None = None


def is_password_reset_email_configured() -> bool:
    """Indica se ha configuracao minima para envio real de e-mail."""
    return all(
        (
            settings.resend_api_key,
            settings.email_from_address,
            settings.frontend_reset_password_url,
        )
    )


def build_password_reset_link(token: str) -> str:
    """Monta o link clicavel de redefinicao para o frontend."""
    base_url = settings.frontend_reset_password_url
    encoded_token = quote(token, safe="")

    if "#" in base_url:
        prefix, fragment = base_url.split("#", 1)
        separator = "&" if "?" in fragment else "?"
        return f"{prefix}#{fragment}{separator}token={encoded_token}"

    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}token={encoded_token}"


def _build_password_reset_email_html(*, recipient_email: str, reset_link: str) -> str:
    safe_email = escape(recipient_email)
    safe_link = escape(reset_link, quote=True)
    return f"""
    <div style="font-family: Arial, sans-serif; color: #1f1a16; line-height: 1.6;">
      <h1 style="margin-bottom: 16px;">Recuperacao de senha do Nexus IA</h1>
      <p>Recebemos um pedido para redefinir a senha da conta <strong>{safe_email}</strong>.</p>
      <p>Para continuar, clique no botao abaixo:</p>
      <p style="margin: 24px 0;">
        <a
          href="{safe_link}"
          style="background: #1f1a16; color: #ffffff; text-decoration: none; padding: 12px 18px; display: inline-block; border-radius: 999px;"
        >
          Redefinir senha
        </a>
      </p>
      <p>Se preferir, copie e cole este link no navegador:</p>
      <p><a href="{safe_link}">{safe_link}</a></p>
      <p>Se voce nao fez essa solicitacao, pode ignorar este e-mail.</p>
      <p>O link expira em 30 minutos.</p>
    </div>
    """.strip()


def _build_password_reset_email_text(*, reset_link: str) -> str:
    return "\n".join(
        [
            "Recuperacao de senha do Nexus IA",
            "",
            "Recebemos um pedido para redefinir sua senha.",
            "Use o link abaixo para continuar:",
            reset_link,
            "",
            "Se voce nao fez essa solicitacao, ignore este e-mail.",
            "O link expira em 30 minutos.",
        ]
    )


def send_password_reset_email(*, recipient_email: str, token: str) -> EmailDeliveryResult:
    """Envia o e-mail de redefinicao por meio do Resend."""
    if not is_password_reset_email_configured():
        raise EmailDeliveryError("Configuracao de e-mail transacional incompleta.")

    reset_link = build_password_reset_link(token)
    payload = {
        "from": f"{settings.email_from_name} <{settings.email_from_address}>",
        "to": [recipient_email],
        "subject": "Recuperacao de senha - Nexus IA",
        "html": _build_password_reset_email_html(
            recipient_email=recipient_email,
            reset_link=reset_link,
        ),
        "text": _build_password_reset_email_text(reset_link=reset_link),
    }

    if settings.email_reply_to:
        payload["reply_to"] = settings.email_reply_to

    try:
        response = requests.post(
            settings.resend_api_url,
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
                "User-Agent": "nexus-ai-portal/0.1",
            },
            json=payload,
            timeout=15,
        )
    except requests.RequestException as exc:
        raise EmailDeliveryError("Falha ao conectar ao provedor de e-mail.") from exc

    if response.status_code >= 400:
        raise EmailDeliveryError(
            f"Falha ao enviar e-mail pelo Resend. Status: {response.status_code}."
        )

    response_payload = response.json() if response.content else {}
    return EmailDeliveryResult(
        delivered=True,
        provider=RESEND_PROVIDER,
        message_id=response_payload.get("id"),
    )
