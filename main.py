"""
Script principal da Newsletter AgroQuímicos Brasil
Orquestra: scraping -> geração HTML -> envio de e-mail -> salvamento de log
"""

import os
import json
from datetime import datetime
from scraper import run_scraper
from newsletter import generate_newsletter_html, generate_plain_text_version
from send_email import send_newsletter_email


def save_log(news_data, html_content, log_dir='logs'):
    """
    Salva log da execução em arquivo JSON

    Args:
        news_data: Dados coletados pelo scraper
        html_content: HTML gerado
        log_dir: Diretório para salvar logs

    Returns:
        str: Caminho do arquivo de log
    """

    # Cria diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)

    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'newsletter_{timestamp}.json')

    # Prepara dados para o log
    log_data = {
        'timestamp': timestamp,
        'date': datetime.now().isoformat(),
        'total_news': sum(len(news) for news in news_data.values()),
        'segments': {
            segment: len(news)
            for segment, news in news_data.items()
            if news
        },
        'sources': list(set(
            noticia['fonte']
            for segment in news_data.values()
            for noticia in segment
        )),
        'html_size': len(html_content),
        'news_by_segment': {
            segment: [
                {
                    'titulo': n['titulo'],
                    'link': n['link'],
                    'fonte': n['fonte'],
                    'data': n['data'].isoformat() if hasattr(n['data'], 'isoformat') else str(n['data'])
                }
                for n in news[:10]  # Salva apenas as 10 primeiras de cada segmento
            ]
            for segment, news in news_data.items()
            if news
        }
    }

    # Salva arquivo
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"Log salvo em: {log_file}")

    return log_file


def main():
    """
    Função principal que executa todo o pipeline

    Pipeline:
    1. Coleta notícias (scraper)
    2. Gera HTML da newsletter
    3. Envia e-mail
    4. Salva log
    """

    print("=" * 60)
    print("NEWSLETTER AGROQUÍMICOS BRASIL")
    print(f"Execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    # Verifica variáveis de ambiente necessárias
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')

    if not all([sender_email, sender_password, recipient_email]):
        print("\n⚠ ERRO: Variáveis de ambiente não configuradas!")
        print("Configure as seguintes variáveis:")
        print("  - SENDER_EMAIL: seu e-mail Gmail")
        print("  - SENDER_PASSWORD: sua senha de app do Google")
        print("  - RECIPIENT_EMAIL: e-mail de destino")
        print("\nSe estiver rodando no GitHub Actions, configure os secrets:")
        print("  - SENDER_EMAIL")
        print("  - SENDER_PASSWORD")
        print("  - RECIPIENT_EMAIL")
        return False

    # Passo 1: Coleta notícias
    print("\n[1/4] Coletando notícias...")
    try:
        news_data = run_scraper()
        total_news = sum(len(news) for news in news_data.values())
        print(f"✓ {total_news} notícias coletadas em {len([k for k, v in news_data.items() if v])} segmentos")
    except Exception as e:
        print(f"✗ Erro no scraping: {e}")
        return False

    # Verifica se há notícias
    if total_news == 0:
        print("⚠ Nenhuma notícia coletada. Abortando.")
        return False

    # Passo 2: Gera HTML da newsletter
    print("\n[2/4] Gerando HTML da newsletter...")
    try:
        html_content = generate_newsletter_html(news_data)
        plain_text_content = generate_plain_text_version(news_data)
        print(f"✓ HTML gerado ({len(html_content)} caracteres)")
    except Exception as e:
        print(f"✗ Erro ao gerar HTML: {e}")
        return False

    # Passo 3: Envia e-mail
    print("\n[3/4] Enviando e-mail...")
    try:
        # Obtém configuração SMTP
        from send_email import get_smtp_config
        smtp_config = get_smtp_config()

        print(f"Usando servidor SMTP: {smtp_config['server']}")

        success = send_newsletter_email(
            html_content=html_content,
            plain_text_content=plain_text_content,
            recipient_email=recipient_email,
            sender_email=sender_email,
            sender_password=sender_password,
            smtp_server=smtp_config['server'],
            smtp_port=smtp_config['port']
        )

        if success:
            print("✓ E-mail enviado com sucesso!")
        else:
            print("✗ Falha ao enviar e-mail")
            # Continua para salvar o log mesmo se o e-mail falhar
    except Exception as e:
        print(f"✗ Erro ao enviar e-mail: {e}")
        # Continua para salvar o log mesmo se o e-mail falhar

    # Passo 4: Salva log
    print("\n[4/4] Salvando log...")
    try:
        log_file = save_log(news_data, html_content)
        print(f"✓ Log salvo em {log_file}")
    except Exception as e:
        print(f"✗ Erro ao salvar log: {e}")

    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DA EXECUÇÃO")
    print("=" * 60)
    print(f"Total de notícias: {total_news}")
    print(f"Segmentos cobertos: {len([k for k, v in news_data.items() if v])}")
    print(f"Fontes consultadas: {len(set(n['fonte'] for seg in news_data.values() for n in seg))}")

    print("\nNotícias por segmento:")
    for segment, news in news_data.items():
        if news:
            print(f"  • {segment.upper()}: {len(news)} notícias")

    print("=" * 60)
    print("✓ Execução concluída!")
    print("=" * 60)

    return True


if __name__ == '__main__':
    main()