#!/usr/bin/env python3
"""
Generador de informe de marketing en PDF — Marketing Claude Code.

Genera informes PDF listos para cliente con graficas, visualizacion de scoring
y plan de accion priorizado.

Requiere: reportlab (pip install reportlab)
"""

import sys
import json
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                     TableStyle, PageBreak, Image)
    from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line, Wedge
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics import renderPDF
except ImportError:
    print("Error: se requiere reportlab. Instala con: pip install reportlab", file=sys.stderr)
    sys.exit(1)


# Paleta de colores
COLORS = {
    "primary": HexColor("#1B2A4A"),
    "accent": HexColor("#2D5BFF"),
    "highlight": HexColor("#FF6B35"),
    "success": HexColor("#00C853"),
    "warning": HexColor("#FFB300"),
    "danger": HexColor("#FF1744"),
    "light_bg": HexColor("#F5F7FA"),
    "text": HexColor("#2C3E50"),
    "text_light": HexColor("#7F8C9B"),
    "border": HexColor("#E0E6ED"),
    "white": white,
    "black": black,
}


def score_color(score):
    """Devuelve el color segun el valor del score."""
    if score >= 80:
        return COLORS["success"]
    elif score >= 60:
        return COLORS["accent"]
    elif score >= 40:
        return COLORS["warning"]
    else:
        return COLORS["danger"]


def draw_score_gauge(score, x, y, size=80):
    """Dibuja un indicador circular del score."""
    d = Drawing(size + 20, size + 30)

    # Circulo de fondo
    d.add(Circle(size / 2 + 10, size / 2 + 15, size / 2,
                 fillColor=COLORS["light_bg"], strokeColor=COLORS["border"], strokeWidth=2))

    # Relleno del score
    color = score_color(score)
    inner_r = size / 2 - 8
    d.add(Circle(size / 2 + 10, size / 2 + 15, inner_r,
                 fillColor=color, strokeColor=None))

    # Centro blanco
    d.add(Circle(size / 2 + 10, size / 2 + 15, inner_r - 10,
                 fillColor=COLORS["white"], strokeColor=None))

    # Numero
    d.add(String(size / 2 + 10, size / 2 + 10, str(int(score)),
                 fontSize=20, fillColor=COLORS["primary"],
                 textAnchor="middle", fontName="Helvetica-Bold"))

    return d


def create_bar_chart(categories, scores, width=450, height=180):
    """Crea una grafica de barras horizontal con los scores por categoria."""
    d = Drawing(width, height)

    bar_height = 20
    gap = 8
    max_bar_width = width - 180
    start_y = height - 30
    label_x = 5
    bar_x = 160

    for i, (cat, score) in enumerate(zip(categories, scores)):
        y = start_y - i * (bar_height + gap)

        # Etiqueta de categoria
        d.add(String(label_x, y + 5, cat[:22],
                     fontSize=9, fillColor=COLORS["text"],
                     textAnchor="start", fontName="Helvetica"))

        # Barra de fondo
        d.add(Rect(bar_x, y, max_bar_width, bar_height,
                   fillColor=COLORS["light_bg"], strokeColor=None))

        # Barra del score
        bar_width = (score / 100) * max_bar_width
        color = score_color(score)
        d.add(Rect(bar_x, y, bar_width, bar_height,
                   fillColor=color, strokeColor=None))

        # Valor numerico
        d.add(String(bar_x + max_bar_width + 10, y + 5, f"{int(score)}",
                     fontSize=10, fillColor=COLORS["text"],
                     textAnchor="start", fontName="Helvetica-Bold"))

    return d


