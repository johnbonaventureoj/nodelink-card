"""Generate the three per-person card pages from one template.

Run from the repo root:  py template.py
Writes index.html (John), xavier/index.html, midhun/index.html.

CAMERA-FIRST: the page requests the rear camera immediately on load, so
scanning the QR drops straight into the live feed with the character
overlaid. The browser's permission prompt is the one unavoidable tap
(first visit only - phones remember "Allow" per site). If the camera is
denied or unavailable (e.g. WhatsApp's in-app browser), the page falls
back to the static card layout with a retry button.
"""
import pathlib

PEOPLE = [
    {"out": "index.html", "person": "John", "depth": "",
     "wa": "https://wa.me/447407489335?text=Hi%20John%2C%20I%20scanned%20your%20business%20card"},
    {"out": "xavier/index.html", "person": "Xavier", "depth": "../",
     "wa": "https://wa.me/447553139924?text=Hi%20Xavier%2C%20I%20scanned%20your%20business%20card"},
    # Midhun's printed card QR has always pointed at the main business
    # WhatsApp (John's number) - no separate Midhun number exists on the
    # card, so his chat button keeps that behaviour.
    {"out": "midhun/index.html", "person": "Midhun", "depth": "../",
     "wa": "https://wa.me/447407489335?text=Hi%2C%20I%20scanned%20Midhun%27s%20business%20card"},
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<title>Nodelink Digital</title>
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0; min-height: 100%;
    background: radial-gradient(ellipse at 50% 0%, #152044 0%, #0a0f1a 60%, #060911 100%);
    color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    overflow-x: hidden;
  }

  /* ---------- live camera view (the DEFAULT experience) ---------- */
  #arView { position: fixed; inset: 0; z-index: 50; display: none; background: #000; }
  #arView.on { display: block; }
  #camFeed { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  #arChar {
    position: absolute; left: 50%; bottom: 17%; transform: translateX(-50%);
    width: min(64vw, 300px);
    filter: drop-shadow(0 18px 30px rgba(0,0,0,0.6));
    animation: arrive 0.9s ease-out, breathe 3s ease-in-out 0.9s infinite;
  }
  @keyframes arrive {
    from { opacity: 0; transform: translateX(-50%) translateY(30px) scale(0.92); }
    to   { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  }
  @keyframes breathe {
    0%, 100% { transform: translateX(-50%) translateY(0); }
    50%      { transform: translateX(-50%) translateY(-8px); }
  }
  #arCaption {
    position: absolute; left: 50%; bottom: 11%; transform: translateX(-50%);
    background: rgba(10,15,26,0.78); color: #fff; white-space: nowrap;
    padding: 10px 20px; border-radius: 999px; font-size: 15px; font-weight: 600;
  }
  .arActions {
    position: absolute; left: 0; right: 0; bottom: 2.5%;
    display: flex; justify-content: center; gap: 10px; padding: 0 16px;
  }
  .pill {
    display: flex; align-items: center; gap: 7px;
    padding: 12px 18px; border-radius: 999px; text-decoration: none;
    font-size: 14px; font-weight: 600;
  }
  .pill.site { background: rgba(10,15,26,0.8); color: #fff; }
  .pill.chat { background: #22c55e; color: #06220f; }
  #arClose {
    position: absolute; top: 18px; right: 18px;
    width: 40px; height: 40px; border-radius: 50%; border: none;
    background: rgba(10,15,26,0.7); color: #fff; font-size: 18px; font-weight: 700;
  }

  /* ---------- fallback card layout ---------- */
  .wrap {
    min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    padding: 28px 20px 24px; max-width: 480px; margin: 0 auto;
  }
  .brand { text-align: center; }
  .brand .name { font-size: 15px; font-weight: 700; letter-spacing: 3px; }
  .brand .tag { font-size: 12px; color: #8b93ab; margin-top: 4px; letter-spacing: 0.5px; }
  .stage { position: relative; width: 100%; display: flex; justify-content: center; margin: 6px 0; }
  .glow {
    position: absolute; bottom: 10%; left: 50%; transform: translateX(-50%);
    width: 280px; height: 280px; border-radius: 50%;
    background: radial-gradient(circle, rgba(56,103,255,0.35) 0%, rgba(56,103,255,0) 70%);
    filter: blur(10px); animation: pulse 3.2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 0.55; transform: translateX(-50%) scale(1); }
    50%      { opacity: 1;    transform: translateX(-50%) scale(1.08); }
  }
  .portrait { position: relative; width: min(78vw, 340px); display: block; filter: drop-shadow(0 18px 30px rgba(0,0,0,0.55)); }
  .caption { text-align: center; margin-top: 2px; }
  .caption .hi { font-size: 20px; font-weight: 700; }
  .caption .role { font-size: 13px; color: #8b93ab; margin-top: 3px; }
  .arbtn {
    margin-top: 14px; border: none; border-radius: 999px;
    background: #3867ff; color: #fff; font-size: 15px; font-weight: 600;
    padding: 14px 28px; letter-spacing: 0.2px;
  }
  .actions { width: 100%; display: flex; gap: 12px; margin-top: 18px; }
  .btn {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 4px; padding: 16px 10px; border-radius: 16px; text-decoration: none;
    font-weight: 600; font-size: 14px; letter-spacing: 0.2px;
    border: 1px solid rgba(255,255,255,0.08);
  }
  .btn .icon { font-size: 20px; line-height: 1; }
  .btn.site { background: rgba(255,255,255,0.06); color: #fff; }
  .btn.chat { background: #22c55e; color: #06220f; border-color: transparent; }
  .btn small { font-weight: 400; opacity: 0.75; font-size: 11px; }
  .footer { font-size: 11px; color: #4d5670; margin-top: 20px; text-align: center; }

  @media (prefers-reduced-motion: reduce) {
    .glow, #arChar { animation: none; }
  }
</style>
</head>
<body>

<div id="arView">
  <video id="camFeed" autoplay playsinline muted></video>
  <img id="arChar" src="__DEPTH__assets/portrait.png" alt="Alex Vale">
  <div id="arCaption">Welcome to Nodelink Digital</div>
  <div class="arActions">
    <a class="pill site" href="https://nodelinkdigital.com" target="_blank" rel="noopener">&#127760; Website</a>
    <a class="pill chat" href="__WA__" target="_blank" rel="noopener">&#128172; Chat with __PERSON__</a>
  </div>
  <button id="arClose" aria-label="Close camera view">&#10005;</button>
</div>

<div class="wrap">
  <div class="brand">
    <div class="name">NODELINK DIGITAL</div>
    <div class="tag">We automate what eats your week</div>
  </div>

  <div class="stage">
    <div class="glow"></div>
    <img class="portrait" src="__DEPTH__assets/portrait.png" alt="Alex Vale, Nodelink Digital">
  </div>

  <div class="caption">
    <div class="hi">Hi, I'm Alex.</div>
    <div class="role">Nodelink Digital &mdash; automation for small businesses</div>
  </div>

  <button class="arbtn" id="arStart">&#128247; See me in your room</button>

  <div class="actions">
    <a class="btn site" href="https://nodelinkdigital.com" target="_blank" rel="noopener">
      <span class="icon">&#127760;</span>
      Our website
      <small>nodelinkdigital.com</small>
    </a>
    <a class="btn chat" href="__WA__" target="_blank" rel="noopener">
      <span class="icon">&#128172;</span>
      Chat with __PERSON__
      <small>WhatsApp</small>
    </a>
  </div>

  <div class="footer">Scanned from a business card &middot; Nodelink Digital Ltd</div>
</div>

<script>
(function () {
  var view = document.getElementById('arView');
  var feed = document.getElementById('camFeed');
  var startBtn = document.getElementById('arStart');
  var stream = null;
  var spoken = false;

  function speak() {
    if (spoken) return;
    try {
      var u = new SpeechSynthesisUtterance('Welcome to Nodelink Digital');
      u.rate = 0.95;
      var voices = speechSynthesis.getVoices();
      var en = voices.filter(function (v) { return /en(-|_)GB/i.test(v.lang); })[0]
            || voices.filter(function (v) { return /^en/i.test(v.lang); })[0];
      if (en) u.voice = en;
      u.onstart = function () { spoken = true; };
      speechSynthesis.speak(u);
    } catch (e) { /* caption always shows the line */ }
  }

  function openCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return Promise.reject(new Error('no getUserMedia'));
    }
    return navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }, audio: false
    }).then(function (s) {
      stream = s;
      feed.srcObject = s;
      view.classList.add('on');
      speak();                 // may be blocked pre-gesture; retried on tap
    });
  }

  // Camera-first: ask the moment the page loads. The permission prompt is
  // the browser's own and unavoidable; once allowed, future scans go
  // straight to the live feed.
  openCamera().catch(function () { /* fallback layout stays visible */ });

  // iOS blocks speech before a gesture - first tap anywhere retries it.
  view.addEventListener('click', function () { speak(); });

  startBtn.addEventListener('click', function () {
    openCamera().then(speak).catch(function () {
      alert('Camera is blocked for this browser. If this opened inside ' +
            'WhatsApp, use "Open in browser", or allow camera access in ' +
            'your browser settings for this site.');
    });
  });

  document.getElementById('arClose').addEventListener('click', function (e) {
    e.stopPropagation();
    view.classList.remove('on');
    try { speechSynthesis.cancel(); } catch (err) {}
    if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
  });
})();
</script>

</body>
</html>
"""

here = pathlib.Path(__file__).parent
for p in PEOPLE:
    html = (TEMPLATE
            .replace("__PERSON__", p["person"])
            .replace("__WA__", p["wa"])
            .replace("__DEPTH__", p["depth"]))
    out = here / p["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out)
