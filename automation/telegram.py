"""Minimal Telegram Bot API client (no dependencies). Bot token from @BotFather in TELEGRAM_BOT_TOKEN.
Bots can upload files up to 50 MB -> we always send the 540p preview, never the master.
TELEGRAM_API can point to a mock server for tests."""
import html, json, mimetypes, os, urllib.error, urllib.parse, urllib.request, uuid

BASE = os.environ.get("TELEGRAM_API", "https://api.telegram.org").rstrip("/")


class TelegramError(Exception):
    pass


def _url(method): return f"{BASE}/bot{os.environ['TELEGRAM_BOT_TOKEN'].strip()}/{method}"


def call(method, fields=None, files=None, timeout=120):
    fields = {k: (json.dumps(v) if isinstance(v, (dict, list)) else str(v)) for k, v in (fields or {}).items() if v is not None}
    if files:
        b = uuid.uuid4().hex; body = b""
        for k, v in fields.items():
            body += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
        for k, path in files.items():
            ct = mimetypes.guess_type(path)[0] or "application/octet-stream"
            body += (f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{os.path.basename(path)}\"\r\n"
                     f"Content-Type: {ct}\r\n\r\n").encode() + open(path, "rb").read() + b"\r\n"
        body += f"--{b}--\r\n".encode()
        req = urllib.request.Request(_url(method), data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    else:
        req = urllib.request.Request(_url(method), data=urllib.parse.urlencode(fields).encode())
    try:
        r = json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        try: r = json.load(e)
        except Exception: raise TelegramError(f"{method}: HTTP {e.code}")
    if not r.get("ok"): raise TelegramError(f"{method}: {r.get('description', r)}")
    return r["result"]


def esc(s): return html.escape(str(s), quote=False)


def send(chat, text, buttons=None, **kw):
    return call("sendMessage", {"chat_id": chat, "text": text[:4096], "parse_mode": "HTML", "disable_web_page_preview": "true",
                                "reply_markup": {"inline_keyboard": buttons} if buttons else None, **kw})


def photo(chat, path, caption="", buttons=None):
    return call("sendPhoto", {"chat_id": chat, "caption": caption[:1024], "parse_mode": "HTML",
                              "reply_markup": {"inline_keyboard": buttons} if buttons else None}, {"photo": path})


def video(chat, path, caption="", buttons=None):
    return call("sendVideo", {"chat_id": chat, "caption": caption[:1024], "parse_mode": "HTML", "supports_streaming": "true",
                              "width": 540, "height": 960, "reply_markup": {"inline_keyboard": buttons} if buttons else None},
                {"video": path}, timeout=300)


def document(chat, path, caption=""):
    return call("sendDocument", {"chat_id": chat, "caption": caption[:1024], "parse_mode": "HTML"}, {"document": path}, timeout=300)


def album(chat, items):
    """items: [(path, caption)] (2-10 photos)"""
    media = [{"type": "photo", "media": f"attach://p{i}", "caption": c[:1024], "parse_mode": "HTML"} for i, (_, c) in enumerate(items)]
    return call("sendMediaGroup", {"chat_id": chat, "media": media}, {f"p{i}": p for i, (p, _) in enumerate(items)})


def buttons_only(chat, message_id, buttons):
    try: call("editMessageReplyMarkup", {"chat_id": chat, "message_id": message_id, "reply_markup": {"inline_keyboard": buttons}})
    except TelegramError as e: print("  (could not edit buttons:", e, ")")


def answer(callback_id, text=""):
    try: call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text[:200]})
    except TelegramError: pass   # callbacks expire after a while; the chat message we also send is what counts


def updates(offset):
    return call("getUpdates", {"offset": offset, "timeout": 0, "allowed_updates": ["message", "callback_query"]})
