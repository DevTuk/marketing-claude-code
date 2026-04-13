#!/bin/bash
# Marketing Claude Code -- Desinstalador
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}Desinstalando Marketing Claude Code...${NC}"
echo ""

SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.claude/agents"

# Eliminar skills
SKILLS=(
    "marketing"
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
for skill in "${SKILLS[@]}"; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        rm -rf "$SKILLS_DIR/$skill"
        echo -e "  ${GREEN}[OK]${NC} Skill eliminada: $skill"
    fi
done

# Eliminar agentes
AGENTS=(
    "marketing-contenido"
    "marketing-conversion"
    "marketing-competencia"
    "marketing-seo"
    "marketing-estrategia"
)
for agent in "${AGENTS[@]}"; do
    if [ -f "$AGENTS_DIR/$agent.md" ]; then
        rm "$AGENTS_DIR/$agent.md"
        echo -e "  ${GREEN}[OK]${NC} Agente eliminado: $agent"
    fi
done

echo ""
echo -e "${GREEN}Marketing Claude Code desinstalado.${NC}"
echo ""
