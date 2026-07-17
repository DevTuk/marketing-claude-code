<p align="center">
  <img src="banner.svg" alt="Marketing Claude Code" width="100%">
</p>

# Marketing Claude Code

Suite de marketing IA para Claude Code. 14 skills con agentes paralelos — audita webs, genera copy, secuencias de email, campañas de ads, calendarios de contenido, inteligencia competitiva e informes en PDF listos para cliente.

---

## Para quién es

- **Agencias de marketing** que quieren entregar auditorías, propuestas e informes profesionales sin tirarse una semana por cliente.
- **Solopreneurs y freelance** que venden servicios de marketing con IA y necesitan un sistema replicable.
- **Creadores y consultores** que analizan negocios de clientes, hacen diagnósticos y generan deliverables listos para cobrar.

Diseñado para mercado hispanohablante (España + LATAM). Los comandos, outputs y plantillas están en castellano. El análisis funciona en cualquier idioma.

---

## Qué hace

Escribes un comando en Claude Code y obtienes un análisis de marketing accionable al instante:

```
> /marketing auditoria https://cal.com

Lanzando 5 agentes en paralelo...

[OK] Contenido y Mensaje           -- Puntuacion: 74/100
[OK] Optimizacion de Conversion    -- Puntuacion: 61/100
[OK] SEO y Descubrimiento          -- Puntuacion: 82/100
[OK] Posicionamiento Competitivo   -- Puntuacion: 68/100
[OK] Marca y Confianza             -- Puntuacion: 79/100
[OK] Crecimiento y Estrategia      -- Puntuacion: 66/100

Puntuacion global: 71/100 (Solido, con palancas claras de mejora)

Top 3 prioridades:
  1. Reducir friccion en el formulario de signup (-3 campos)
  2. Anadir social proof above-the-fold (logos de clientes + numero de usuarios)
  3. Reescribir headline: enfocar en resultado, no en feature

Informe completo guardado en AUDITORIA-MARKETING.md
```

El sistema no te devuelve una puntuación y ya está. Te da prioridades ordenadas, copy reescrito, campañas listas para pegar y PDFs profesionales para entregar a cliente.

---

## Instalación

### Un solo comando



### Manual

```bash
git clone --depth 1 https://github.com/DevTuk/marketing-claude-code.git
cd marketing-claude-code
./install.sh
```

### Opcional: soporte para informes PDF

```bash
pip install reportlab
```

---

## Comandos

| Comando                             | Qué hace                                                         |
| ----------------------------------- | ---------------------------------------------------------------- |
| `/marketing auditoria <url>`        | Auditoría completa con 5 agentes paralelos y puntuación 0-100    |
| `/marketing rapido <url>`           | Snapshot de marketing en 60 segundos                             |
| `/marketing copy <url>`             | Copy optimizado con ejemplos antes/después                       |
| `/marketing emails <tema>`          | Secuencias de email completas (bienvenida, nurture, lanzamiento) |
| `/marketing redes <tema>`           | Calendario de contenido a 30 días                                |
| `/marketing ads <url>`              | Creatividades y copy para ads (Meta, Google, LinkedIn)           |
| `/marketing funnel <url>`           | Análisis y optimización de funnel de ventas                      |
| `/marketing competidores <url>`     | Informe de inteligencia competitiva                              |
| `/marketing landing <url>`          | Análisis CRO de landing page                                     |
| `/marketing lanzamiento <producto>` | Playbook de lanzamiento de producto                              |
| `/marketing propuesta <cliente>`    | Generador de propuesta comercial                                 |
| `/marketing informe <url>`          | Informe de marketing completo (Markdown)                         |
| `/marketing informe-pdf <url>`      | Informe de marketing profesional (PDF)                           |
| `/marketing seo <url>`              | Auditoría SEO de contenido                                       |
| `/marketing marca <url>`            | Análisis de voz de marca y guidelines                            |

---

## Arquitectura

