"""
Scraper resiliente para a newsletter AgroQuimicos Brasil.

Estrategia:
- prioriza RSS estavel em vez de scraping HTML fragil
- usa Google News RSS por segmento para ampliar cobertura
- mantem feeds diretos quando disponiveis
- enriquece resumos via Firecrawl de forma opcional
"""

from __future__ import annotations

import html
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List
from urllib.parse import quote_plus

import feedparser
import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30
LOOKBACK_DAYS = int(os.environ.get("SCRAPER_LOOKBACK_DAYS", "30"))
MAX_ITEMS_PER_FEED = int(os.environ.get("SCRAPER_MAX_ITEMS_PER_FEED", "20"))
MAX_ITEMS_PER_SEGMENT = int(os.environ.get("SCRAPER_MAX_ITEMS_PER_SEGMENT", "20"))
FIRECRAWL_MAX_ENRICH = int(os.environ.get("FIRECRAWL_MAX_ENRICH", "5"))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

SEGMENT_KEYWORDS = {
    "herbicidas": [
        "herbicida",
        "herbicidas",
        "glifosato",
        "glyphosate",
        "atrazina",
        "atrazine",
        "plantas daninhas",
        "daninhas",
    ],
    "fungicidas": [
        "fungicida",
        "fungicidas",
        "fungo",
        "fungos",
        "mancozebe",
        "azoxistrobina",
        "estrobilurina",
        "triazol",
    ],
    "inseticidas": [
        "inseticida",
        "inseticidas",
        "praga",
        "pragas",
        "imidacloprido",
        "neonicotinoide",
        "clorpirifos",
        "spinosad",
    ],
    "acaricidas": [
        "acaricida",
        "acaricidas",
        "acaro",
        "acaros",
        "abamectina",
    ],
    "nematicidas": [
        "nematicida",
        "nematicidas",
        "nematoide",
        "nematoides",
        "fluopyram",
        "fluensulfone",
    ],
    "adjuvantes": [
        "adjuvante",
        "adjuvantes",
        "surfactante",
        "oleo mineral",
        "oleo vegetal",
        "espalhante",
    ],
    "biodefensivos": [
        "biodefensivo",
        "biodefensivos",
        "bioinsumo",
        "bioinsumos",
        "biologico",
        "bacillus",
        "trichoderma",
        "beauveria",
        "metarhizium",
    ],
    "fertilizantes": [
        "fertilizante",
        "fertilizantes",
        "adubo",
        "adubos",
        "foliar",
        "micronutriente",
        "micronutrientes",
        "npk",
    ],
    "registro_oficial": [
        "registro",
        "registros",
        "mapa",
        "anvisa",
        "agrofit",
        "ministerio da agricultura",
    ],
}

GENERAL_KEYWORDS = [
    "agroquimico",
    "agroquimicos",
    "agrotoxico",
    "agrotoxicos",
    "agrotóxico",
    "agrotóxicos",
    "defensivo agricola",
    "defensivos agricolas",
    "defensivo agrícola",
    "defensivos agrícolas",
    "pesticida",
    "pesticidas",
    "bioinsumo",
    "bioinsumos",
]

SEGMENT_QUERIES = {
    "herbicidas": '"herbicida OR herbicidas OR glifosato" Brasil',
    "fungicidas": '"fungicida OR fungicidas OR ferrugem da soja" Brasil',
    "inseticidas": '"inseticida OR inseticidas OR controle de pragas" Brasil',
    "acaricidas": '"acaricida OR acaricidas" Brasil',
    "nematicidas": '"nematicida OR nematicidas OR nematoides" Brasil',
    "adjuvantes": '"adjuvante OR adjuvantes agricolas" Brasil',
    "biodefensivos": '"biodefensivos OR bioinsumos OR controle biologico" Brasil',
    "fertilizantes": '"fertilizantes foliares OR nutricao foliar" Brasil',
    "registro_oficial": '"MAPA OR Anvisa OR Agrofit" agrotóxicos Brasil',
    "geral": '"agrotoxicos OR agroquimicos OR defensivos agricolas" Brasil',
}

DIRECT_FEEDS = [
    {
        "name": "Agrolink",
        "url": "https://www.agrolink.com.br/rss/noticias",
        "segment": None,
    },
    {
        "name": "Grupo Cultivar",
        "url": "https://www.grupocultivar.com.br/rss",
        "segment": None,
    },
]


def normalize_text(text: str) -> str:
    cleaned = html.unescape(text or "")
    cleaned = BeautifulSoup(cleaned, "html.parser").get_text(" ", strip=True)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def normalize_key(text: str) -> str:
    text = normalize_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def build_google_news_rss_url(query: str) -> str:
    encoded = quote_plus(query)
    return (
        "https://news.google.com/rss/search?"
        f"q={encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    )


def parse_entry_date(entry) -> datetime:
    for attr in ("published", "updated"):
        value = getattr(entry, attr, None)
        if value:
            try:
                parsed = parsedate_to_datetime(value)
                if parsed.tzinfo is not None:
                    parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
                return parsed
            except (TypeError, ValueError):
                pass

    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            return datetime(*parsed[:6])

    return datetime.utcnow()


def is_recent(date_value: datetime) -> bool:
    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)
    return date_value >= cutoff


def extract_source_name(entry, default_name: str) -> str:
    source = getattr(entry, "source", None)
    if isinstance(source, dict) and source.get("title"):
        return normalize_text(source["title"])

    description = normalize_text(getattr(entry, "description", ""))
    parts = [part.strip() for part in description.split("  ")]
    if parts:
        possible_source = parts[-1]
        if len(possible_source) < 80:
            return possible_source

    return default_name


