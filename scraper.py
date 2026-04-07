"""
Scraper para coleta de notícias sobre agroquímicos no Brasil
Monitore sites brasileiros e portais do MAPA
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import time
import random
import re
from urllib.parse import urljoin, urlparse

# Headers para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}

# Configuração de sites para monitorar
SITES_CONFIG = {
    'agrolink': {
        'name': 'Agrolink',
        'base_url': 'https://www.agrolink.com.br',
        'rss': 'https://www.agrolink.com.br/rss/noticias',
        'type': 'rss',
        'segments': ['herbicidas', 'fungicidas', 'inseticidas', 'fertilizantes']
    },
    'cultivar': {
        'name': 'Grupo Cultivar',
        'base_url': 'https://www.grupocultivar.com.br',
        'rss': 'https://www.grupocultivar.com.br/rss',
        'type': 'rss',
        'segments': ['herbicidas', 'fungicidas', 'inseticidas', 'biodefensivos']
    },
    'agronegocio': {
        'name': 'Agronegócio',
        'base_url': 'https://www.agronegocio.com.br',
        'type': 'scrape',
        'search_paths': ['/noticias', '/agrotoxicos'],
        'segments': ['todos']
    },
    'agropage': {
        'name': 'Agropage',
        'base_url': 'https://www.agropage.com.br',
        'type': 'scrape',
        'search_paths': ['/noticias', '/produtos'],
        'segments': ['todos']
    },
    'bayer': {
        'name': 'Bayer Crop Science Brasil',
        'base_url': 'https://www.cropscience.bayer.br',
        'type': 'scrape',
        'search_paths': ['/noticias', '/produtos'],
        'segments': ['herbicidas', 'fungicidas', 'inseticidas']
    },
    'syngenta': {
        'name': 'Syngenta Brasil',
        'base_url': 'https://www.syngenta.com.br',
        'type': 'scrape',
        'search_paths': ['/noticias', '/produtos'],
        'segments': ['herbicidas', 'fungicidas', 'inseticidas', 'sementes']
    },
    'corteva': {
        'name': 'Corteva Agriscience',
        'base_url': 'https://www.corteva.com.br',
        'type': 'scrape',
        'search_paths': ['/noticias-e-eventos'],
        'segments': ['herbicidas', 'fungicidas', 'inseticidas']
    },
    'nortox': {
        'name': 'Nortox',
        'base_url': 'https://www.nortox.com.br',
        'type': 'scrape',
        'search_paths': ['/novidades'],
        'segments': ['herbicidas', 'fungicidas', 'inseticidas']
    },
    'upl': {
        'name': 'UPL Brasil',
        'base_url': 'https://www.upl.com/br/pt',
        'type': 'scrape',
        'search_paths': ['/media-center'],
        'segments': ['todos']
    }
}

# Palavras-chave para filtrar notícias relevantes
KEYWORDS = {
    'herbicidas': ['herbicida', 'herbicides', 'controle de plantas', 'plantas daninhas', 'glyphosate', 'glifosato', 'atrazine', 'atrazina', '2,4-D', 'paraquat', 'diuron'],
    'fungicidas': ['fungicida', 'fungicides', 'controle fungos', 'doenças fúngicas', 'tebuconazole', 'azoxystrobin', 'mancozebe', 'triazol', 'estrobilurina'],
    'inseticidas': ['inseticida', 'insecticide', 'controle de pragas', 'insetos', 'neonicotinoide', 'imidacloprid', 'clorpirifos', 'spinosad', 'diamida'],
    'acaricidas': ['acaricida', 'acaricide', 'ácaros', 'controle ácaros', 'abamectina', 'cipermectrina'],
    'nematicidas': ['nematicida', 'nematicide', 'nematoides', 'controle nematoides', 'fluensulfone', 'fluopyram'],
    'adjuvantes': ['adjuvante', 'surfactante', 'óleo mineral', 'óleo vegetal', 'espalhante', 'adesivo', 'emulsificante'],
    'biodefensivos': ['biodefensivo', 'biológico', 'bioinsumos', 'controle biológico', 'bacillus', 'trichoderma', 'beauveria', 'metarhizium', 'biodefesa'],
    'fertilizantes': ['fertilizante', 'adubo', 'nutrição', 'foliar', 'NPK', 'micronutrientes', 'macronutrientes', 'fertirrigação']
}

# Termos gerais de agroquímicos para filtrar qualquer notícia relevante
GENERAL_KEYWORDS = [
    'agroquímico', 'agrotoxico', 'agrotóxico', 'pesticida', 'pesticide',
    'registro mapa', 'novo produto', 'registro de produto', 'liberado',
    'defensivo agrícola', 'defensivos', 'produto fitossanitário',
    'molécula', 'ingrediente ativo', 'formulação', 'bula'
]


def random_delay():
    """Delay aleatório para evitar bloqueios"""
    time.sleep(random.uniform(1, 3))


def make_request(url, retries=3):
    """Faz requisição HTTP com retry"""
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                print(f"Erro ao acessar {url}: {e}")
                return None


def parse_rss_feed(site_key, config):
    """Extrai notícias de feeds RSS"""
    noticias = []

    if 'rss' not in config:
        return noticias

    try:
        feed = feedparser.parse(config['rss'])

        for entry in feed.entries[:20]:  # Limita a 20 notícias por feed
            # Obtém data de publicação
            pub_date = None
            if hasattr(entry, 'published_parsed'):
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed'):
                pub_date = datetime(*entry.updated_parsed[:6])

            # Obtém resumo/conteúdo
            summary = ''
            if hasattr(entry, 'summary'):
                summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:500]

            noticia = {
                'titulo': entry.title if hasattr(entry, 'title') else 'Sem título',
                'link': entry.link if hasattr(entry, 'link') else '',
                'resumo': summary,
                'data': pub_date or datetime.now(),
                'fonte': config['name'],
                'segmento': classify_segment(entry.title + ' ' + summary)
            }

            # Filtra apenas notícias relevantes
            if is_relevant(noticia['titulo'], noticia['resumo']):
                noticias.append(noticia)

        random_delay()
    except Exception as e:
        print(f"Erro ao processar RSS {config['name']}: {e}")

    return noticias


def scrape_site(site_key, config):
    """Extrai notícias por scraping de páginas"""
    noticias = []

    if config['type'] != 'scrape':
        return noticias

    base_url = config['base_url']

    for path in config.get('search_paths', ['/']):
        url = urljoin(base_url, path)
        response = make_request(url)

        if not response:
            continue

        try:
            soup = BeautifulSoup(response.content, 'lxml')

            # Tenta encontrar links de notícias/artigos
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'(news|article|post|noticia|item)', re.I))

            if not articles:
                # Fallback: procura por links com padrão de data ou notícia
                articles = soup.find_all('a', href=re.compile(r'(noticia|news|article|post|\d{4}/)', re.I))

            for article in articles[:15]:  # Limita a 15 por página
                try:
                    # Extrai título
                    title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'a', 'span', 'p'])
                    title = title_tag.get_text(strip=True) if title_tag else article.get_text(strip=True)[:200]

                    # Extrai link
                    link = article.find('a', href=True)
                    if link:
                        href = link['href']
                    elif article.name == 'a':
                        href = article['href']
                    else:
                        href = ''

                    if href and not href.startswith('http'):
                        href = urljoin(base_url, href)

                    # Extrai resumo
                    summary = article.get_text(strip=True)[:300]

                    if title and len(title) > 10:  # Filtra títulos muito curtos
                        noticia = {
                            'titulo': title[:200],
                            'link': href,
                            'resumo': summary,
                            'data': datetime.now(),
                            'fonte': config['name'],
                            'segmento': classify_segment(title + ' ' + summary)
                        }

                        if is_relevant(title, summary) and href:
                            noticias.append(noticia)
                except Exception as e:
                    continue

            random_delay()
        except Exception as e:
            print(f"Erro ao fazer scrape de {url}: {e}")

    return noticias


def classify_segment(text):
    """Classifica a notícia em um segmento"""
    text_lower = text.lower()

    for segment, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return segment

    return 'geral'


def is_relevant(title, summary):
    """Verifica se a notícia é relevante para agroquímicos"""
    text = (title + ' ' + summary).lower()

    # Verifica palavras-chave específicas de segmentos
    for keywords in KEYWORDS.values():
        for keyword in keywords:
            if keyword.lower() in text:
                return True

    # Verifica termos gerais de agroquímicos
    for keyword in GENERAL_KEYWORDS:
        if keyword.lower() in text:
            return True

    return False


def scrape_mapa_agrofit():
    """
    Scraper para o sistema Agrofit do MAPA
    Verifica novos registros de produtos
    """
    noticias = []

    try:
        # Página principal do Agrofit
        url = 'https://www.agrofit.agricultura.gov.br/consultar_agrofit'
        response = make_request(url)

        if response:
            soup = BeautifulSoup(response.content, 'lxml')

            # Procura por avisos ou notícias sobre novos registros
            alerts = soup.find_all(['div', 'span', 'p'], class_=re.compile(r'(alert|notice|aviso|news)', re.I))

            for alert in alerts[:10]:
                text = alert.get_text(strip=True)
                if 'registro' in text.lower() or 'novo' in text.lower() or 'liberado' in text.lower():
                    noticias.append({
                        'titulo': f"Registro MAPA: {text[:100]}",
                        'link': 'https://www.agrofit.agricultura.gov.br',
                        'resumo': text[:300],
                        'data': datetime.now(),
                        'fonte': 'MAPA Agrofit',
                        'segmento': 'registro_oficial'
                    })
    except Exception as e:
        print(f"Erro ao acessar Agrofit: {e}")

    # Tenta acessar página de notícias do MAPA
    try:
        mapa_news_url = 'https://www.gov.br/agricultura/pt-br/assuntos/noticias'
        response = make_request(mapa_news_url)

        if response:
            soup = BeautifulSoup(response.content, 'lxml')
            articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'(news|noticia|item)', re.I))

            for article in articles[:10]:
                title_tag = article.find(['h1', 'h2', 'h3', 'a'])
                if title_tag:
                    title = title_tag.get_text(strip=True)

                    link_tag = article.find('a', href=True)
                    link = link_tag['href'] if link_tag else ''

                    summary = article.get_text(strip=True)[:300]

                    # Filtra apenas notícias relacionadas a defensivos/agroquímicos
                    if is_relevant(title, summary):
                        noticias.append({
                            'titulo': title[:200],
                            'link': link,
                            'resumo': summary,
                            'data': datetime.now(),
                            'fonte': 'MAPA',
                            'segmento': classify_segment(title + ' ' + summary)
                        })
    except Exception as e:
        print(f"Erro ao acessar notícias MAPA: {e}")

    return noticias


def run_scraper():
    """Executa todos os scrapers e retorna notícias agregadas"""
    all_news = {
        'herbicidas': [],
        'fungicidas': [],
        'inseticidas': [],
        'acaricidas': [],
        'nematicidas': [],
        'adjuvantes': [],
        'biodefensivos': [],
        'fertilizantes': [],
        'registro_oficial': [],
        'geral': []
    }

    print("Iniciando coleta de notícias...")

    # Coleta de RSS feeds
    print("Coletando feeds RSS...")
    for site_key, config in SITES_CONFIG.items():
        if config['type'] == 'rss':
            print(f"  Processando {config['name']}...")
            noticias = parse_rss_feed(site_key, config)
            for noticia in noticias:
                segmento = noticia['segmento']
                if segmento in all_news:
                    all_news[segmento].append(noticia)
                else:
                    all_news['geral'].append(noticia)

    # Coleta por scraping
    print("Coletando por scraping...")
    for site_key, config in SITES_CONFIG.items():
        if config['type'] == 'scrape':
            print(f"  Processando {config['name']}...")
            noticias = scrape_site(site_key, config)
            for noticia in noticias:
                segmento = noticia['segmento']
                if segmento in all_news:
                    all_news[segmento].append(noticia)
                else:
                    all_news['geral'].append(noticia)

    # Coleta do MAPA/Agrofit
    print("Coletando dados do MAPA...")
    mapa_news = scrape_mapa_agrofit()
    for noticia in mapa_news:
        segmento = noticia['segmento']
        if segmento in all_news:
            all_news[segmento].append(noticia)
        else:
            all_news['geral'].append(noticia)

    # Remove duplicatas e ordena por data
    for segmento in all_news:
        seen_links = set()
        unique_news = []
        for noticia in all_news[segmento]:
            if noticia['link'] not in seen_links:
                seen_links.add(noticia['link'])
                unique_news.append(noticia)

        # Ordena por data (mais recentes primeiro)
        unique_news.sort(key=lambda x: x['data'], reverse=True)
        all_news[segmento] = unique_news[:20]  # Limita a 20 por segmento

    # Conta total de notícias
    total = sum(len(news) for news in all_news.values())
    print(f"Total de {total} notícias coletadas.")

    return all_news


if __name__ == '__main__':
    # Teste do scraper
    news = run_scraper()
    for segmento, noticias in news.items():
        if noticias:
            print(f"\n{segmento.upper()}: {len(noticias)} notícias")
            for n in noticias[:3]:
                print(f"  - {n['titulo'][:80]}...")