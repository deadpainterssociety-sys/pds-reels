"""The location tag of every post: the museum where the painting hangs (story.json meta.museum + meta.city, the same place
the ending names). Looked up once per museum and cached in places.json (public facts only):
  - coordinates + a display name from OpenStreetMap (Nominatim)          -> YouTube recordingDetails
  - the museum's Facebook place page (Pages Search, our Facebook token)   -> Instagram location_id
TikTok's API has no location field: the manual-post message on Telegram names the place to add by hand.
A story can force its place with "place": {"ig_location_id": "...", "lat": .., "lon": ..} in story.json.

usage: python automation/places.py <slug>          (prints the place; needs IG_ACCESS_TOKEN for the Instagram id)
"""
import datetime, json, math, os, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import jload, jsave, story

CACHE = "places.json"
UA = "dps-reels/1.0 (+https://github.com/deadpainterssociety-sys/pds-reels)"
RETRY_DAYS = 7


def _get(url, headers=None):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})}), timeout=30))


def _osm(museum, city):
    r = _get("https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({"q": f"{museum}, {city}", "format": "json", "limit": 1}))
    return (float(r[0]["lat"]), float(r[0]["lon"])) if r else (None, None)


def _km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def _facebook_place(museum, city, lat, lon):
    """the museum's Facebook page with a physical location (what Instagram's location_id must be).
    -> (id or None, note); id None + note None means "couldn't ask" (no token / network), so try again next time"""
    import instagram as I
    if not os.environ.get("IG_ACCESS_TOKEN", "").strip() or not I.fb_token(): return None, None
    try: res = I.req("GET", "pages/search", q=f"{museum} {city}", fields="id,name,location,link").get("data", [])
    except Exception as e: return None, f"Meta refused the place search: {str(e)[:200]}"
    for p in res:
        loc = p.get("location") or {}
        if "latitude" not in loc: continue
        if lat is not None and _km(lat, lon, loc["latitude"], loc["longitude"]) > 2.0: continue
        if lat is None and city.lower() not in (loc.get("city") or "").lower(): continue
        return p["id"], f"{p.get('name')} ({p.get('link', '')})"
    return None, f"no place page found among {len(res)} results"


def get(slug):
    """{name, lat, lon, ig_location_id} for the story's museum. Cached in places.json; a lookup that got an answer
    (even "not found") is retried after a week, one that couldn't be made (no network, no token) on the next post."""
    st = story(slug); m = st.get("meta", {})
    museum, city = m.get("museum", ""), m.get("city", "")
    if not museum: return {}
    key = f"{museum}, {city}"
    places = jload(CACHE, {}); p = places.get(key, {}); today = datetime.date.today(); changed = False
    due = lambda f: not p.get(f) and (not p.get(f + "_checked") or (today - datetime.date.fromisoformat(p[f + "_checked"])).days >= RETRY_DAYS)
    if due("lat"):
        try: p["lat"], p["lon"] = _osm(museum, city); p["lat_checked"] = today.isoformat(); changed = True
        except Exception as e: print("places: OpenStreetMap:", e)
    if due("ig_location_id"):
        pid, note = _facebook_place(museum, city, p.get("lat"), p.get("lon"))
        if pid or note: p["ig_location_id"], p["ig_note"], p["ig_location_id_checked"] = pid, note, today.isoformat(); changed = True
    if changed: places[key] = p; jsave(CACHE, places)
    return {"name": key, **{k: p[k] for k in ("lat", "lon", "ig_location_id") if p.get(k) is not None}, **st.get("place", {})}


if __name__ == "__main__":
    m = story(sys.argv[1])["meta"]
    print(get(sys.argv[1]), jload(CACHE, {}).get(f"{m['museum']}, {m['city']}", {}).get("ig_note") or "")
