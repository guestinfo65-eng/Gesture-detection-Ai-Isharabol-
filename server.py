"""
IshaaraBol server — no pip installs needed, just Python 3 itself.

Serves index.html and proxies the AI Assistant's chat requests to
Fireworks AI, so the API key never has to sit inside browser-visible
JavaScript.

Setup:
    1. Set your Fireworks API key as an environment variable:
         Windows (cmd):        set FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx
         Windows (PowerShell): $env:FIREWORKS_API_KEY="fw_xxxxxxxxxxxxxxxx"
         macOS/Linux:          export FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx
    2. Run:  python server.py
    3. Open: http://localhost:8080

If FIREWORKS_API_KEY isn't set, the app still runs — the AI Assistant
just falls back to its built-in offline replies.
"""

import json
import os
import time
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
MAX_CUSTOM_GESTURES = 100
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
GESTURES_FILE = os.path.join(PROJECT_DIR, "custom_gestures.json")
# Default key so the app works out-of-the-box without any setup step.
# It's still only ever read here, server-side — never sent to the browser.
# You can override it anytime with an environment variable:
#   set FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx      (Windows)
#   export FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxx   (macOS/Linux)
DEFAULT_FIREWORKS_API_KEY = "fw_LA9ZUdKXGsd2yYYCUdcJcE"
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", DEFAULT_FIREWORKS_API_KEY)
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_MODEL = "accounts/fireworks/models/kimi-k2p7-code"
# Used automatically if FIREWORKS_MODEL above returns a "model not found" style
# error (e.g. it's unavailable on your account) — a widely available Fireworks
# chat model, so the assistant still answers instead of going straight offline.
FIREWORKS_FALLBACK_MODEL = "accounts/fireworks/models/llama-v3p1-8b-instruct"

SYSTEM_PROMPT = (
    "You are the in-app help assistant for IshaaraBol, a browser-based sign-to-speech app "
    "for people who can't speak. Answer briefly (2-6 lines), mixing Roman Urdu and English "
    "(Roman Urdu style) unless the user writes in pure English. Key facts about the app: it "
    "runs fully in the browser using the camera, video never leaves the device. It recognizes "
    "a set of core gestures (head nod = YES, head shake = NO, thumbs-up near mouth = WATER, "
    "pinched fingers near mouth = HUNGRY, open hand near puckered lips = KISS/LOVE), plus any "
    "custom signs the user has taught it themselves in the 'My Signs' panel (up to 100, saved "
    "on this computer). Sensitivity (hold time / detection confidence) can be tuned in the "
    "Sensitivity panel. If camera doesn't work: check browser permission, don't open the file "
    "directly (use server.py), use Chrome/Edge, close other apps using the camera."
)


