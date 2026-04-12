#!/usr/bin/env bash
# ============================================================================
# ClassLens ASD — Sandbox Bootstrap Script
# Run this FIRST when you copy the project to your sandbox server.
# Usage: chmod +x setup.sh && ./setup.sh
# ============================================================================

set -e  # Exit on any error

# --- Colors ----------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
info() { echo -e "  ${BLUE}→${NC} $1"; }
header() { echo -e "\n${BOLD}${CYAN}═══ $1 ═══${NC}"; }

ERRORS=0
WARNINGS=0

# ============================================================================
header "1/7  PYTHON ENVIRONMENT"
# ============================================================================

# Check Python version
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
        pass "Python $PY_VERSION (3.11+ required)"
    else
        warn "Python $PY_VERSION found — 3.11+ recommended, may still work"
        ((WARNINGS++))
    fi
else
    fail "Python 3 not found — install Python 3.11+"
    ((ERRORS++))
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv venv
    pass "Virtual environment created"
else
    pass "Virtual environment already exists"
fi

# Activate
source venv/bin/activate
pass "Virtual environment activated"

# ============================================================================
header "2/7  DEPENDENCIES"
# ============================================================================

info "Installing requirements..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Verify each critical package
for pkg in google.genai streamlit PIL plotly pydantic dotenv jinja2; do
    if python3 -c "import $pkg" 2>/dev/null; then
        pass "$pkg"
    else
        # Some packages have different import names
        case $pkg in
            google.genai) fail "google-genai — run: pip install google-genai" ; ((ERRORS++)) ;;
            PIL) fail "Pillow — run: pip install Pillow" ; ((ERRORS++)) ;;
            dotenv) fail "python-dotenv — run: pip install python-dotenv" ; ((ERRORS++)) ;;
            *) fail "$pkg" ; ((ERRORS++)) ;;
        esac
    fi
done

# Install dev/test dependencies
info "Installing dev dependencies..."
pip install pytest -q
pass "pytest installed"

# ============================================================================
header "3/7  API KEY"
# ============================================================================

