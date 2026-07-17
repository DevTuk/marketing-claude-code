#!/usr/bin/env python3
"""
Analizador de paginas de marketing — utilidad para las skills de Marketing Claude Code.

Analiza una URL y extrae senales relevantes de marketing: elementos SEO, estructura
de contenido, senales de confianza, CTAs, prueba social e indicadores de optimizacion
de conversion.
"""

import sys
import json
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin


class MarketingPageParser(HTMLParser):
    """Parsea el HTML y extrae elementos relevantes para analisis de marketing."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.meta_keywords = ""
        self.og_tags = {}
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}
        self.links = []
        self.images = []
        self.forms = []
        self.buttons = []
        self.scripts = []
        self.schema_data = []
        self.ctas = []
        self.social_links = []
        self.tracking_scripts = []

        # Estado interno del parser
        self._current_tag = None
        self._current_attrs = {}
        self._in_title = False
        self._in_heading = None
        self._in_button = False
        self._in_a = False
        self._current_text = ""
        self._in_script = False
        self._script_type = ""
        self._in_form = False
        self._current_form = {}
        self._form_fields = []
        self._text_content = []
        self._has_viewport = False
        self._canonical = ""
        self._robots_meta = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._current_tag = tag
        self._current_attrs = attrs_dict

        if tag == "title":
            self._in_title = True
            self._current_text = ""

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "keywords":
                self.meta_keywords = content
            elif name == "viewport":
                self._has_viewport = True
            elif name == "robots":
                self._robots_meta = content
            elif prop.startswith("og:"):
                self.og_tags[prop] = content

        elif tag == "link":
            rel = attrs_dict.get("rel", "")
            if "canonical" in rel:
                self._canonical = attrs_dict.get("href", "")

        elif tag in self.headings:
            self._in_heading = tag
            self._current_text = ""

        elif tag == "a":
            self._in_a = True
            self._current_text = ""
            href = attrs_dict.get("href", "")
            self.links.append({"href": href, "text": "", "attrs": attrs_dict})
            # Detectar enlaces a redes sociales
            social_platforms = ["twitter.com", "x.com", "facebook.com", "linkedin.com",
                                "instagram.com", "youtube.com", "tiktok.com", "github.com"]
            for platform in social_platforms:
                if platform in href:
                    self.social_links.append({"platform": platform.split(".")[0], "url": href})

        elif tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", ""),
                "has_alt": "alt" in attrs_dict,
                "loading": attrs_dict.get("loading", "")
            })

        elif tag == "button":
            self._in_button = True
            self._current_text = ""

        elif tag == "form":
            self._in_form = True
            self._current_form = {
                "action": attrs_dict.get("action", ""),
                "method": attrs_dict.get("method", "GET").upper()
            }
            self._form_fields = []

        elif tag == "input" and self._in_form:
            self._form_fields.append({
                "type": attrs_dict.get("type", "text"),
                "name": attrs_dict.get("name", ""),
                "placeholder": attrs_dict.get("placeholder", ""),
                "required": "required" in attrs_dict
            })

        elif tag == "script":
            self._in_script = True
            self._script_type = attrs_dict.get("type", "")
            self._current_text = ""
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
                # Deteccion de herramientas de tracking
                tracking_indicators = {
                    "gtag": "Google Analytics (gtag)",
                    "googletagmanager": "Google Tag Manager",
                    "google-analytics": "Google Analytics",
                    "analytics": "Analytics",
                    "fbevents": "Meta Pixel",
                    "facebook": "Meta/Facebook",
                    "snap.licdn": "LinkedIn Insight Tag",
                    "hotjar": "Hotjar",
                    "fullstory": "FullStory",
                    "mixpanel": "Mixpanel",
                    "amplitude": "Amplitude",
                    "segment": "Segment",
                    "hubspot": "HubSpot",
                    "intercom": "Intercom",
                    "crisp": "Crisp Chat",
                    "drift": "Drift",
                    "tiktok": "TikTok Pixel",
                    "clarity": "Microsoft Clarity"
                }
                src_lower = src.lower()
                for indicator, name in tracking_indicators.items():
                    if indicator in src_lower:
                        self.tracking_scripts.append(name)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = self._current_text.strip()

        elif tag in self.headings and self._in_heading == tag:
            text = self._current_text.strip()
            if text:
                self.headings[tag].append(text)
            self._in_heading = None

        elif tag == "a" and self._in_a:
            self._in_a = False
            text = self._current_text.strip()
            if self.links:
                self.links[-1]["text"] = text
            # Deteccion de CTAs (palabras en ES e EN para cubrir webs mixtas)
            cta_words = ["sign up", "get started", "try free", "start free", "buy now",
                         "subscribe", "join", "register", "download", "book", "schedule",
                         "request demo", "contact us", "learn more", "see pricing",
                         "start trial", "create account", "claim", "unlock",
                         "empezar", "empieza", "comienza", "regístrate", "registrate",
                         "suscríbete", "suscribete", "descargar", "reservar", "agendar",
                         "pedir demo", "contactar", "contacto", "saber más", "ver precios",
                         "prueba gratis", "crear cuenta", "únete", "unete", "solicita"]
            text_lower = text.lower()
            for cta in cta_words:
                if cta in text_lower:
                    self.ctas.append({"text": text, "href": self.links[-1]["href"], "type": "link"})
                    break

        elif tag == "button" and self._in_button:
            self._in_button = False
            text = self._current_text.strip()
            if text:
                self.buttons.append(text)
                self.ctas.append({"text": text, "type": "button"})

        elif tag == "form" and self._in_form:
            self._in_form = False
            self._current_form["fields"] = self._form_fields
            self._current_form["field_count"] = len(self._form_fields)
            self.forms.append(self._current_form)

        elif tag == "script" and self._in_script:
            self._in_script = False
            script_content = self._current_text
            # Tracking inline
            if "gtag" in script_content or "dataLayer" in script_content:
                if "Google Analytics" not in self.tracking_scripts and "Google Tag Manager" not in self.tracking_scripts:
                    self.tracking_scripts.append("Google Analytics/GTM (inline)")
            if "fbq" in script_content:
                if "Meta Pixel" not in self.tracking_scripts:
                    self.tracking_scripts.append("Meta Pixel (inline)")
            # Schema JSON-LD
            if self._script_type == "application/ld+json":
                try:
                    schema = json.loads(script_content)
                    if isinstance(schema, list):
                        self.schema_data.extend(schema)
                    else:
                        self.schema_data.append(schema)
                except (json.JSONDecodeError, ValueError):
                    pass

    def handle_data(self, data):
        if self._in_title or self._in_heading or self._in_a or self._in_button or self._in_script:
            self._current_text += data
        self._text_content.append(data)

    def get_full_text(self):
        return " ".join(self._text_content)

    def get_results(self):
        """Consolida los hallazgos en una estructura de resultados."""
        # Imagenes sin atributo alt
        images_without_alt = sum(1 for img in self.images if not img.get("has_alt") or not img.get("alt"))
        images_with_lazy = sum(1 for img in self.images if img.get("loading") == "lazy")

        # Jerarquia de encabezados
        heading_issues = []
        if not self.headings["h1"]:
            heading_issues.append("Falta etiqueta H1")
        elif len(self.headings["h1"]) > 1:
            heading_issues.append(f"Multiples H1 ({len(self.headings['h1'])})")
        if self.headings["h3"] and not self.headings["h2"]:
            heading_issues.append("H3 sin H2 previo (salto de nivel)")

        # Tracking unico
        tracking = list(set(self.tracking_scripts))

        # Conteo de palabras
        full_text = self.get_full_text()
        word_count = len(full_text.split())

        return {
            "seo": {
                "title": self.title,
                "title_length": len(self.title),
                "title_ok": 30 <= len(self.title) <= 60,
                "meta_description": self.meta_description,
                "meta_description_length": len(self.meta_description),
                "meta_description_ok": 120 <= len(self.meta_description) <= 160,
                "canonical": self._canonical,
                "robots_meta": self._robots_meta,
                "has_viewport": self._has_viewport,
                "og_tags": self.og_tags,
                "headings": {k: v for k, v in self.headings.items() if v},
                "heading_issues": heading_issues,
                "images_total": len(self.images),
                "images_without_alt": images_without_alt,
                "images_with_lazy_loading": images_with_lazy
            },
            "content": {
                "word_count": word_count,
                "headings_count": sum(len(v) for v in self.headings.values()),
                "h1": self.headings["h1"],
                "h2": self.headings["h2"]
            },
            "conversion": {
                "ctas": self.ctas[:20],
                "cta_count": len(self.ctas),
                "forms": self.forms,
                "form_count": len(self.forms),
                "buttons": self.buttons[:20]
            },
            "trust": {
                "social_links": self.social_links,
                "social_link_count": len(self.social_links)
            },
            "tracking": {
                "tools_detected": tracking,
                "tools_count": len(tracking),
                "schema_types": [s.get("@type", "Unknown") for s in self.schema_data],
                "schema_count": len(self.schema_data)
            },
            "technical": {
                "total_links": len(self.links),
                "internal_links": 0,  # se rellena tras analizar URL base
                "external_links": 0,
                "scripts_count": len(self.scripts)
            }
        }


def fetch_page(url):
    """Descarga una URL y devuelve el HTML como string."""
   ctx = ssl.create_default_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.5",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def fetch_robots_txt(url):
    """Intenta descargar y parsear robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    content = fetch_page(robots_url)
    if content:
        has_sitemap = "sitemap:" in content.lower()
        return {"exists": True, "has_sitemap_reference": has_sitemap, "content_preview": content[:500]}
    return {"exists": False}


