"""
Gerador de Newsletter em HTML
Cria e-mails bonitos e responsivos no tema agrícola
"""

from datetime import datetime
from jinja2 import Template
import html


def generate_newsletter_html(news_data, date=None):
    """
    Gera o HTML da newsletter com estilo profissional

    Args:
        news_data: Dicionário com notícias por segmento
        date: Data da newsletter (padrão: hoje)

    Returns:
        String com HTML completo da newsletter
    """

    if date is None:
        date = datetime.now()

    # Formata data em português
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    data_formatada = f"{date.day} de {meses[date.month - 1]} de {date.year}"

    # Conta total de notícias
    total_noticias = sum(len(news) for news in news_data.values())

    # Prepara dados para o template
    segmentos_info = {
        'herbicidas': {'icone': '🌿', 'cor': '#27ae60', 'titulo': 'Herbicidas'},
        'fungicidas': {'icone': '🍄', 'cor': '#9b59b6', 'titulo': 'Fungicidas'},
        'inseticidas': {'icone': '🐛', 'cor': '#e74c3c', 'titulo': 'Inseticidas'},
        'acaricidas': {'icone': '🕷️', 'cor': '#f39c12', 'titulo': 'Acaricidas'},
        'nematicidas': {'icone': '🔬', 'cor': '#1abc9c', 'titulo': 'Nematicidas'},
        'adjuvantes': {'icone': '💧', 'cor': '#3498db', 'titulo': 'Adjuvantes'},
        'biodefensivos': {'icone': '🌱', 'cor': '#2ecc71', 'titulo': 'Biodefensivos & Bioinsumos'},
        'fertilizantes': {'icone': '🌾', 'cor': '#f1c40f', 'titulo': 'Fertilizantes Foliares'},
        'registro_oficial': {'icone': '📋', 'cor': '#34495e', 'titulo': 'Registros Oficiais MAPA'},
        'geral': {'icone': '📰', 'cor': '#7f8c8d', 'titulo': 'Notícias Gerais'}
    }

    # Filtra apenas segmentos com notícias
    segmentos_com_news = [
        (key, info, news_data[key])
        for key, info in segmentos_info.items()
        if key in news_data and news_data[key]
    ]

    # Gera resumo executivo
    resumo = generate_executive_summary(news_data, segmentos_com_news)

    # Template HTML com Jinja2
    html_template = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgroQuímicos Brasil - Newsletter Diária</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            color: #2c3e50;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 50%, #1abc9c 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header .subtitle {
            font-size: 16px;
            opacity: 0.95;
            font-weight: 400;
        }

        .header .date {
            margin-top: 15px;
            font-size: 14px;
            background-color: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            display: inline-block;
        }

        /* Resumo Executivo */
        .executive-summary {
            background-color: #e8f5e9;
            border-left: 4px solid #27ae60;
            padding: 25px 30px;
            margin: 0;
        }

        .executive-summary h2 {
            color: #1b5e20;
            font-size: 18px;
            margin-bottom: 15px;
        }

        .executive-summary ul {
            margin-left: 20px;
        }

        .executive-summary li {
            margin-bottom: 8px;
            color: #2e7d32;
        }

        /* Stats */
        .stats {
            display: flex;
            justify-content: center;
            background-color: #f9fbe7;
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
        }

        .stat-item {
            text-align: center;
            margin: 0 30px;
        }

        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #27ae60;
        }

        .stat-label {
            font-size: 12px;
            color: #757575;
            text-transform: uppercase;
        }

        /* Seções */
        .section {
            padding: 25px 30px;
            border-bottom: 1px solid #eeeeee;
        }

        .section:last-child {
            border-bottom: none;
        }

        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid;
        }

        .section-icon {
            font-size: 28px;
            margin-right: 12px;
        }

        .section-title {
            font-size: 22px;
            font-weight: 600;
        }

        .section-count {
            margin-left: auto;
            background-color: #e0e0e0;
            color: #616161;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }

        /* Notícias */
        .news-item {
            padding: 15px 0;
            border-bottom: 1px solid #f5f5f5;
        }

        .news-item:last-child {
            border-bottom: none;
        }

        .news-title {
            font-size: 16px;
            font-weight: 600;
            color: #1565c0;
            text-decoration: none;
            display: block;
            margin-bottom: 8px;
        }

        .news-title:hover {
            color: #0d47a1;
            text-decoration: underline;
        }

        .news-summary {
            color: #546e7a;
            font-size: 14px;
            margin-bottom: 8px;
            line-height: 1.5;
        }

        .news-meta {
            font-size: 12px;
            color: #9e9e9e;
        }

        .news-source {
            background-color: #eceff1;
            padding: 2px 8px;
            border-radius: 4px;
            color: #455a64;
        }

        .news-date {
            margin-left: 10px;
        }

        /* Footer */
        .footer {
            background-color: #263238;
            color: #b0bec5;
            padding: 30px;
            text-align: center;
        }

        .footer h3 {
            color: white;
            font-size: 18px;
            margin-bottom: 10px;
        }

        .footer p {
            font-size: 13px;
            margin-bottom: 5px;
        }

        .footer .sources {
            margin-top: 20px;
            font-size: 11px;
        }

        .footer a {
            color: #4db6ac;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        /* Responsivo */
        @media only screen and (max-width: 600px) {
            .header h1 {
                font-size: 24px;
            }

            .stats {
                flex-direction: column;
            }

            .stat-item {
                margin: 10px 0;
            }

            .section {
                padding: 20px 15px;
            }

            .section-header {
                flex-wrap: wrap;
            }

            .section-count {
                margin-left: 0;
                margin-top: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🧪 AgroQuímicos Brasil</h1>
            <p class="subtitle">Sua newsletter diária sobre defensivos agrícolas e insumos</p>
            <div class="date">{{ data_formatada }}</div>
        </div>

        <!-- Estatísticas -->
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ total_noticias }}</div>
                <div class="stat-label">Notícias Coletadas</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ segmentos_com_news|length }}</div>
                <div class="stat-label">Segmentos Cobertos</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ fontes_count }}</div>
                <div class="stat-label">Fontes Monitoradas</div>
            </div>
        </div>

        <!-- Resumo Executivo -->
        <div class="executive-summary">
            <h2>📊 Resumo Executivo</h2>
            <ul>
                {{ resumo|safe }}
            </ul>
        </div>

        <!-- Seções por Segmento -->
        {% for key, info, noticias in segmentos_com_news %}
        <div class="section">
            <div class="section-header" style="border-color: {{ info.cor }};">
                <span class="section-icon">{{ info.icone }}</span>
                <span class="section-title" style="color: {{ info.cor }};">{{ info.titulo }}</span>
                <span class="section-count">{{ noticias|length }} notícias</span>
            </div>

            {% for noticia in noticias %}
            <div class="news-item">
                <a href="{{ noticia.link }}" class="news-title" target="_blank">
                    {{ noticia.titulo|e }}
                </a>
                <p class="news-summary">{{ noticia.resumo[:200] }}{% if noticia.resumo|length > 200 %}...{% endif %}</p>
                <div class="news-meta">
                    <span class="news-source">{{ noticia.fonte }}</span>
                    <span class="news-date">{{ noticia.data.strftime('%d/%m/%Y') }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}

        <!-- Footer -->
        <div class="footer">
            <h3>AgroQuímicos Brasil Newsletter</h3>
            <p>Monitoramento automatizado de notícias sobre agroquímicos</p>
            <p>Gerado automaticamente em {{ data_formatada }}</p>
            <div class="sources">
                <p><strong>Fontes:</strong> MAPA Agrofit, Agrolink, Grupo Cultivar, Agronegócio, Agropage, Bayer, Syngenta, Corteva, Nortox, UPL e outros.</p>
                <p style="margin-top: 15px;">
                    <a href="#">Cancelar inscrição</a> |
                    <a href="#">Preferências</a> |
                    <a href="#">Ver online</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    '''

    # Conta fontes únicas
    fontes = set()
    for noticias in news_data.values():
        for noticia in noticias:
            fontes.add(noticia['fonte'])

    # Renderiza template
    template = Template(html_template)
    html_content = template.render(
        data_formatada=data_formatada,
        total_noticias=total_noticias,
        segmentos_com_news=segmentos_com_news,
        fontes_count=len(fontes),
        resumo=resumo
    )

    return html_content


def generate_executive_summary(news_data, segmentos_com_news):
    """Gera resumo executivo em bullet points"""
    resumo_items = []
    total = sum(len(news_data.get(k, [])) for k in news_data)

    if total == 0:
        return (
            "<li><strong>Nenhuma notícia relevante encontrada</strong> nas fontes monitoradas nesta execução.</li>\n"
            "<li>O monitoramento segue ativo e uma nova coleta ocorrerá na próxima execução.</li>"
        )

    # Destaque para registros do MAPA
    if 'registro_oficial' in news_data and news_data['registro_oficial']:
        count = len(news_data['registro_oficial'])
        resumo_items.append(f"<li><strong>{count} atualizações</strong> de registros no MAPA Agrofit</li>")

    # Principais segmentos
    segment_counts = []
    for key, info, noticias in segmentos_com_news:
        if key != 'registro_oficial' and key != 'geral' and noticias:
            segment_counts.append(f"<li>{len(noticias)} notícias sobre <strong>{info['titulo'].lower()}</strong></li>")

    # Adiciona até 5 segmentos
    resumo_items.extend(segment_counts[:5])

    # Notícias gerais
    if 'geral' in news_data and news_data['geral']:
        resumo_items.append(f"<li>{len(news_data['geral'])} notícias gerais do setor</li>")

    # Total
    resumo_items.append(f"<li><strong>Total: {total} notícias</strong> de {len(set(n['fonte'] for segment in news_data.values() for n in segment))} fontes diferentes</li>")

    return '\n'.join(resumo_items)


def generate_plain_text_version(news_data, date=None):
    """
    Gera versão em texto puro da newsletter
    Útil para clientes de e-mail que não suportam HTML
    """
    if date is None:
        date = datetime.now()

    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    data_formatada = f"{date.day} de {meses[date.month - 1]} de {date.year}"

    text = f"""
═══════════════════════════════════════════════════════════════
    AGROQUÍMICOS BRASIL - NEWSLETTER DIÁRIA
    {data_formatada}
═══════════════════════════════════════════════════════════════

"""

    segmentos_nomes = {
        'herbicidas': 'HERBICIDAS',
        'fungicidas': 'FUNGICIDAS',
        'inseticidas': 'INSETICIDAS',
        'acaricidas': 'ACARICIDAS',
        'nematicidas': 'NEMATICIDAS',
        'adjuvantes': 'ADJUVANTES',
        'biodefensivos': 'BIODEFENSIVOS & BIOINSUMOS',
        'fertilizantes': 'FERTILIZANTES FOLIARES',
        'registro_oficial': 'REGISTROS OFICIAIS MAPA',
        'geral': 'NOTÍCIAS GERAIS'
    }

    for segmento, nome in segmentos_nomes.items():
        if segmento in news_data and news_data[segmento]:
            text += f"\n{'─' * 60}\n{nome}\n{'─' * 60}\n\n"

            for noticia in news_data[segmento][:5]:  # Limita a 5 por seção
                text += f"• {noticia['titulo']}\n"
                text += f"  {noticia['resumo'][:150]}...\n"
                text += f"  Fonte: {noticia['fonte']} | {noticia['data'].strftime('%d/%m/%Y')}\n"
                text += f"  Link: {noticia['link']}\n\n"

    text += f"""
═══════════════════════════════════════════════════════════════
Fontes: MAPA Agrofit, Agrolink, Grupo Cultivar, Agronegócio,
        Agropage, Bayer, Syngenta, Corteva, Nortox, UPL e outros.
═══════════════════════════════════════════════════════════════
"""

    return text


if __name__ == '__main__':
    # Teste com dados de exemplo
    test_data = {
        'herbicidas': [
            {
                'titulo': 'Nova formulação de glifosato é lançada no mercado',
                'link': 'https://exemplo.com/noticia1',
                'resumo': 'Empresa lança novo herbicida com tecnologia avançada...',
                'data': datetime.now(),
                'fonte': 'Agrolink',
                'segmento': 'herbicidas'
            }
        ],
        'fungicidas': [
            {
                'titulo': 'Alerta de resistência a fungicidas em soja',
                'link': 'https://exemplo.com/noticia2',
                'resumo': 'Pesquisadores alertam para aumento de resistência...',
                'data': datetime.now(),
                'fonte': 'Cultivar',
                'segmento': 'fungicidas'
            }
        ]
    }

    html = generate_newsletter_html(test_data)
    print("HTML gerado com sucesso!")
    print(f"Tamanho: {len(html)} caracteres")