if [ -f ".env" ]; then
    KEY=$(grep -oP 'GOOGLE_AI_STUDIO_KEY=\K.+' .env 2>/dev/null || echo "")
    if [ -z "$KEY" ] || [ "$KEY" = "your_api_key_here" ]; then
        fail ".env exists but GOOGLE_AI_STUDIO_KEY is not set"
        warn "Get your key at: https://aistudio.google.com/apikey"
        ((ERRORS++))
    else
        pass ".env found with API key (${KEY:0:8}...)"
        # Quick API test
        info "Testing Gemma 4 API connection..."
        API_TEST=$(python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
try:
    from google import genai
    client = genai.Client(api_key=os.getenv('GOOGLE_AI_STUDIO_KEY'))
    response = client.models.generate_content(
        model='gemma-4-27b-it',
        contents='Reply with exactly: CLASSLENS_OK'
    )
    if 'CLASSLENS_OK' in response.text:
        print('OK')
    else:
        print('PARTIAL')
except Exception as e:
    print(f'FAIL:{e}')
" 2>&1)
        if [ "$API_TEST" = "OK" ]; then
            pass "Gemma 4 API connection verified"
        elif [ "$API_TEST" = "PARTIAL" ]; then
            warn "API responded but unexpected content — check model access"
            ((WARNINGS++))
        else
            fail "API test failed: $API_TEST"
            warn "Check your key at https://aistudio.google.com/apikey"
            ((ERRORS++))
        fi
    fi
else
    info "No .env file found — creating from template..."
    cp .env.example .env
    fail ".env created but API key not set — edit .env with your key"
    warn "Get your key at: https://aistudio.google.com/apikey"
    ((ERRORS++))
fi

# ============================================================================
header "4/7  PROJECT STRUCTURE"
# ============================================================================

# Verify all expected directories exist
EXPECTED_DIRS=(
    "agents"
    "core"
    "schemas"
    "ui"
    "prompts"
    "data/students"
    "data/sample_work"
    "data/precomputed"
    "tests"
    "scripts"
    "docs"
    ".streamlit"
)

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        pass "$dir/"
    else
        info "Creating $dir/"
        mkdir -p "$dir"
        if [ ! -f "$dir/__init__.py" ] && [[ "$dir" != "data"* ]] && [[ "$dir" != "docs" ]] && [[ "$dir" != ".streamlit" ]] && [[ "$dir" != "scripts" ]]; then
            touch "$dir/__init__.py"
        fi
        warn "Created missing directory: $dir/"
        ((WARNINGS++))
    fi
done

# Verify critical files
CRITICAL_FILES=(
    "CLAUDE.md"
    "README.md"
    "requirements.txt"
    ".env.example"
    ".gitignore"
    ".streamlit/config.toml"
    "schemas/student_profile.py"
    "core/state_store.py"
    "prompts/templates.py"
    "data/students/maya_2026.json"
    "data/students/jaylen_2026.json"
    "data/students/sofia_2026.json"
    "tests/conftest.py"
    "tests/mock_api_responses.py"
    "tests/gold_standard_outputs.json"
    "tests/test_scenarios.md"
)

echo ""
info "Checking critical files..."
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        pass "$file"
    else
        fail "MISSING: $file"
        ((ERRORS++))
    fi
done

# ============================================================================
header "5/7  SCHEMA VALIDATION"
# ============================================================================

info "Validating Pydantic models + student data..."
SCHEMA_TEST=$(python3 -c "
import json, sys
try:
    from schemas.student_profile import StudentProfile, IEPGoal, TrialData, SensoryProfile
    print('MODELS_OK')
except Exception as e:
    print(f'MODELS_FAIL:{e}')
    sys.exit(1)

# Load and validate all 3 students
students = ['maya_2026', 'jaylen_2026', 'sofia_2026']
for s in students:
    try:
        with open(f'data/students/{s}.json') as f:
            data = json.load(f)
        print(f'DATA_OK:{s} ({len(data.get(\"iep_goals\", []))} goals)')
    except Exception as e:
        print(f'DATA_FAIL:{s}:{e}')
" 2>&1)

while IFS= read -r line; do
    case "$line" in
        MODELS_OK) pass "Pydantic models import successfully" ;;
        MODELS_FAIL*) fail "Pydantic models failed: ${line#MODELS_FAIL:}" ; ((ERRORS++)) ;;
        DATA_OK*) pass "Student data valid: ${line#DATA_OK:}" ;;
        DATA_FAIL*) fail "Student data invalid: ${line#DATA_FAIL:}" ; ((ERRORS++)) ;;
    esac
done <<< "$SCHEMA_TEST"

# Validate prompts load
info "Validating prompt templates..."
PROMPT_TEST=$(python3 -c "
from prompts.templates import (
    VISION_READER_SYSTEM, IEP_MAPPER_SYSTEM,
    PROGRESS_ANALYST_SYSTEM, MATERIAL_FORGE_SYSTEM
)
systems = [VISION_READER_SYSTEM, IEP_MAPPER_SYSTEM, PROGRESS_ANALYST_SYSTEM, MATERIAL_FORGE_SYSTEM]
total_chars = sum(len(s) for s in systems)
print(f'OK:{total_chars}')
" 2>&1)

if [[ "$PROMPT_TEST" == OK:* ]]; then
    CHARS="${PROMPT_TEST#OK:}"
    pass "All 4 system prompts loaded (${CHARS} chars total)"
else
    fail "Prompt templates failed to load: $PROMPT_TEST"
    ((ERRORS++))
fi

# ============================================================================
header "6/7  GIT SETUP"
# ============================================================================

if [ -d ".git" ]; then
    pass "Git repo already initialized"
else
    info "Initializing git repo..."
    git init -q
    pass "Git repo initialized"
fi

# Check .gitignore protects secrets
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        pass ".gitignore protects .env"
    else
        warn ".gitignore exists but doesn't exclude .env — adding it"
        echo ".env" >> .gitignore
        ((WARNINGS++))
    fi
else
    warn "No .gitignore — creating one"
    echo -e ".env\n__pycache__/\nvenv/\n*.pyc" > .gitignore
    ((WARNINGS++))
fi

# ============================================================================
header "7/7  SAMPLE WORK IMAGES"
# ============================================================================

PNG_COUNT=$(find data/sample_work -name "*.png" 2>/dev/null | wc -l)
if [ "$PNG_COUNT" -ge 7 ]; then
    pass "$PNG_COUNT sample work images found"
else
    info "Generating sample work images..."
    python3 scripts/generate_sample_work.py 2>/dev/null
    NEW_COUNT=$(find data/sample_work -name "*.png" 2>/dev/null | wc -l)
    if [ "$NEW_COUNT" -ge 7 ]; then
        pass "Generated $NEW_COUNT sample work images"
    else
        warn "Only $NEW_COUNT images generated — check scripts/generate_sample_work.py"
        ((WARNINGS++))
    fi
fi

# ============================================================================
header "RESULTS"
# ============================================================================

echo ""
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  ✅ ALL CHECKS PASSED — Ready to build!${NC}"
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}  ⚠  $WARNINGS warning(s), 0 errors — Mostly ready${NC}"
else
    echo -e "${RED}${BOLD}  ❌ $ERRORS error(s), $WARNINGS warning(s) — Fix errors before building${NC}"