def classify_segment(text: str, preferred_segment: str | None = None) -> str:
    haystack = normalize_key(text)

    if preferred_segment and preferred_segment in SEGMENT_KEYWORDS:
        if any(keyword in haystack for keyword in map(normalize_key, SEGMENT_KEYWORDS[preferred_segment])):
            return preferred_segment

    for segment, keywords in SEGMENT_KEYWORDS.items():
        normalized_keywords = [normalize_key(keyword) for keyword in keywords]
        if any(keyword in haystack for keyword in normalized_keywords):
            return segment

    return preferred_segment or "geral"


def is_relevant(title: str, summary: str) -> bool:
    haystack = normalize_key(f"{title} {summary}")
    all_keywords = GENERAL_KEYWORDS + [
        keyword
        for keywords in SEGMENT_KEYWORDS.values()
        for keyword in keywords
    ]
    return any(normalize_key(keyword) in haystack for keyword in all_keywords)


def parse_feed(feed_url: str, source_name: str, preferred_segment: str | None = None) -> List[dict]:
    print(f"  Lendo feed: {source_name}")
    parsed = feedparser.parse(feed_url, request_headers=HEADERS)

    if getattr(parsed, "bozo", 0):
        print(f"  Aviso: feed com parsing imperfeito em {source_name}: {parsed.bozo_exception}")

    news_items = []

    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
        title = normalize_text(getattr(entry, "title", "Sem titulo"))
        summary = normalize_text(
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
        )
        link = getattr(entry, "link", "").strip()
        date_value = parse_entry_date(entry)

        if not link or not is_recent(date_value):
            continue

        if not is_relevant(title, summary):
            continue

        news_items.append(
            {
                "titulo": title[:220],
                "link": link,
                "resumo": summary[:600] or title,
                "data": date_value,
                "fonte": extract_source_name(entry, source_name),
                "segmento": classify_segment(f"{title} {summary}", preferred_segment),
            }
        )

    print(f"  -> {len(news_items)} noticias relevantes em {source_name}")
    return news_items


def collect_direct_feeds() -> List[dict]:
    collected: List[dict] = []
    print("Coletando feeds RSS diretos...")
    for feed in DIRECT_FEEDS:
        collected.extend(parse_feed(feed["url"], feed["name"], feed["segment"]))
    return collected


def collect_google_news_feeds() -> List[dict]:
    collected: List[dict] = []
    print("Coletando Google News RSS por segmento...")
    for segment, query in SEGMENT_QUERIES.items():
        feed_url = build_google_news_rss_url(query)
        source_name = f"Google News ({segment})"
        collected.extend(parse_feed(feed_url, source_name, segment))
    return collected


def enrich_with_firecrawl(news_items: List[dict]) -> None:
    api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not api_key:
        print("Firecrawl nao configurado; seguindo com resumos do RSS.")
        return

    print("Enriquecendo parte das noticias com Firecrawl...")
    enriched = 0

    for item in news_items:
        if enriched >= FIRECRAWL_MAX_ENRICH:
            break

        if "news.google.com" in item["link"]:
            continue

        try:
            response = requests.post(
                "https://api.firecrawl.dev/v2/scrape",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "url": item["link"],
                    "formats": ["markdown"],
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data", {})
            markdown = normalize_text(data.get("markdown", ""))

            if markdown:
                item["resumo"] = markdown[:600]
                metadata = data.get("metadata", {})
                if metadata.get("title"):
                    item["titulo"] = normalize_text(metadata["title"])[:220]
                enriched += 1
        except requests.RequestException as exc:
            print(f"  Firecrawl falhou para {item['link']}: {exc}")
        except ValueError as exc:
            print(f"  Firecrawl retornou JSON invalido para {item['link']}: {exc}")

    print(f"  -> {enriched} noticias enriquecidas com Firecrawl")


def deduplicate_and_bucket(news_items: List[dict]) -> Dict[str, List[dict]]:
    all_news = {
        "herbicidas": [],
        "fungicidas": [],
        "inseticidas": [],
        "acaricidas": [],
        "nematicidas": [],
        "adjuvantes": [],
        "biodefensivos": [],
        "fertilizantes": [],
        "registro_oficial": [],
        "geral": [],
    }

    seen = set()

    for item in sorted(news_items, key=lambda item: item["data"], reverse=True):
        unique_key = (
            normalize_key(item["titulo"]),
            item["link"].strip().lower(),
        )
        if unique_key in seen:
            continue

        seen.add(unique_key)
        segment = item["segmento"] if item["segmento"] in all_news else "geral"
        all_news[segment].append(item)

    for segment in all_news:
        all_news[segment] = all_news[segment][:MAX_ITEMS_PER_SEGMENT]

    return all_news


def run_scraper() -> Dict[str, List[dict]]:
    print("Iniciando coleta de noticias com fontes estaveis...")

    collected = []
    collected.extend(collect_direct_feeds())
    collected.extend(collect_google_news_feeds())

    enrich_with_firecrawl(collected)

    all_news = deduplicate_and_bucket(collected)
    total = sum(len(items) for items in all_news.values())
    print(f"Total de {total} noticias coletadas.")

    return all_news


if __name__ == "__main__":
    result = run_scraper()
    for segment, items in result.items():
        if items:
            print(f"{segment}: {len(items)}")
