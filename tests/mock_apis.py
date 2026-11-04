"""One local HTTP server that imitates the Telegram, Instagram, YouTube, TikTok and GitHub release APIs, so the whole
review -> approve -> publish flow can be tested without real accounts. Every request is recorded in CALLS.
usage (from tests/test_automation.py): srv = MockAPIs(); srv.start(); ... srv.calls(path_part)"""
import json, re, threading, urllib.parse
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CALLS, UPDATES, STATE = [], [], {"msg": 100, "assets": {}, "releases": [], "aid": 1}


def parse_body(h, raw):
    ct = h.get("Content-Type", "")
    if ct.startswith("multipart/form-data"):
        msg = BytesParser(policy=email_policy).parsebytes(b"Content-Type: " + ct.encode() + b"\r\n\r\n" + raw)
        out = {}
        for part in msg.iter_parts():
            name, fn, data = part.get_param("name", header="content-disposition"), part.get_filename(), part.get_payload(decode=True)
            out[name] = f"<file {fn} {len(data)}B>" if fn else data.decode()
        return out
    if ct.startswith("application/x-www-form-urlencoded"): return dict(urllib.parse.parse_qsl(raw.decode()))
    if ct.startswith("application/json"):
        try: return json.loads(raw or b"{}")
        except Exception: return {}
    return {"_bytes": len(raw)}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def reply(self, obj, code=200, headers=None, raw=None):
        body = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(code)
        for k, v in (headers or {}).items(): self.send_header(k, v)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do(self, method):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        u = urllib.parse.urlparse(self.path); q = dict(urllib.parse.parse_qsl(u.query)); body = parse_body(self.headers, raw)
        CALLS.append({"method": method, "path": u.path, "query": q, "body": body, "headers": dict(self.headers), "size": len(raw)})
        p = u.path; port = self.server.server_address[1]
        # ---------- Telegram ----------
        m = re.match(r"/bot([^/]+)/(\w+)", p)
        if m:
            meth = m.group(2)
            if meth == "getMe": return self.reply({"ok": True, "result": {"username": "dps_review_bot"}})
            if meth == "getUpdates":
                off = int(body.get("offset", 0)); res = [u for u in UPDATES if u["update_id"] >= off]
                return self.reply({"ok": True, "result": res})
            if meth == "answerCallbackQuery": return self.reply({"ok": True, "result": True})
            if meth == "editMessageReplyMarkup": return self.reply({"ok": True, "result": True})
            if meth == "sendMediaGroup": return self.reply({"ok": True, "result": [{"message_id": 1}]})
            STATE["msg"] += 1
            return self.reply({"ok": True, "result": {"message_id": STATE["msg"]}})
        # ---------- Instagram ----------
        if p.endswith("/me") and "access_token" in q: return self.reply({"user_id": "1784", "username": "thedeadpainterssociety", "account_type": "BUSINESS"})
        if p.endswith("/me/accounts"): return self.reply({"data": [{"name": "Dead Painters Society", "instagram_business_account": {"id": "17841", "username": "thedeadpainterssociety"}}]})
        if p.endswith("/17841") and method == "GET": return self.reply({"id": "17841", "username": "thedeadpainterssociety"})
        if p.endswith("/17841/media"): return self.reply({"id": "container1"})
        if p.endswith("/17841/media_publish"): return self.reply({"id": "media1"})
        if p.endswith("/me/media"): return self.reply({"id": "container1"})
        if p.endswith("/container1"): return self.reply({"status_code": "FINISHED"})
        if p.endswith("/me/media_publish"): return self.reply({"id": "media1"})
        if p.endswith("/media1"): return self.reply({"permalink": "https://www.instagram.com/reel/TEST/"})
        if p == "/refresh_access_token": return self.reply({"access_token": "IGNEW", "expires_in": 5184000})
        # ---------- YouTube ----------
        if p == "/token": return self.reply({"access_token": "ya29.test"})
        if p.startswith("/youtube/v3/channels"): return self.reply({"items": [{"snippet": {"title": "Dead Painters Society"}}]})
        if p.startswith("/upload/youtube/v3/videos"): return self.reply({}, headers={"Location": f"http://127.0.0.1:{port}/yt-session/1"})
        if p == "/yt-session/1": return self.reply({"id": "YTVID1", "status": {"privacyStatus": "public"}})
        # ---------- TikTok ----------
        if p == "/v2/oauth/token/": return self.reply({"access_token": "act.1", "refresh_token": "rft.NEW", "scope": "video.upload"})
        if p == "/v2/user/info/": return self.reply({"data": {"user": {"display_name": "thedeadpainterssociety"}}})
        if p == "/v2/post/publish/creator_info/query/": return self.reply({"data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"]}})
        if p.endswith("/video/init/"): return self.reply({"data": {"upload_url": f"http://127.0.0.1:{port}/tt-upload/1", "publish_id": "v_pub_1"}, "error": {"code": "ok"}})
        if p == "/tt-upload/1": return self.reply({})
        if p == "/v2/post/publish/status/fetch/": return self.reply({"data": {"status": "SEND_TO_USER_INBOX"}})
        # ---------- GitHub releases ----------
        if p == "/repos/o/r/releases" and method == "GET": return self.reply(STATE["releases"])
        if p == "/repos/o/r/releases" and method == "POST":
            rel = {"id": 1, "name": body["name"], "tag_name": body["tag_name"], "draft": body.get("draft"), "assets": [],
                   "upload_url": f"http://127.0.0.1:{port}/uploads/repos/o/r/releases/1/assets{{?name,label}}"}
            STATE["releases"].append(rel); return self.reply(rel, 201)
        if p == "/uploads/repos/o/r/releases/1/assets":
            aid = STATE["aid"]; STATE["aid"] += 1; STATE["assets"][aid] = raw
            STATE["releases"][0]["assets"].append({"id": aid, "name": q["name"], "url": f"http://127.0.0.1:{port}/repos/o/r/releases/assets/{aid}"})
            return self.reply({"id": aid}, 201)
        m = re.match(r"/repos/o/r/releases/assets/(\d+)", p)
        if m and method == "DELETE":
            aid = int(m.group(1)); STATE["releases"][0]["assets"] = [a for a in STATE["releases"][0]["assets"] if a["id"] != aid]
            return self.reply({}, 204, raw=b"")
        if m: return self.reply({}, 302, headers={"Location": f"http://127.0.0.1:{port}/signed/{m.group(1)}"}, raw=b"")
        m = re.match(r"/signed/(\d+)", p)
        if m:
            if self.headers.get("Authorization"): return self.reply({"error": "token leaked to signed URL"}, 400)
            return self.reply(None, raw=STATE["assets"][int(m.group(1))])
        return self.reply({"error": f"mock: no route {method} {p}"}, 404)

    def do_GET(self): self.do("GET")
    def do_POST(self): self.do("POST")
    def do_PUT(self): self.do("PUT")
    def do_DELETE(self): self.do("DELETE")


class MockAPIs:
    def __init__(self): self.srv = ThreadingHTTPServer(("127.0.0.1", 0), H); self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"
    def start(self): threading.Thread(target=self.srv.serve_forever, daemon=True).start(); return self
    def calls(self, part=""): return [c for c in CALLS if part in c["path"]]
    def tg(self, method): return [c for c in CALLS if c["path"].endswith("/" + method)]
    def push(self, upd): upd["update_id"] = 1000 + len(UPDATES); UPDATES.append(upd)
