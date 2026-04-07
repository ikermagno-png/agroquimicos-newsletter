"""
Módulo de envio de e-mail via SMTP
Suporta SMTP2GO, Gmail, Brevo e outros provedores SMTP
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os


def send_newsletter_email(
    html_content,
    plain_text_content,
    recipient_email,
    sender_email,
    sender_password,
    smtp_server='smtp.gmail.com',
    smtp_port=587
):
    """
    Envia a newsletter por e-mail

    Args:
        html_content: Conteúdo HTML da newsletter
        plain_text_content: Versão texto puro (fallback)
        recipient_email: E-mail do destinatário
        sender_email: E-mail do remetente
        sender_password: Senha de app ou chave SMTP
        smtp_server: Servidor SMTP
        smtp_port: Porta SMTP

    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """

    try:
        # Cria mensagem multipart
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Formata data no assunto
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        today = datetime.now()
        subject = f"AgroQuímicos Brasil - {today.day} de {meses[today.month - 1]} de {today.year}"

        msg['Subject'] = subject

        # Adiciona versão texto puro
        part1 = MIMEText(plain_text_content, 'plain', 'utf-8')

        # Adiciona versão HTML
        part2 = MIMEText(html_content, 'html', 'utf-8')

        # Anexa ambas as versões
        msg.attach(part1)
        msg.attach(part2)

        # Conecta ao servidor SMTP
        print(f"Conectando ao servidor {smtp_server}:{smtp_port}...")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Inicia TLS
            server.starttls()
            print("Conexão TLS iniciada.")

            # Autentica
            print(f"Autenticando como {sender_email}...")
            server.login(sender_email, sender_password)
            print("Autenticação bem-sucedida.")

            # Envia e-mail
            print(f"Enviando e-mail para {recipient_email}...")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("E-mail enviado com sucesso!")

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Erro de autenticação: {e}")
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
    Obtém configuração SMTP baseada no provedor

    Returns:
        dict: Configuração SMTP (server, port, requires_app_password)
    """

    # Provedores SMTP conhecidos
    smtp_providers = {
        'smtp2go': {
            'server': 'mail.smtp2go.com',
            'port': 587,
            'requires_app_password': False
        },
        'gmail': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'requires_app_password': True
        },
        'outlook': {
            'server': 'smtp-mail.outlook.com',
            'port': 587,
            'requires_app_password': True
        },
        'yahoo': {
            'server': 'smtp.mail.yahoo.com',
            'port': 587,
            'requires_app_password': True
        },
        'brevo': {
            'server': 'smtp-relay.brevo.com',
            'port': 587,
            'requires_app_password': False
        },
        'sendgrid': {
            'server': 'smtp.sendgrid.net',
            'port': 587,
            'requires_app_password': False,
            'username': 'apikey'
        },
        'mailgun': {
            'server': 'smtp.mailgun.org',
            'port': 587,
            'requires_app_password': False
        }
    }

    # Detecta provedor baseado no e-mail ou variável de ambiente
    sender_email = os.environ.get('SENDER_EMAIL', '')

    # Verifica se há configuração explícita
    provider = os.environ.get('SMTP_PROVIDER', '').lower()
    if provider in smtp_providers:
        return smtp_providers[provider]

    # Auto-detecção baseada no e-mail
    if 'gmail' in sender_email.lower():
        return smtp_providers['gmail']
    elif 'outlook' in sender_email.lower() or 'hotmail' in sender_email.lower():
        return smtp_providers['outlook']
    elif 'yahoo' in sender_email.lower():
        return smtp_providers['yahoo']

    # Padrão para SMTP2GO (melhor opção sem senha de app)
    return smtp_providers['smtp2go']


if __name__ == '__main__':
    # Teste de envio
    import os

    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('SENDER_PASSWORD')
    recipient = os.environ.get('RECIPIENT_EMAIL')

    if not all([sender, password, recipient]):
        print("Configure as variáveis de ambiente:")
        print("  SENDER_EMAIL=seu_email")
        print("  SENDER_PASSWORD=sua_senha_ou_chave")
        print("  RECIPIENT_EMAIL=email_destino")
        print("\nPara SMTP2GO (recomendado):")
        print("  SMTP_PROVIDER=smtp2go")
        print("  SENDER_EMAIL=seu_email_cadastrado")
        print("  SENDER_PASSWORD=sua_chave_api_smtp2go")
    else:
        config = get_smtp_config()
        print(f"Provedor detectado: {config['server']}")

        test_html = """
        <html>
            <body>
                <h1>Teste AgroQuímicos Brasil</h1>
                <p>Este é um e-mail de teste.</p>
            </body>
        </html>
        """

        test_text = "Teste AgroQuímicos Brasil\n\nEste é um e-mail de teste."

        success = send_newsletter_email(
            test_html,
            test_text,
            recipient,
            sender,
            password,
            config['server'],
            config['port']
        )

        if success:
            print("E-mail de teste enviado com sucesso!")
        else:
            print("Falha ao enviar e-mail de teste.")