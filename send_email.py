"""
Modulo de envio de e-mail via SMTP.
Suporta SMTP2GO, Gmail, Brevo e outros provedores SMTP.
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_newsletter_email(
    html_content,
    plain_text_content,
    recipient_email,
    sender_email,
    sender_password,
    smtp_username=None,
    smtp_server="smtp.gmail.com",
    smtp_port=587,
):
    """
    Envia a newsletter por e-mail.

    Args:
        html_content: Conteudo HTML da newsletter
        plain_text_content: Versao texto puro (fallback)
        recipient_email: E-mail do destinatario
        sender_email: E-mail do remetente
        sender_password: Senha de app ou chave SMTP
        smtp_username: Usuario de autenticacao SMTP (opcional)
        smtp_server: Servidor SMTP
        smtp_port: Porta SMTP

    Returns:
        bool: True se enviado com sucesso, False caso contrario
    """

    try:
        smtp_username = smtp_username or sender_email

        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = recipient_email

        meses = [
            "Janeiro",
            "Fevereiro",
            "Marco",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
        ]
        today = datetime.now()
        subject = f"AgroQuimicos Brasil - {today.day} de {meses[today.month - 1]} de {today.year}"
        msg["Subject"] = subject

        part1 = MIMEText(plain_text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        print(f"Conectando ao servidor {smtp_server}:{smtp_port}...")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("Conexao TLS iniciada.")

            print(f"Autenticando como {smtp_username}...")
            server.login(smtp_username, sender_password)
            print("Autenticacao bem-sucedida.")

            print(f"Enviando e-mail para {recipient_email}...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("E-mail enviado com sucesso!")

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Erro de autenticacao: {e}")
        print("Verifique suas credenciais SMTP.")
        return False

    except smtplib.SMTPException as e:
        print(f"Erro SMTP: {e}")
        return False

    except Exception as e:
        print(f"Erro inesperado ao enviar e-mail: {e}")
        return False


def get_smtp_config():
    """
    Obtem configuracao SMTP baseada no provedor.

    Returns:
        dict: Configuracao SMTP (server, port, requires_app_password)
    """

    smtp_providers = {
        "smtp2go": {
            "server": "mail.smtp2go.com",
            "port": 587,
            "requires_app_password": False,
        },
        "gmail": {
            "server": "smtp.gmail.com",
            "port": 587,
            "requires_app_password": True,
        },
        "outlook": {
            "server": "smtp-mail.outlook.com",
            "port": 587,
            "requires_app_password": True,
        },
        "yahoo": {
            "server": "smtp.mail.yahoo.com",
            "port": 587,
            "requires_app_password": True,
        },
        "brevo": {
            "server": "smtp-relay.brevo.com",
            "port": 587,
            "requires_app_password": False,
        },
        "sendgrid": {
            "server": "smtp.sendgrid.net",
            "port": 587,
            "requires_app_password": False,
            "username": "apikey",
        },
        "mailgun": {
            "server": "smtp.mailgun.org",
            "port": 587,
            "requires_app_password": False,
        },
    }

    sender_email = os.environ.get("SENDER_EMAIL", "")
    provider = os.environ.get("SMTP_PROVIDER", "").lower()

    if provider in smtp_providers:
        return smtp_providers[provider]

    if "gmail" in sender_email.lower():
        return smtp_providers["gmail"]
    if "outlook" in sender_email.lower() or "hotmail" in sender_email.lower():
        return smtp_providers["outlook"]
    if "yahoo" in sender_email.lower():
        return smtp_providers["yahoo"]

    return smtp_providers["smtp2go"]


if __name__ == "__main__":
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    if not all([sender, password, recipient]):
        print("Configure as variaveis de ambiente:")
        print("  SMTP_USERNAME=seu_usuario_smtp (opcional)")
        print("  SENDER_EMAIL=seu_email")
        print("  SENDER_PASSWORD=sua_senha_ou_chave")
        print("  RECIPIENT_EMAIL=email_destino")
        print("\nPara SMTP2GO (recomendado):")
        print("  SMTP_PROVIDER=smtp2go")
        print("  SMTP_USERNAME=seu_usuario_smtp2go")
        print("  SENDER_EMAIL=seu_email_remetente")
        print("  SENDER_PASSWORD=sua_chave_api_smtp2go")
    else:
        config = get_smtp_config()
        smtp_username = os.environ.get("SMTP_USERNAME") or config.get("username")
        print(f"Provedor detectado: {config['server']}")

        test_html = """
        <html>
            <body>
                <h1>Teste AgroQuimicos Brasil</h1>
                <p>Este e um e-mail de teste.</p>
            </body>
        </html>
        """

        test_text = "Teste AgroQuimicos Brasil\n\nEste e um e-mail de teste."

        success = send_newsletter_email(
            test_html,
            test_text,
            recipient,
            sender,
            password,
            smtp_username,
            config["server"],
            config["port"],
        )

        if success:
            print("E-mail de teste enviado com sucesso!")
        else:
            print("Falha ao enviar e-mail de teste.")
