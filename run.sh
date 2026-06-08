#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/face_env/bin/activate"
echo "[>] OSINT Suite launching on http://localhost:8501"
streamlit run "$DIR/osint_suite.py" --server.headless true --server.port 8501