fi

# ============================================================================
header "BUILD ORDER (from IMPLEMENTATION-PLAN.md)"
# ============================================================================

echo -e "
${BOLD}Phase 1: Foundation (Days 1-3)${NC}
  ${CYAN}Day 1${NC}  core/gemma_client.py    — API wrapper (generate, multimodal, tools, thinking)
  ${CYAN}Day 2${NC}  schemas/tools.py        — 8 function calling JSON schemas
  ${CYAN}Day 3${NC}  core/pipeline.py        — Orchestrator skeleton

${BOLD}Phase 2: Agents (Days 4-10)${NC}
  ${CYAN}Day 4-5${NC}   agents/vision_reader.py   — Multimodal OCR agent
  ${CYAN}Day 6-7${NC}   agents/iep_mapper.py      — Goal mapping agent
  ${CYAN}Day 8${NC}     agents/progress_analyst.py — Trend detection agent
  ${CYAN}Day 9-10${NC}  agents/material_forge.py   — 7 output types

${BOLD}Phase 3: Demo App (Days 11-18)${NC}
  ${CYAN}Day 11-13${NC}  app.py + ui/ pages     — Streamlit app (see docs/wireframe.html)
  ${CYAN}Day 14-15${NC}  Pre-baked demo mode    — Precompute all demo results
  ${CYAN}Day 16-18${NC}  Polish + edge cases    — Error handling, loading states

${BOLD}Phase 4: Deploy + Submit (Days 19-22)${NC}
  ${CYAN}Day 19${NC}  Streamlit Cloud deploy
  ${CYAN}Day 20${NC}  Video recording (see docs/VIDEO-SCRIPT.md)
  ${CYAN}Day 21${NC}  Kaggle writeup (see docs/COMPETITION-WRITEUP.md)
  ${CYAN}Day 22${NC}  Final submission

${BOLD}Your first command after this script:${NC}
  ${GREEN}python3 -c \"from core.gemma_client import GemmaClient; print('Ready')\"${NC}
  (This will fail — because gemma_client.py doesn't exist yet. That's Day 1.)

${BOLD}Key docs to reference while building:${NC}
  docs/wireframe.html              — Open in browser for visual spec
  docs/UX-COPY-REFERENCE.md        — All UI strings ready to paste
  docs/ACCESSIBILITY-AUDIT.md      — CSS snippets for ASD-friendly design
  prompts/templates.py             — All agent prompts ready to use
  tests/mock_api_responses.py      — MockGemmaClient for offline dev
  tests/gold_standard_outputs.json — Expected outputs for validation
  docs/VIDEO-SCRIPT.md             — Demo flow (build the app around this)
"

echo -e "${BOLD}${GREEN}Good luck, Jeff. Go win this thing. 🦖${NC}\n"
