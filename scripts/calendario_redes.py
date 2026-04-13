#!/usr/bin/env python3
"""
Generador de calendario de redes sociales — utilidad para las skills de Marketing Claude Code.

Genera un calendario editorial de 30 dias con posts especificos por plataforma,
pilares de contenido y formulas de hook.
"""

import sys
import json
from datetime import datetime, timedelta


# Plantillas por pilar de contenido
CONTENT_PILLARS = {
    "educational": {
        "name": "Educativo",
        "description": "Ensena algo util que la audiencia pueda aplicar hoy",
        "formats": ["Hilo paso a paso", "Tip rapido", "Desmontar un mito", "Framework",
                    "Recomendacion de herramienta", "Analisis de sector", "Desglose de datos"],
        "platforms": {
            "linkedin": "Post largo con bullets. Comparte frameworks y datos concretos",
            "twitter": "Hilo de 5-10 tweets. Abre con tesis contraintuitiva o dato sorpresa",
            "instagram": "Carrusel de 5-10 slides, diseno limpio, una idea por slide",
            "tiktok": "Talking head o screen recording de 60-90s, hook en los 2 primeros segundos",
            "youtube": "Video de 8-15 min, titulo buscable, miniatura potente"
        }
    },
    "behind_the_scenes": {
        "name": "Behind the Scenes",
        "description": "Muestra el proceso real, sin filtros",
        "formats": ["Dia en mi vida", "Stack de herramientas", "Walkthrough de un proceso",
                    "Error y leccion aprendida", "Metricas reales del negocio", "Equipo o workspace"],
        "platforms": {
            "linkedin": "Historia personal, vulnerabilidad + leccion concreta",
            "twitter": "Tweet unico con foto o hilo corto, crudo y sin filtros",
            "instagram": "Stories o Reels, casual y autentico, grabacion directa",
            "tiktok": "Grabacion cruda, audio trending, sensacion real",
            "youtube": "Formato vlog de 5-10 min: dia en la vida o proceso por dentro"
        }
    },
    "social_proof": {
        "name": "Prueba Social",
        "description": "Resultados, testimonios y credibilidad demostrable",
        "formats": ["Caso de exito de cliente", "Testimonio", "Antes/despues",
                    "Hito de facturacion", "Contenido generado por usuarios", "Premio o reconocimiento"],
        "platforms": {
            "linkedin": "Caso de exito con numeros concretos. Etiqueta al cliente si procede",
            "twitter": "Screenshot del resultado + contexto breve. Celebra en publico",
            "instagram": "Grafica con testimonio o clip de video corto",
            "tiktok": "Reveal de transformacion antes/despues",
            "youtube": "Case study completo de 10-15 min"
        }
    },
    "engagement": {
        "name": "Engagement",
        "description": "Abre conversaciones, construye comunidad",
        "formats": ["Opinion fuerte", "Pregunta abierta", "Encuesta", "Esto o lo otro",
                    "Opinion impopular", "De acuerdo o no", "Rellena el hueco"],
        "platforms": {
            "linkedin": "Abre con afirmacion rotunda, pide opinion en comentarios",
            "twitter": "Tweet corto y punzante o encuesta. Responde a todos los comentarios",
            "instagram": "Encuestas y preguntas en stories, stickers interactivos",
            "tiktok": "Formato stitch o duet, responde comentarios en video",
            "youtube": "Community post con encuesta o video pidiendo opiniones"
        }
    },
    "promotional": {
        "name": "Promocional",
        "description": "Promocion directa del producto o servicio (con moderacion)",
        "formats": ["Demo de producto", "Feature destacada", "Oferta especial",
                    "Webinar o evento", "Recurso gratuito", "Invitacion a la comunidad"],
        "platforms": {
            "linkedin": "Enfoque valor primero. Abre con el problema que resuelves",
            "twitter": "Pitch breve con enlace, o hilo mostrando la herramienta en accion",
            "instagram": "Reel demo o carrusel con beneficios, enlace en bio",
            "tiktok": "Demo del producto con formato trending, venta suave",
            "youtube": "Tutorial usando tu producto, no un pitch comercial"
        }
    }
}

# Recomendaciones de frecuencia de publicacion
POSTING_FREQUENCY = {
    "linkedin": {"ideal": "3-5 posts/semana", "minimum": "2 posts/semana", "best_times": "Mar-Jue 8-10h, 12h"},
    "twitter": {"ideal": "3-5 tweets/dia", "minimum": "1 tweet/dia", "best_times": "9h, 12h, 17h"},
    "instagram": {"ideal": "4-7 posts/semana (feed+reels)", "minimum": "3 posts/semana", "best_times": "11-13h, 19-21h"},
    "tiktok": {"ideal": "1-3 videos/dia", "minimum": "3 videos/semana", "best_times": "7-9h, 12-15h, 19-23h"},
    "youtube": {"ideal": "2-3 videos/semana", "minimum": "1 video/semana", "best_times": "Jue-Sab 14-16h"},
    "facebook": {"ideal": "3-5 posts/semana", "minimum": "2 posts/semana", "best_times": "Mie 11h, Vie 10-11h"}
}

