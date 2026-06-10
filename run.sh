#!/usr/bin/env bash
# OSINT Suite Pro — launcher
# Works on Kali, Ubuntu, Debian, and any system with Python 3.8+
# Just run:  bash run.sh

set -e

VENV_DIR="$HOME/osint-suite/.venv"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP="$SCRIPT_DIR/osint_suite.py"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║       🕵️  OSINT Suite Pro             ║"
echo "  ║       real data · no demos · 2026     ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${RESET}"

# ── 1. Make sure Python 3 exists ─────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[✗] python3 not found. Install it: sudo apt install python3${RESET}"
    exit 1
fi
PYTHON=$(command -v python3)
echo -e "${GREEN}[✓] Python:${RESET} $($PYTHON --version)"

# ── 2. Create venv if it doesn't exist ───────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[→] Creating virtual environment at $VENV_DIR …${RESET}"

    # python3-venv might not be installed on fresh Kali
    if ! $PYTHON -m venv "$VENV_DIR" 2>/dev/null; then
        echo -e "${YELLOW}[→] venv module missing, installing it…${RESET}"
        sudo apt-get install -y python3-venv python3-pip 2>/dev/null || true
        $PYTHON -m venv "$VENV_DIR"
    fi
    echo -e "${GREEN}[✓] Virtual environment created${RESET}"
else
    echo -e "${GREEN}[✓] Virtual environment exists${RESET}"
fi

# ── 3. Activate venv ─────────────────────────────────────────────────────────
source "$VENV_DIR/bin/activate"
PIP="$VENV_DIR/bin/pip"
STREAMLIT="$VENV_DIR/bin/streamlit"

# ── 4. Install / upgrade dependencies ────────────────────────────────────────
PACKAGES="streamlit requests Pillow dnspython"
MISSING=""

for pkg in streamlit requests Pillow dnspython; do
    if ! "$VENV_DIR/bin/python" -c "import ${pkg,,}" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

# fix import name mismatches
if ! "$VENV_DIR/bin/python" -c "import PIL" 2>/dev/null;     then MISSING="$MISSING Pillow"; fi
if ! "$VENV_DIR/bin/python" -c "import dns" 2>/dev/null;     then MISSING="$MISSING dnspython"; fi
if ! "$VENV_DIR/bin/python" -c "import streamlit" 2>/dev/null; then MISSING="$MISSING streamlit"; fi
if ! "$VENV_DIR/bin/python" -c "import requests" 2>/dev/null;  then MISSING="$MISSING requests"; fi

if [ -n "$MISSING" ]; then
    echo -e "${YELLOW}[→] Installing:${RESET}$MISSING"
    "$PIP" install --quiet --upgrade pip
    "$PIP" install --quiet $PACKAGES
    echo -e "${GREEN}[✓] All packages installed${RESET}"
else
    echo -e "${GREEN}[✓] All packages already installed${RESET}"
fi

# optional: python-magic for better file type detection
"$PIP" install --quiet python-magic 2>/dev/null || true

# ── 5. Launch ────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[>] OSINT Suite launching on http://localhost:8501${RESET}"
echo -e "${CYAN}[>] Press Ctrl+C to stop${RESET}"
echo ""

"$STREAMLIT" run "$APP" \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false \
    --server.enableXsrfProtection false
