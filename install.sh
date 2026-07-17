#!/bin/bash
# Marketing Claude Code — Instalador de skills
# Instala skills, agentes y scripts en Claude Code

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   Marketing Claude Code — Suite de marketing   ${NC}"
echo -e "${CYAN}   14 skills . 5 agentes . 4 scripts . PDF      ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Detectar directorio del script
if [ -n "$BASH_SOURCE" ] && [ "$BASH_SOURCE" != "bash" ] && [ -f "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
else
    # Ejecucion remota via curl | bash -- clonamos el repo
    echo -e "${YELLOW}Instalacion remota detectada. Clonando repositorio...${NC}"
    TEMP_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/DevTuk/marketing-claude-code.git"$TEMP_DIR/marketing-claude-code" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Error al clonar el repositorio.${NC}"
        exit 1
    fi
    SCRIPT_DIR="$TEMP_DIR/marketing-claude-code"
fi

# Directorios destino
SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.claude/agents"

echo -e "${BLUE}Origen:${NC}  $SCRIPT_DIR"
echo -e "${BLUE}Destino:${NC} $SKILLS_DIR"
echo ""

# Verificar Claude Code
if command -v claude &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} Claude Code detectado"
else
    echo -e "${YELLOW}[!]${NC} Claude Code no encontrado en el PATH"
    if [ -t 0 ]; then
        read -p "  Continuar igualmente? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "Instalacion cancelada."
            exit 0
        fi
    else
        echo "  Continuando (modo no interactivo)..."
    fi
fi

# Crear directorios
echo -e "\n${BLUE}Creando directorios...${NC}"
mkdir -p "$SKILLS_DIR"
mkdir -p "$AGENTS_DIR"

# Instalar skill principal (orquestador)
echo -e "${BLUE}Instalando skill principal...${NC}"
mkdir -p "$SKILLS_DIR/marketing"
cp "$SCRIPT_DIR/marketing/SKILL.md" "$SKILLS_DIR/marketing/SKILL.md"
echo -e "  ${GREEN}[OK]${NC} marketing/SKILL.md (orquestador)"

# Instalar sub-skills
echo -e "\n${BLUE}Instalando sub-skills...${NC}"
SKILLS=(
    "marketing-auditoria"
    "marketing-copy"
    "marketing-emails"
    "marketing-redes"
    "marketing-ads"
    "marketing-funnel"
    "marketing-competidores"
    "marketing-landing"
    "marketing-lanzamiento"
    "marketing-propuesta"
    "marketing-informe"
    "marketing-informe-pdf"
    "marketing-seo-contenido"
    "marketing-marca"
)

SKILL_COUNT=0
for skill in "${SKILLS[@]}"; do
    if [ -f "$SCRIPT_DIR/skills/$skill/SKILL.md" ]; then
        mkdir -p "$SKILLS_DIR/$skill"
        cp "$SCRIPT_DIR/skills/$skill/SKILL.md" "$SKILLS_DIR/$skill/SKILL.md"
        echo -e "  ${GREEN}[OK]${NC} $skill"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    else
        echo -e "  ${YELLOW}[!]${NC} $skill (no encontrado, se omite)"
    fi
done

# Instalar agentes
echo -e "\n${BLUE}Instalando agentes...${NC}"
AGENTS=(
    "marketing-contenido"
    "marketing-conversion"
    "marketing-competencia"
    "marketing-seo"
    "marketing-estrategia"
)

AGENT_COUNT=0
for agent in "${AGENTS[@]}"; do
    if [ -f "$SCRIPT_DIR/agents/$agent.md" ]; then
        cp "$SCRIPT_DIR/agents/$agent.md" "$AGENTS_DIR/$agent.md"
        echo -e "  ${GREEN}[OK]${NC} $agent"
        AGENT_COUNT=$((AGENT_COUNT + 1))
    else
        echo -e "  ${YELLOW}[!]${NC} $agent (no encontrado, se omite)"
    fi
done

# Instalar scripts
echo -e "\n${BLUE}Instalando scripts...${NC}"
SCRIPTS_TARGET="$SKILLS_DIR/marketing/scripts"
mkdir -p "$SCRIPTS_TARGET"