def fetch_sitemap(url):
    """Comprueba si existe sitemap.xml y cuenta URLs."""
    parsed = urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "MarketingBot/1.0"})
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        content = response.read().decode("utf-8", errors="replace")
        url_count = content.lower().count("<url>") or content.lower().count("<loc>")
        return {"exists": True, "url_count": url_count}
    except Exception:
        return {"exists": False, "url_count": 0}


def analyze(url):
    """Ejecuta el analisis completo de marketing sobre una URL."""
    results = {"url": url, "status": "success"}

    html = fetch_page(url)
    if not html:
        return {"url": url, "status": "error", "message": "No se pudo descargar la pagina"}

    parser = MarketingPageParser()
    try:
        parser.feed(html)
    except Exception as e:
        return {"url": url, "status": "error", "message": f"Error al parsear: {str(e)}"}

    page_results = parser.get_results()

    # Enlaces internos vs externos
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    internal = 0
    external = 0
    for link in parser.links:
        href = link.get("href", "")
        if href.startswith("/") or domain in href:
            internal += 1
        elif href.startswith("http"):
            external += 1
    page_results["technical"]["internal_links"] = internal
    page_results["technical"]["external_links"] = external

    # robots.txt y sitemap
    page_results["robots"] = fetch_robots_txt(url)
    page_results["sitemap"] = fetch_sitemap(url)

    # Scoring parcial por area
    scores = {}

    # SEO
    seo_score = 10
    seo = page_results["seo"]
    if not seo["title"]:
        seo_score -= 3
    elif not seo["title_ok"]:
        seo_score -= 1
    if not seo["meta_description"]:
        seo_score -= 3
    elif not seo["meta_description_ok"]:
        seo_score -= 1
    if not seo["headings"].get("h1"):
        seo_score -= 2
    if seo["images_without_alt"] > 0:
        seo_score -= min(2, seo["images_without_alt"])
    if seo["heading_issues"]:
        seo_score -= 1
    if not seo["has_viewport"]:
        seo_score -= 1
    scores["seo"] = max(0, seo_score)

    # CTAs
    cta_score = 5
    conv = page_results["conversion"]
    if conv["cta_count"] == 0:
        cta_score = 1
    elif conv["cta_count"] >= 2:
        cta_score = 7
    if conv["cta_count"] >= 4:
        cta_score = 8
    value_ctas = [c for c in conv["ctas"] if len(c.get("text", "")) > 10]
    if value_ctas:
        cta_score = min(10, cta_score + 1)
    scores["cta"] = cta_score

    # Confianza
    trust_score = 5
    if page_results["trust"]["social_link_count"] >= 3:
        trust_score += 2
    elif page_results["trust"]["social_link_count"] >= 1:
        trust_score += 1
    if page_results["tracking"]["schema_count"] > 0:
        trust_score += 1
    scores["trust"] = min(10, trust_score)

    # Tracking
    track_score = 3
    if page_results["tracking"]["tools_count"] >= 3:
        track_score = 9
    elif page_results["tracking"]["tools_count"] >= 2:
        track_score = 7
    elif page_results["tracking"]["tools_count"] >= 1:
        track_score = 5
    scores["tracking"] = track_score

    page_results["scores"] = scores
    page_results["overall_score"] = round(sum(scores.values()) / len(scores), 1)

    results["analysis"] = page_results
    return results


def main():
    if len(sys.argv) < 2:
        # Modo demo
        print(json.dumps({
            "uso": "python3 analizar_pagina.py <url>",
            "ejemplo": "python3 analizar_pagina.py https://vystral.com",
            "descripcion": "Analiza una URL y devuelve un informe estructurado de marketing"
        }, indent=2, ensure_ascii=False))
        return

    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url

    results = analyze(url)
    print(json.dumps(results, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