def generate_report(data, output_path):
    """Genera un informe PDF profesional de marketing."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=COLORS["primary"],
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=COLORS["text_light"],
        spaceAfter=20,
        fontName="Helvetica"
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=COLORS["primary"],
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold"
    )

    subheading_style = ParagraphStyle(
        "CustomSubheading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=COLORS["accent"],
        spaceBefore=14,
        spaceAfter=8,
        fontName="Helvetica-Bold"
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLORS["text"],
        spaceAfter=6,
        fontName="Helvetica",
        leading=14
    )

    # Elementos del documento
    elements = []

    # === PORTADA ===
    elements.append(Spacer(1, 1.5 * inch))
    elements.append(Paragraph("Informe de Marketing", title_style))

    url = data.get("url", "ejemplo.com")
    date_str = data.get("date", datetime.now().strftime("%d/%m/%Y"))
    elements.append(Paragraph(f"{url}", subtitle_style))
    elements.append(Paragraph(f"Generado: {date_str}", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Gauge de score global
    overall_score = data.get("overall_score", 0)
    gauge = draw_score_gauge(overall_score, 0, 0, size=100)
    elements.append(gauge)
    elements.append(Spacer(1, 0.3 * inch))

    grade = "A+" if overall_score >= 90 else "A" if overall_score >= 80 else "B" if overall_score >= 70 else "C" if overall_score >= 60 else "D" if overall_score >= 50 else "F"
    elements.append(Paragraph(f"Score global de marketing: {int(overall_score)}/100 (Nota: {grade})", heading_style))

    exec_summary = data.get("executive_summary", "Este informe analiza la efectividad de marketing de la web en seis dimensiones: contenido y mensaje, optimizacion de conversion, SEO y descubrimiento, posicionamiento competitivo, marca y confianza, y crecimiento y estrategia.")
    elements.append(Paragraph(exec_summary, body_style))

    elements.append(PageBreak())

    # === DESGLOSE DE SCORES ===
    elements.append(Paragraph("Desglose por categoria", heading_style))

    categories = data.get("categories", {})
    cat_names = list(categories.keys()) if categories else [
        "Contenido y Mensaje", "Optimizacion de Conversion", "SEO y Descubrimiento",
        "Posicionamiento Competitivo", "Marca y Confianza", "Crecimiento y Estrategia"
    ]
    cat_scores = [categories.get(c, {}).get("score", 50) for c in cat_names] if categories else [65, 58, 72, 55, 68, 60]

    # Grafica
    chart = create_bar_chart(cat_names, cat_scores)
    elements.append(chart)
    elements.append(Spacer(1, 0.3 * inch))

    # Tabla de scores (pesos nuevos: Conversion 25%, SEO 15%)
    score_data = [["Categoria", "Score", "Peso", "Estado"]]
    weights = ["25%", "25%", "15%", "15%", "10%", "10%"]
    for i, (name, score) in enumerate(zip(cat_names, cat_scores)):
        status = "Solido" if score >= 75 else "Por mejorar" if score >= 50 else "Critico"
        weight = weights[i] if i < len(weights) else "—"
        score_data.append([name, f"{int(score)}/100", weight, status])

    score_table = Table(score_data, colWidths=[180, 70, 60, 90])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["white"], COLORS["light_bg"]]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(score_table)

    elements.append(PageBreak())

    # === HALLAZGOS CLAVE ===
    elements.append(Paragraph("Hallazgos clave", heading_style))

    findings = data.get("findings", [])
    if not findings:
        findings = [
            {"severity": "Critico", "finding": "El titular de la home no comunica claramente la propuesta de valor en menos de 5 segundos"},
            {"severity": "Alto", "finding": "No hay prueba social visible en la home: faltan testimonios, logos de clientes e insignias de confianza"},
            {"severity": "Alto", "finding": "El CTA principal usa texto generico en vez de copy orientado a valor"},
            {"severity": "Medio", "finding": "Faltan meta descriptions en las landings principales"},
            {"severity": "Medio", "finding": "No hay mecanismo de captura de email ni lead magnet visible"},
            {"severity": "Bajo", "finding": "El blog no enlaza internamente a las paginas de producto"},
        ]

    findings_data = [["Severidad", "Hallazgo"]]
    for f in findings:
        severity = f.get("severity", "Medio")
        finding = f.get("finding", "")
        findings_data.append([severity, Paragraph(finding, body_style)])

    findings_table = Table(findings_data, colWidths=[70, 400])
    severity_colors = {
        "Critico": COLORS["danger"],
        "Alto": COLORS["highlight"],
        "Medio": COLORS["warning"],
        "Bajo": COLORS["accent"],
        # Fallback para ingles
        "Critical": COLORS["danger"],
        "High": COLORS["highlight"],
        "Medium": COLORS["warning"],
        "Low": COLORS["accent"]
    }
    table_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]
    for i, f in enumerate(findings, 1):
        color = severity_colors.get(f.get("severity", "Medio"), COLORS["warning"])
        table_style_cmds.append(("TEXTCOLOR", (0, i), (0, i), color))
        table_style_cmds.append(("FONTNAME", (0, i), (0, i), "Helvetica-Bold"))

    findings_table.setStyle(TableStyle(table_style_cmds))
    elements.append(findings_table)

    elements.append(PageBreak())

    # === PLAN DE ACCION ===
    elements.append(Paragraph("Plan de accion priorizado", heading_style))

    # Quick Wins
    elements.append(Paragraph("Quick wins (esta semana)", subheading_style))
    quick_wins = data.get("quick_wins", [
        "Reescribir el titular de la home para que sea especifico y orientado a beneficio",
        "Anadir 3-5 logos de clientes o insignias de confianza above the fold",
        "Cambiar el CTA principal por copy orientado a valor (ej. 'Empezar gratis — sin tarjeta')",
        "Anadir meta descriptions a las 5 landings principales",
    ])
    for i, win in enumerate(quick_wins, 1):
        elements.append(Paragraph(f"{i}. {win}", body_style))

    elements.append(Spacer(1, 0.2 * inch))

    # Medio plazo
    elements.append(Paragraph("Medio plazo (1-3 meses)", subheading_style))
    medium_term = data.get("medium_term", [
        "Montar funnel de captura de email con lead magnet",
        "Crear paginas de comparacion para los 3 competidores principales",
        "Desarrollar 3 casos de exito con resultados medibles",
        "Implementar estrategia de contenido orientada a keywords de alta intencion",
    ])
    for i, action in enumerate(medium_term, 1):
        elements.append(Paragraph(f"{i}. {action}", body_style))

    elements.append(Spacer(1, 0.2 * inch))

    # Estrategico
    elements.append(Paragraph("Estrategico (3-6 meses)", subheading_style))
    strategic = data.get("strategic", [
        "Lanzar programa de referidos con incentivo estructurado",
        "Construir hub de contenido con piezas pilar",
        "Implementar retargeting full-funnel con mensajes por etapa",
        "Optimizar pricing segun metricas de valor",
    ])
    for i, action in enumerate(strategic, 1):
        elements.append(Paragraph(f"{i}. {action}", body_style))

    elements.append(PageBreak())

    # === COMPETIDORES ===
    if data.get("competitors"):
        elements.append(Paragraph("Panorama competitivo", heading_style))

        comp_data = [["", data.get("brand_name", "Target")] + [c.get("name", f"Competidor {i+1}") for i, c in enumerate(data["competitors"][:3])]]
        comp_rows = ["Posicionamiento", "Pricing", "Prueba social", "Contenido"]

        for row_name in comp_rows:
            row = [row_name, data.get("brand_name", "Target")]
            for comp in data["competitors"][:3]:
                key = row_name.lower().replace(" ", "_")
                row.append(comp.get(key, "—"))
            while len(row) < len(comp_data[0]):
                row.append("—")
            comp_data.append(row)

        col_count = len(comp_data[0])
        col_width = 470 / col_count
        comp_table = Table(comp_data, colWidths=[col_width] * col_count)
        comp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["white"], COLORS["light_bg"]]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ]))
        elements.append(comp_table)
        elements.append(PageBreak())

    # === METODOLOGIA ===
    elements.append(Paragraph("Metodologia", heading_style))
    elements.append(Paragraph(
        "Este informe evalua seis dimensiones de efectividad de marketing. "
        "Cada categoria se puntua de 0 a 100 segun buenas practicas del sector y benchmarks competitivos. "
        "Los pesos priorizan conversion sobre SEO: la mayoria de webs B2B en Espana viven de trafico de pago "
        "y outbound, no de SEO organico.",
        body_style
    ))

    method_data = [
        ["Categoria", "Peso", "Que medimos"],
        ["Contenido y Mensaje", "25%", "Calidad del copy, claridad de la propuesta de valor, efectividad de CTAs"],
        ["Optimizacion de Conversion", "25%", "Diseno del funnel, formularios, prueba social, reduccion de friccion"],
        ["SEO y Descubrimiento", "15%", "SEO on-page, SEO tecnico, estructura de contenido"],
        ["Posicionamiento Competitivo", "15%", "Diferenciacion, pricing, estrategia frente a alternativas"],
        ["Marca y Confianza", "10%", "Calidad de diseno, senales de confianza, indicadores de autoridad"],
        ["Crecimiento y Estrategia", "10%", "Estrategia de precios, canales de adquisicion, retencion"],
    ]

    method_table = Table(method_data, colWidths=[140, 50, 280])
    method_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["border"]),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLORS["white"], COLORS["light_bg"]]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(method_table)

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(
        "Generado por Marketing Claude Code",
        ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=COLORS["text_light"])
    ))

    # Construir PDF
    doc.build(elements)
    return output_path


def main():
    if len(sys.argv) < 2:
        # Modo demo — genera un informe de muestra
        sample_data = {
            "url": "https://ejemplo.com",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "overall_score": 62,
            "executive_summary": "Este analisis identifica varias oportunidades de alto impacto para mejorar la conversion y reforzar el posicionamiento competitivo. La web tiene base solida en contenido pero rinde por debajo en optimizacion de conversion y conciencia competitiva.",
            "categories": {
                "Contenido y Mensaje": {"score": 68, "weight": "25%"},
                "Optimizacion de Conversion": {"score": 52, "weight": "25%"},
                "SEO y Descubrimiento": {"score": 74, "weight": "15%"},
                "Posicionamiento Competitivo": {"score": 48, "weight": "15%"},
                "Marca y Confianza": {"score": 70, "weight": "10%"},
                "Crecimiento y Estrategia": {"score": 55, "weight": "10%"},
            },
            "findings": [
                {"severity": "Critico", "finding": "Titular de home generico: no comunica valor concreto a la audiencia objetivo"},
                {"severity": "Critico", "finding": "Sin prueba social visible above the fold"},
                {"severity": "Alto", "finding": "El boton principal dice 'Enviar' en vez de usar copy de valor"},
                {"severity": "Alto", "finding": "La pagina de precios no incluye comparativa ni aborda objeciones"},
                {"severity": "Medio", "finding": "Faltan paginas de comparativa con competidores: se pierde trafico de alta intencion"},
                {"severity": "Medio", "finding": "El blog no enlaza a las paginas de producto"},
                {"severity": "Bajo", "finding": "Enlaces a redes sociales en el footer pero sin integracion de prueba social"},
            ],
            "quick_wins": [
                "Reescribir titular: 'Ayudamos a empresas a crecer' -> 'Consigue 3x mas leads cualificados en 30 dias sin llamar en frio'",
                "Anadir 5 logos de clientes above the fold con texto 'Mas de 500 empresas confian en nosotros'",
                "Cambiar boton de formulario de 'Enviar' a 'Quiero mi auditoria gratis'",
                "Anadir seccion de testimonios con nombre, foto, empresa y resultado concreto",
            ],
            "medium_term": [
                "Montar landings tipo 'Alternativa a [Competidor]' para los 3 principales",
                "Producir 3 case studies en video con resultados medibles",
                "Implementar popup de exit-intent con lead magnet",
                "Lanzar secuencia de nurture para leads que no convierten al instante",
            ],
            "strategic": [
                "Construir hub de contenido con 10 paginas pilar orientadas a keywords de alto volumen",
                "Lanzar programa de referidos con incentivos para ambas partes",
                "Montar campanas de retargeting en Meta y Google con mensajes por etapa",
                "Crear una herramienta o assessment gratuito para captar leads en top of funnel",
            ],
            "competitors": [
                {"name": "Comp A", "posicionamiento": "Plataforma all-in-one", "pricing": "49-199 EUR/mes", "prueba_social": "10K+ usuarios", "contenido": "Blog activo"},
                {"name": "Comp B", "posicionamiento": "Enfoque enterprise", "pricing": "A medida", "prueba_social": "Logos Fortune 500", "contenido": "Whitepapers"},
                {"name": "Comp C", "posicionamiento": "Bajo coste", "pricing": "Gratis-29 EUR/mes", "prueba_social": "4.8 en G2", "contenido": "Canal YouTube"},
            ],
            "brand_name": "Acme Espana"
        }

        output = "INFORME-MARKETING-muestra.pdf"
        generate_report(sample_data, output)
        print(f"Informe de muestra generado: {output}")
        return

    # Modo input JSON
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "INFORME-MARKETING.pdf"

    with open(input_file, "r") as f:
        data = json.load(f)

    generate_report(data, output_file)
    print(f"Informe generado: {output_file}")


if __name__ == "__main__":
    main()
