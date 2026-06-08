#!/usr/bin/env bash
set -e

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; RESET='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║     OSINT Intelligence Suite          ║"
echo "  ║     Kali Linux · Python 3.13          ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${RESET}"

echo -e "${CYAN}[1/4]${RESET} Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip git curl \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev 2>/dev/null || true
echo -e "${GREEN}✓ System deps done${RESET}"

echo -e "${CYAN}[2/4]${RESET} Setting up Python venv: face_env"
if [ ! -d "face_env" ]; then
    python3 -m venv face_env
fi
source face_env/bin/activate
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ venv ready${RESET}"

echo -e "${CYAN}[3/4]${RESET} Installing Python packages..."
pip install streamlit requests Pillow --quiet
pip install opencv-python numpy --quiet 2>/dev/null && \
    echo -e "${GREEN}✓ OpenCV installed (face detection enabled)${RESET}" || \
    echo -e "${YELLOW}⚠ OpenCV skipped — face detection disabled${RESET}"
echo -e "${GREEN}✓ Packages done${RESET}"

echo -e "${CYAN}[4/4]${RESET} Writing run.sh..."
cat > run.sh << 'LAUNCH'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/face_env/bin/activate"
echo "[>] OSINT Suite launching on http://localhost:8501"
streamlit run "$DIR/osint_suite.py" --server.headless true --server.port 8501
LAUNCH
chmod +x run.sh

echo ""
echo -e "${GREEN}╔══════════════════════════════════╗"
echo -e "║   INSTALLATION COMPLETE ✓        ║"
echo -e "╚══════════════════════════════════╝${RESET}"
echo ""
echo -e "  Launch: ${BOLD}bash run.sh${RESET}"
echo -e "  URL:    ${CYAN}http://localhost:8501${RESET}"
echo ""