```
marketing-claude-code/
├── README.md                              Este archivo
├── LICENSE                                MIT
├── .gitignore
├── banner.svg                             Banner del repo
├── install.sh                             Instalador
├── uninstall.sh                           Desinstalador
├── requirements.txt                       Deps de Python
├── CREDITS.md                             Inspiracion del ecosistema
│
├── marketing/SKILL.md                     Orquestador principal (enruta /marketing *)
│
├── skills/                                14 sub-skills
│   ├── marketing-auditoria/SKILL.md       Auditoria completa
│   ├── marketing-copy/SKILL.md            Copywriting
│   ├── marketing-emails/SKILL.md          Secuencias de email
│   ├── marketing-redes/SKILL.md           Calendario de redes
│   ├── marketing-ads/SKILL.md             Campanas de ads
│   ├── marketing-funnel/SKILL.md          Analisis de funnel
│   ├── marketing-competidores/SKILL.md    Inteligencia competitiva
│   ├── marketing-landing/SKILL.md         CRO de landing
│   ├── marketing-lanzamiento/SKILL.md     Playbook de lanzamiento
│   ├── marketing-propuesta/SKILL.md       Propuesta comercial
│   ├── marketing-informe/SKILL.md         Informe Markdown
│   ├── marketing-informe-pdf/SKILL.md     Informe PDF
│   ├── marketing-seo-contenido/SKILL.md   Auditoria SEO
│   └── marketing-marca/SKILL.md           Voz de marca
│
├── agents/                                5 subagentes paralelos
│   ├── marketing-contenido.md             Contenido y mensaje
│   ├── marketing-conversion.md            CRO y funnel
│   ├── marketing-competencia.md           Posicionamiento
│   ├── marketing-seo.md                   SEO tecnico
│   └── marketing-estrategia.md            Marca, precios, crecimiento
│
├── scripts/                               Scripts Python
│   ├── analizar_pagina.py
│   ├── escaner_competidores.py
│   ├── calendario_redes.py
│   └── generar_informe_pdf.py
│
└── templates/                             Plantillas
    ├── email-bienvenida.md
    ├── email-nurture.md
    ├── email-lanzamiento.md
    ├── plantilla-propuesta.md
    ├── calendario-contenido.md
    └── checklist-lanzamiento.md
```

---

## Metodología de scoring

La auditoría completa puntúa cualquier web en 6 dimensiones. Los pesos son deliberados:

| Categoría                   | Peso | Qué mide                                               |
| --------------------------- | ---- | ------------------------------------------------------ |
| Contenido y Mensaje         | 25%  | Calidad del copy, value props, headlines, CTAs         |
| Optimización de Conversión  | 25%  | Funnels, formularios, social proof, fricción, urgencia |
| SEO y Descubrimiento        | 15%  | SEO on-page, SEO técnico, estructura de contenido      |
| Posicionamiento Competitivo | 15%  | Diferenciación, alternativas, conciencia de mercado    |
| Marca y Confianza           | 10%  | Diseño, trust signals, autoridad                       |
| Crecimiento y Estrategia    | 10%  | Precios, canales de adquisición, retención             |

**Por qué conversión pesa más que SEO:** la mayoría de webs B2B en España y LATAM viven de tráfico de pago (Meta Ads, Google Ads) y outbound, no de SEO orgánico. Priorizar conversión sobre SEO refleja cómo realmente se mueve el dinero en estos negocios. Si mejoras 10 puntos de conversión, el impacto en revenue es inmediato. Si mejoras 10 puntos de SEO, tardas meses en verlo.

La **puntuación global** es el promedio ponderado de las 6 categorías (0-100).

---

## Cómo funciona

1. Escribes un comando — por ejemplo `/marketing auditoria https://ejemplo.com`.
2. Claude lee los archivos `SKILL.md` — le dicen exactamente cómo analizar la web.
3. Se lanzan 5 subagentes en paralelo — cada uno analiza una dimensión distinta.
4. Se ejecutan los scripts de Python — análisis automático de la página y escaneo de competidores.
5. Se compilan los resultados — en un informe puntuado, priorizado y accionable. Output en Markdown o PDF profesional.

---

## Casos de uso

### Agencias

- Ejecutar `/marketing auditoria` sobre la web de un prospecto antes de la llamada de venta.
- Generar `/marketing propuesta` con hallazgos específicos y precios.
- Entregar `/marketing informe-pdf` como deliverable profesional al cliente.

### Solopreneurs

- Usar `/marketing copy` para optimizar tus propias landings.
- Generar `/marketing emails` para tus lanzamientos.
- Montar `/marketing redes` para publicar con constancia sin pensar cada día qué subir.

### Creadores

- Estudiar competencia con `/marketing competidores`.
- Planificar lanzamientos con `/marketing lanzamiento`.
- Diagnosticar tu embudo con `/marketing funnel`.

---

## Desinstalar

```bash
./uninstall.sh
```

O manualmente:

```bash
rm -rf ~/.claude/skills/marketing*
rm -f ~/.claude/agents/marketing-*.md
```

---

## Créditos

Este repo se apoya en el ecosistema open-source de skills de [Claude Code](https://docs.anthropic.com/en/docs/claude-code). El formato de skills (carpeta con `SKILL.md` + orquestador + sub-skills + agentes paralelos) viene de patrones compartidos públicamente por la comunidad. Esta suite es una adaptación al mercado hispanohablante pensada para gente que vende servicios de marketing con IA. Detalle en [CREDITS.md](CREDITS.md).

---

## Licencia

MIT — ver [LICENSE](LICENSE).
