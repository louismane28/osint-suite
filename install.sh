#!/usr/bin/env bash
# One-time setup for OSINT Suite Pro on Kali / Debian / Ubuntu
# Run once:  bash install.sh
# Then run:  bash run.sh

set -e

VENV_DIR="$HOME/osint-suite/.venv"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

echo -e "${CYAN}[→] OSINT Suite Pro — one-time install${RESET}"

# ensure python3-venv is available
echo -e "${YELLOW}[→] Installing system packages (python3-venv, python3-pip)…${RESET}"
sudo apt-get update -qq
sudo apt-get install -y python3-venv python3-pip curl 2>/dev/null

# create venv
echo -e "${YELLOW}[→] Creating virtual environment…${RESET}"
python3 -m venv "$VENV_DIR"

# install python packages inside venv
echo -e "${YELLOW}[→] Installing Python packages…${RESET}"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet streamlit requests Pillow dnspython python-magic

echo ""
echo -e "${GREEN}[✓] Done! Run the app with:${RESET}"
echo "    bash run.sh"
echo ""
