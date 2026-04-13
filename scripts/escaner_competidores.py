#!/usr/bin/env python3
"""
Escaner de competidores — utilidad para las skills de Marketing Claude Code.

Escanea webs de competidores y extrae posicionamiento, pricing, features y senales
de confianza para analisis competitivo.
"""

import sys
import json
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser
from urllib.parse import urlparse


class CompetitorPageParser(HTMLParser):
    """Parsea la pagina de un competidor para extraer datos de posicionamiento."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.og_title = ""
        self.og_description = ""
        self.h1_tags = []
        self.h2_tags = []
        self.pricing_indicators = []
        self.social_links = []
        self.trust_signals = []
        self.ctas = []
        self.testimonial_count = 0
        self.logo_count = 0

        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_a = False
        self._in_button = False
        self._current_text = ""
        self._all_text = []
        self._current_href = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "title":
            self._in_title = True
            self._current_text = ""
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
        elif tag == "h1":
            self._in_h1 = True
            self._current_text = ""
        elif tag == "h2":
            self._in_h2 = True
            self._current_text = ""
        elif tag == "a":
            self._in_a = True
            self._current_text = ""
            self._current_href = attrs_dict.get("href", "")
            # Redes sociales
            social_platforms = {"twitter.com": "Twitter/X", "x.com": "Twitter/X",
                                "facebook.com": "Facebook", "linkedin.com": "LinkedIn",
                                "instagram.com": "Instagram", "youtube.com": "YouTube",
                                "tiktok.com": "TikTok", "github.com": "GitHub"}
            href = attrs_dict.get("href", "")
            for domain, name in social_platforms.items():
                if domain in href:
                    self.social_links.append({"platform": name, "url": href})
        elif tag == "button":
            self._in_button = True
            self._current_text = ""
        elif tag == "img":
            alt = attrs_dict.get("alt", "").lower()
            src = attrs_dict.get("src", "").lower()
            # Contar logos de clientes
            if any(word in alt for word in ["logo", "client", "partner", "customer", "trusted", "cliente", "socio"]):
                self.logo_count += 1
            if any(word in src for word in ["logo", "client", "partner", "cliente"]):
                self.logo_count += 1

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = self._current_text.strip()
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            text = self._current_text.strip()
            if text:
                self.h1_tags.append(text)
        elif tag == "h2" and self._in_h2:
            self._in_h2 = False
            text = self._current_text.strip()
            if text:
                self.h2_tags.append(text)
        elif tag == "a" and self._in_a:
            self._in_a = False
            text = self._current_text.strip()
            cta_words = ["sign up", "get started", "try free", "start", "buy", "subscribe",
                         "join", "register", "download", "book", "demo", "contact", "pricing",
                         "empezar", "empieza", "comienza", "probar", "comprar", "suscribete",
                         "suscríbete", "unete", "únete", "descargar", "reservar", "agendar",
                         "contactar", "contacto", "precios", "precio"]
            if any(w in text.lower() for w in cta_words):
                self.ctas.append(text)
        elif tag == "button" and self._in_button:
            self._in_button = False
            text = self._current_text.strip()
            if text:
                self.ctas.append(text)

    def handle_data(self, data):
        if self._in_title or self._in_h1 or self._in_h2 or self._in_a or self._in_button:
            self._current_text += data
        self._all_text.append(data.strip())

        # Detectar patrones de pricing
        text_lower = data.lower().strip()
        pricing_patterns = [r"€\d+", r"\$\d+", r"£\d+", r"/mes", r"/año", r"/ano",
                            r"/month", r"/year", r"/mo", r"al mes", r"al año", r"al ano",
                            r"per month", r"per year", r"annually", r"plan gratis",
                            r"plan gratuito", r"prueba gratis", r"free plan",
                            r"free tier", r"free trial", r"enterprise"]
        for pattern in pricing_patterns:
            if re.search(pattern, text_lower):
                self.pricing_indicators.append(data.strip())
                break

        # Testimonios / casos
        testimonial_words = ["testimonial", "review", "said about", "what our customers",
                             "customer stories", "case study", "success story",
                             "testimonio", "resena", "reseña", "lo que dicen",
                             "caso de exito", "caso de éxito", "historia de cliente"]
        if any(w in text_lower for w in testimonial_words):
            self.testimonial_count += 1

    def get_results(self):
        full_text = " ".join(self._all_text)
        word_count = len(full_text.split())

        positioning = self.og_description or self.meta_description or ""
        if self.h1_tags:
            positioning = self.h1_tags[0]

        return {
            "positioning": {
                "headline": self.h1_tags[0] if self.h1_tags else self.title,
                "tagline": self.meta_description,
                "og_title": self.og_title,
                "og_description": self.og_description,
                "key_sections": self.h2_tags[:10]
            },
            "pricing": {
                "has_pricing_info": len(self.pricing_indicators) > 0,
                "pricing_mentions": list(set(self.pricing_indicators))[:10]
            },
            "trust": {
                "social_platforms": [s["platform"] for s in self.social_links],
                "social_link_count": len(self.social_links),
                "estimated_logo_count": self.logo_count,
                "has_testimonials": self.testimonial_count > 0
            },
            "ctas": list(set(self.ctas))[:10],
            "content": {
                "word_count": word_count,
                "sections": len(self.h2_tags)
            }
        }


def fetch_page(url):
    """Descarga una pagina web."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        return response.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def scan_competitor(url):
    """Escanea un competidor individual."""
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")

    result = {
        "url": url,
        "domain": domain,
        "status": "success"
    }

    html = fetch_page(url)
    if not html:
        result["status"] = "error"
        result["message"] = "No se pudo descargar la pagina"
        return result

    parser = CompetitorPageParser()
    try:
        parser.feed(html)
    except Exception:
        result["status"] = "error"
        result["message"] = "No se pudo parsear la pagina"
        return result

    result["data"] = parser.get_results()

    # Intentar acceder a la pagina de pricing
    pricing_urls = [
        f"https://{parsed.netloc}/precios",
        f"https://{parsed.netloc}/planes",
        f"https://{parsed.netloc}/pricing",
        f"https://{parsed.netloc}/plans",
        f"https://{parsed.netloc}/price",
    ]

    for pricing_url in pricing_urls:
        pricing_html = fetch_page(pricing_url)
        if pricing_html and len(pricing_html) > 1000:
            pricing_parser = CompetitorPageParser()
            try:
                pricing_parser.feed(pricing_html)
                pricing_data = pricing_parser.get_results()
                result["pricing_page"] = {
                    "url": pricing_url,
                    "found": True,
                    "pricing_mentions": pricing_data["pricing"]["pricing_mentions"],
                    "sections": pricing_data["positioning"]["key_sections"]
                }
            except Exception:
                pass
            break
    else:
        result["pricing_page"] = {"found": False}

    return result


def scan_multiple(urls):
    """Escanea varios competidores."""
    results = []
    for url in urls:
        result = scan_competitor(url)
        results.append(result)
    return results


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "uso": "python3 escaner_competidores.py <url1> [url2] [url3] ...",
            "ejemplo": "python3 escaner_competidores.py cal.com calendly.com doodle.com",
            "descripcion": "Escanea webs de competidores para extraer posicionamiento, pricing y senales de confianza"
        }, indent=2, ensure_ascii=False))
        return

    urls = sys.argv[1:]
    if len(urls) == 1:
        result = scan_competitor(urls[0])
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    else:
        results = scan_multiple(urls)
        print(json.dumps({"competitors": results}, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