# Formulas de hook por plataforma
HOOK_FORMULAS = {
    "linkedin": [
        "He probado {X} y {resultado inesperado}. Esto es lo que aprendi:",
        "La mayoria piensa que {creencia}. Estan equivocados. Aqui el motivo:",
        "{Numero} cosas que me habria gustado saber antes de {accion}:",
        "He invertido {tiempo} analizando {tema}. Estos son los {numero} hallazgos:",
        "Deja de {error comun}. Haz esto en su lugar:",
        "El sector {X} esta cambiando. Esto es lo que nadie esta contando:"
    ],
    "twitter": [
        "{Tema} esta roto. Hilo con como arreglarlo:",
        "He estudiado {numero} {cosas}. Esto diferencia a los mejores del resto:",
        "Opinion impopular: {afirmacion fuerte}",
        "No necesitas {X}. Necesitas {Y}. Te explico:",
        "{Numero} {cosas} que te daran {beneficio} (hilo):",
        "El error mas grande en {tema}? {Error}. Te lo cuento:"
    ],
    "instagram": [
        "Guarda esto para despues",
        "POV: por fin consigues {resultado deseado}",
        "{Numero} cosas sobre {tema} que te van a volar la cabeza",
        "La chuleta de {tema} que no sabias que necesitabas",
        "Si te cuesta {problema}, prueba esto",
        "Converti {input} en {output impresionante}. Asi lo hice:"
    ],
    "tiktok": [
        "Espera al final... (reveal de transformacion)",
        "Cosas que tienen sentido en {nicho}",
        "POV: descubres {cosa util}",
        "No me creo que {cosa sorprendente} funcione de verdad",
        "Respondiendo a @user — asi hago {X}",
        "Dia {X} de {reto/serie}"
    ]
}


def generate_calendar(topic, platforms=None, days=30, brand_name=None):
    """Genera un calendario editorial de contenido."""
    if platforms is None:
        platforms = ["linkedin", "twitter", "instagram"]

    start_date = datetime.now()
    calendar = {
        "topic": topic,
        "brand": brand_name or topic,
        "platforms": platforms,
        "duration_days": days,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=days)).strftime("%Y-%m-%d"),
        "posting_schedule": {p: POSTING_FREQUENCY.get(p, {}) for p in platforms},
        "content_pillars": {
            k: {"name": v["name"], "description": v["description"], "frequency": ""}
            for k, v in CONTENT_PILLARS.items()
        },
        "pillar_distribution": {
            "educational": "40%",
            "behind_the_scenes": "15%",
            "social_proof": "15%",
            "engagement": "20%",
            "promotional": "10%"
        },
        "hook_formulas": {p: HOOK_FORMULAS.get(p, []) for p in platforms},
        "calendar": []
    }

    # Rotacion de pilares a lo largo del mes
    pillar_rotation = ["educational", "engagement", "educational", "behind_the_scenes",
                       "educational", "social_proof", "promotional",
                       "educational", "engagement", "educational"]

    for day in range(days):
        date = start_date + timedelta(days=day)
        day_of_week = date.strftime("%A")

        pillar_key = pillar_rotation[day % len(pillar_rotation)]
        pillar = CONTENT_PILLARS[pillar_key]

        format_idx = day % len(pillar["formats"])
        content_format = pillar["formats"][format_idx]

        day_entry = {
            "day": day + 1,
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": day_of_week,
            "pillar": pillar["name"],
            "format": content_format,
            "topic_angle": f"{content_format} sobre {topic}",
            "platforms": {}
        }

        for platform in platforms:
            if platform in pillar["platforms"]:
                day_entry["platforms"][platform] = {
                    "guidance": pillar["platforms"][platform],
                    "post": True
                }

        calendar["calendar"].append(day_entry)

    # Estrategia de repurposing
    calendar["repurposing_strategy"] = {
        "description": "Convierte 1 pieza larga en 10+ posts distribuidos por plataforma",
        "workflow": [
            f"1. Crea una pieza larga sobre {topic} (post de blog o video YouTube)",
            "2. Extrae 5-7 ideas clave como posts individuales",
            "3. Convierte cada idea al formato nativo de cada plataforma",
            "4. Arma un carrusel o hilo desde la pieza completa",
            "5. Graba un resumen de 60s en formato Reel/TikTok",
            "6. Saca quotes potentes para posts de imagen",
            "7. Crea una encuesta o pregunta a partir de una idea",
            "8. Comparte el behind-the-scenes de haber creado la pieza",
            "9. Reutiliza los posts que mejor rindieron 2-4 semanas despues",
            "10. Compila un 'best of' mensual"
        ]
    }

    return calendar


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "uso": "python3 calendario_redes.py <tema> [plataforma1,plataforma2,...] [dias]",
            "ejemplo": "python3 calendario_redes.py 'automatizaciones IA' linkedin,twitter,instagram 30",
            "descripcion": "Genera un calendario editorial de contenido para redes sociales",
            "plataformas_disponibles": list(POSTING_FREQUENCY.keys())
        }, indent=2, ensure_ascii=False))
        return

    topic = sys.argv[1]
    platforms = sys.argv[2].split(",") if len(sys.argv) > 2 else ["linkedin", "twitter", "instagram"]
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    calendar = generate_calendar(topic, platforms, days)
    print(json.dumps(calendar, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