SCRIPT_FILES=(
    "analizar_pagina.py"
    "escaner_competidores.py"
    "calendario_redes.py"
    "generar_informe_pdf.py"
)

SCRIPT_COUNT=0
for script in "${SCRIPT_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/scripts/$script" ]; then
        cp "$SCRIPT_DIR/scripts/$script" "$SCRIPTS_TARGET/$script"
        chmod +x "$SCRIPTS_TARGET/$script"
        echo -e "  ${GREEN}[OK]${NC} $script"
        SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
    else
        echo -e "  ${YELLOW}[!]${NC} $script (no encontrado, se omite)"
    fi
done

# Instalar plantillas
echo -e "\n${BLUE}Instalando plantillas...${NC}"
TEMPLATES_TARGET="$SKILLS_DIR/marketing/templates"
mkdir -p "$TEMPLATES_TARGET"

TEMPLATE_COUNT=0
if [ -d "$SCRIPT_DIR/templates" ]; then
    for template in "$SCRIPT_DIR/templates"/*.md; do
        if [ -f "$template" ]; then
            cp "$template" "$TEMPLATES_TARGET/$(basename "$template")"
            echo -e "  ${GREEN}[OK]${NC} $(basename "$template")"
            TEMPLATE_COUNT=$((TEMPLATE_COUNT + 1))
        fi
    done
fi

# Dependencias Python
echo -e "\n${BLUE}Comprobando dependencias de Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    echo -e "  ${GREEN}[OK]${NC} Python $PYTHON_VERSION detectado"

    if python3 -c "import reportlab" 2>/dev/null; then
        echo -e "  ${GREEN}[OK]${NC} reportlab instalado (informes PDF listos)"
    else
        echo -e "  ${YELLOW}[!]${NC} reportlab no instalado (necesario para informes PDF)"
        echo -e "    Instalar con: ${CYAN}pip install reportlab${NC}"
    fi

    if python3 -c "import requests" 2>/dev/null; then
        echo -e "  ${GREEN}[OK]${NC} requests instalado"
    fi
else
    echo -e "  ${YELLOW}[!]${NC} Python 3 no encontrado -- los scripts no funcionaran"
    echo -e "    Instalar Python: ${CYAN}https://python.org${NC}"
fi

# Limpieza si es instalacion remota
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Resumen
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}            Instalacion completada              ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "  Skills instaladas:     ${GREEN}$SKILL_COUNT${NC}"
echo -e "  Agentes instalados:    ${GREEN}$AGENT_COUNT${NC}"
echo -e "  Scripts instalados:    ${GREEN}$SCRIPT_COUNT${NC}"
echo -e "  Plantillas instaladas: ${GREEN}$TEMPLATE_COUNT${NC}"
echo ""
echo -e "${CYAN}Comandos disponibles:${NC}"
echo "  /marketing auditoria <url>       Auditoria de marketing completa (5 agentes en paralelo)"
echo "  /marketing rapido <url>          Snapshot de marketing en 60 segundos"
echo "  /marketing copy <url>            Copy optimizado con ejemplos antes/despues"
echo "  /marketing emails <tema>         Secuencias de email completas"
echo "  /marketing redes <tema>          Calendario de contenido para redes sociales"
echo "  /marketing ads <url>             Creatividades y copy para ads"
echo "  /marketing funnel <url>          Analisis y optimizacion de funnel"
echo "  /marketing competidores <url>    Inteligencia competitiva"
echo "  /marketing landing <url>         Analisis CRO de landing page"
echo "  /marketing lanzamiento <prod>    Playbook de lanzamiento"
echo "  /marketing propuesta <cliente>   Generador de propuesta comercial"
echo "  /marketing informe <url>         Informe de marketing (Markdown)"
echo "  /marketing informe-pdf <url>     Informe de marketing (PDF)"
echo "  /marketing seo <url>             Auditoria SEO de contenido"
echo "  /marketing marca <url>           Analisis de voz de marca"
echo ""
echo -e "  ${YELLOW}Inicia una nueva sesion de Claude Code para usar las skills.${NC}"
echo ""
