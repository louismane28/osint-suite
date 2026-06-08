<div align="center">

<!-- Logo -->
<img src="https://raw.githubusercontent.com/louismane28/osint-suite/main/assets/logo.svg" width="96" alt="OSINT Suite Pro Logo"/>

# OSINT Suite Pro

### Intelligence Platform · v2.0 · 2026

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-00c6ff?style=for-the-badge)](LICENSE)
[![Live App](https://img.shields.io/badge/Live%20App-Deploy-00e676?style=for-the-badge&logo=streamlit)](https://louismane28-osint-suite.streamlit.app)

**A professional, all-in-one open-source intelligence and security research platform.**  
Built for OSINT analysts, CTF competitors, penetration testers, and curious minds.

---

</div>

## ✨ Features

| Tab | Tool | Description |
|-----|------|-------------|
| 🔍 | **Reverse Image** | Upload → auto-host → open Google Lens, Yandex, Bing Visual, TinEye |
| 👤 | **Username Hunt** | Search 60+ global platforms simultaneously with name variation engine |
| 📧 | **Email OSINT** | Gravatar lookup, HIBP breach check, EmailRep reputation score |
| 📁 | **Metadata & EXIF** | Extract GPS, camera info, timestamps from any image |
| 🎯 | **CTF Solver** | 10 interactive tools: multi-decoder, ROT brute-force, hash ID, base converter, Caesar/Vigenère, encoding chains, steg guide, web payloads, forensics, RE |
| 🔬 | **Deep File Scan** | Entropy heatmap, string extraction, embedded file signatures, flag pattern search |
| 🌐 | **Network Recon** | DNS (all record types), IP geolocation + map, port scan, threat intel |
| 🔑 | **Password Intel** | Strength analyzer with entropy, hash generator, targeted wordlist builder |
| 🎵 | **TikTok Finder** | 15+ username variants, live profile checks, direct search links |
| 🛡️ | **Pentest Suite** | 15 categories: recon, exploitation, shells, privesc, cloud, pivoting |
| 🔐 | **Crypto CTF+** | RSA solver, XOR brute-force, frequency analysis, classic cipher library |
| 🕵️ | **Google Dorking** | 8 dork categories, custom builder, one-click Google search |
| 🌐 | **Subdomain Recon** | Live crt.sh + HackerTarget + local tool command generator |
| 📖 | **Beginner Guide** | Roadmap, CTF quickstart, Linux basics, Python snippets, glossary |

---

## 🚀 Quick Start

### Run locally

```bash
git clone https://github.com/louismane28/osint-suite.git
cd osint-suite
pip install -r requirements.txt
streamlit run osint_suite.py
```

### Deploy on Streamlit Cloud (free)

[![Deploy](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. New app → select your fork → `main` → `osint_suite.py` → Deploy

---

## 🎯 Who is this for?

- **CTF competitors** — solvers for crypto, forensics, steg, web, RE, pwn
- **OSINT analysts** — username hunt, email intel, reverse image, dorking
- **Penetration testers** — pentest command reference, subdomain recon, network recon
- **Beginners** — guided roadmap, glossary, Python snippets, free resource links
- **Everyday curious people** — no setup, runs in browser, completely free

---

## 🛡️ Legal & Ethics

This tool is built for **authorized security research, CTF competitions, and educational use only.**  
Never use against systems you don't own or have explicit permission to test.  
All data lookups use public APIs and open-source intelligence sources.

---

## 📦 Stack

- **Frontend:** Streamlit + custom iOS liquid glass CSS
- **Backend:** Python 3.13
- **APIs:** ip-api.com · crt.sh · HackerTarget · EmailRep · Gravatar · tmpfiles.org
- **Libraries:** `requests` · `dnspython` · `Pillow`

---

## 🤝 Contributing

Pull requests welcome. Open an issue for bugs or feature requests.

---

<div align="center">
<sub>Built with 🔍 by the community · Real data only · Open source forever</sub>
</div>