def load_custom_gestures():
    if not os.path.exists(GESTURES_FILE):
        return []
    try:
        with open(GESTURES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_custom_gestures(gestures):
    with open(GESTURES_FILE, "w", encoding="utf-8") as f:
        json.dump(gestures, f, ensure_ascii=False, indent=2)


def get_local_assistant_reply(text):
    lower = (text or "").lower()
    if any(k in lower for k in ["gesture", "sign", "signs", "ishara", "ishare", "all gestures", "list"]):
        return (
            "IshaaraBol supports these core gestures: YES, NO, WATER, HUNGRY, and KISS/LOVE. "
            "It also supports three two-hand signs: THANK YOU, HELP, and STOP/WAIT. "
            "You can add your own custom signs from the My Signs panel."
        )
    if any(k in lower for k in ["camera", "webcam", "not working", "permission", "chrome", "edge"]):
        return (
            "If the camera is not working, allow camera permission in the browser, use Chrome or Edge, "
            "and open the app through the server instead of opening the HTML file directly."
        )
    if any(k in lower for k in ["sensitivity", "hold time", "confidence", "detect", "trigger"]):
        return (
            "You can adjust sensitivity from the Sensitivity panel by changing the gesture hold time and detection confidence. "
            "Increase them if gestures trigger too easily, or lower them if nothing is detected."
        )
    if any(k in lower for k in ["voice", "sound", "speech", "speak", "speak"]):
        return (
            "If there is no voice output, make sure the sound button is on, the browser volume is up, and you click the page once before testing speech."
        )
    if any(k in lower for k in ["help", "emergency"]):
        return "If you need help, the app can trigger an emergency alert and copy a help message for caregivers."
    return (
        "I can help with gestures, camera setup, sensitivity, and voice output. Try asking about gestures, camera, sensitivity, or voice."
    )


def call_fireworks(messages, model=None, max_tokens=400, temperature=0.4):
    """POSTs to Fireworks chat completions. Returns (reply_text, error_str).
    On the primary model failing with a 4xx (e.g. model not found/unauthorized
    for that model), automatically retries once with FIREWORKS_FALLBACK_MODEL.
    """
    use_model = model or FIREWORKS_MODEL
    payload = json.dumps({
        "model": use_model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        FIREWORKS_URL,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip(), None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        # Retry once with the fallback model if the primary model itself is the problem
        # (bad model id, not enabled on this account, etc.) and we haven't already retried.
        if e.code in (400, 404) and use_model != FIREWORKS_FALLBACK_MODEL:
            return call_fireworks(messages, model=FIREWORKS_FALLBACK_MODEL,
                                   max_tokens=max_tokens, temperature=temperature)
        return None, f"Fireworks HTTP {e.code}: {detail[:300]}"
    except urllib.error.URLError as e:
        return None, f"Fireworks request failed: {e.reason}"
    except (KeyError, IndexError, json.JSONDecodeError):
        return None, "Unexpected response from Fireworks"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console quiet

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/gestures":
            self._send_json(200, {"gestures": load_custom_gestures()})
            return
        if self.path == "/api/assistant/health":
            if not FIREWORKS_API_KEY:
                self._send_json(200, {"ok": False, "error": "FIREWORKS_API_KEY not set on server"})
                return
            reply, error = call_fireworks(
                [{"role": "user", "content": "Reply with exactly: OK"}],
                max_tokens=10, temperature=0,
            )
            if error:
                self._send_json(200, {"ok": False, "error": error})
            else:
                self._send_json(200, {"ok": True, "reply": reply})
            return
        requested_path = self.path.split("?", 1)[0]
        path = "index.html" if requested_path in ("/", "") else requested_path.lstrip("/")
        path = os.path.join(PROJECT_DIR, path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        try:
            with open(path, "rb") as f:
                data = f.read()
            self.send_response(200)
            if path.endswith(".html"):
                self.send_header("Content-Type", "text/html; charset=utf-8")
            elif path.endswith(".js"):
                self.send_header("Content-Type", "application/javascript")
            elif path.endswith(".css"):
                self.send_header("Content-Type", "text/css")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/gestures":
            self._handle_add_gesture()
            return
        if self.path == "/api/gestures/delete":
            self._handle_delete_gesture()
            return
        if self.path != "/api/assistant":
            self.send_response(404)
            self.end_headers()
            return

        if not FIREWORKS_API_KEY:
            self._send_json(500, {"error": "FIREWORKS_API_KEY not set on server"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return

        user_text = (body.get("message") or "").strip()
        history = body.get("history") or []
        if not user_text:
            self._send_json(400, {"error": "empty message"})
            return

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": user_text})

        reply, error = call_fireworks(messages)
        if error:
            local_reply = get_local_assistant_reply(user_text)
            self._send_json(200, {"reply": local_reply, "mode": "offline", "error": error})
        else:
            self._send_json(200, {"reply": reply, "mode": "ai"})

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def _handle_add_gesture(self):
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return

        name_en = (body.get("name_en") or "").strip()
        name_ur = (body.get("name_ur") or "").strip()
        icon = (body.get("icon") or "🖐️").strip() or "🖐️"
        vector = body.get("vector")
        hands = body.get("hands", 1)

        if not name_en:
            self._send_json(400, {"error": "name_en is required"})
            return
        if not isinstance(vector, list) or not vector or not all(isinstance(n, (int, float)) for n in vector):
            self._send_json(400, {"error": "vector must be a non-empty list of numbers"})
            return

        gestures = load_custom_gestures()
        if len(gestures) >= MAX_CUSTOM_GESTURES:
            self._send_json(400, {"error": f"Limit of {MAX_CUSTOM_GESTURES} custom gestures reached"})
            return

        entry = {
            "id": f"g{int(time.time() * 1000)}",
            "name_en": name_en,
            "name_ur": name_ur,
            "icon": icon,
            "hands": 2 if hands == 2 else 1,
            "vector": vector,
        }
        gestures.append(entry)
        save_custom_gestures(gestures)
        self._send_json(200, {"gesture": entry, "gestures": gestures})

    def _handle_delete_gesture(self):
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid JSON"})
            return

        gid = body.get("id")
        if not gid:
            self._send_json(400, {"error": "id is required"})
            return

        gestures = load_custom_gestures()
        remaining = [g for g in gestures if g.get("id") != gid]
        save_custom_gestures(remaining)
        self._send_json(200, {"gestures": remaining})


if __name__ == "__main__":
    print(f"Starting IshaaraBol server on http://localhost:{PORT} ...")
    if not FIREWORKS_API_KEY:
        print("NOTE: FIREWORKS_API_KEY is not set — the AI Assistant will use offline replies.")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
