# -*- coding: utf-8 -*-
"""八字排盘 · 本地网页版
只监听 127.0.0.1，不对外。启动：py2.exe app.py
"""
import json
import math
import os
import time
import subprocess
import sys
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_here = os.path.dirname(os.path.abspath(__file__))
for _p in (r"C:\Users\Administrator\.dsh\skills\aimood", _here):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import aimood  # noqa: E402
from lunar_python import Solar  # noqa: E402
import bazi_ext  # noqa: E402

from liuren_core import cast_at as liuren_cast  # noqa: E402,MIT: arlen-liang/liuren-bench
from bonefate.bonefate import BoneFates  # noqa: E402

HIDDEN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"], "卯": ["乙"],
    "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"], "午": ["丁", "己"],
    "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"], "酉": ["辛"],
    "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}
HERE = Path(__file__).parent
TOKEN = os.environ.get("MINGPAN_TOKEN", "").strip()
_RATE = {}
RATE_LIMIT = 60


def _client_ip(handler):
    fwd = handler.headers.get("CF-Connecting-IP") or handler.headers.get("X-Forwarded-For")
    if fwd:
        return fwd.split(",")[0].strip()
    return handler.client_address[0]


def _allowed(handler):
    # 本机放行；其余必须带口令。返回 (ok, set_cookie)
    ip = _client_ip(handler)
    if ip in ("127.0.0.1", "::1"):
        return True, False
    if not TOKEN:
        return True, False
    u = urlparse(handler.path)
    q = parse_qs(u.query)
    if (q.get("k") or [""])[0] == TOKEN:
        return True, True
    if TOKEN in (handler.headers.get("Cookie") or ""):
        return True, False
    return False, False


def _rate_ok(ip):
    now = time.time()
    hits = [t for t in _RATE.get(ip, []) if now - t < 60]
    if len(hits) >= RATE_LIMIT:
        _RATE[ip] = hits
        return False
    hits.append(now)
    _RATE[ip] = hits
    return True
NODE = "node"

# 五行、十神说明（人话版）
SHISHEN_TEXT = {
    "比肩": "和我一样的力量。主见强，不喜欢被安排，也容易硬撑。",
    "劫财": "争我的力量。朋友多，但也容易为朋友破财。",
    "食神": "我说出来的东西。温和的表达欲，做内容的天赋。",
    "伤官": "我要说破的东西。锋利、不服管、容易得罪人。",
    "偏财": "流动的资源。机会、人脉、钱，来得杂。",
    "正财": "稳定的资源。一份踏实的收入和一段踏实的关系。",
    "七杀": "压我的力量。压力、竞争、也代表行动力和狠劲。",
    "正官": "管我的规矩。责任、位置、被认可。",
    "偏印": "偏门的学习。直觉、冷知识、想得多。",
    "正印": "正经的学习。吸收能力、长辈缘、文凭。",
}

ELEMENT_OF = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

# 地支五行 + 藏干（本气/中气/余气）
BRANCH = {
    "子": ("水", ["癸"]),
    "丑": ("土", ["己", "癸", "辛"]),
    "寅": ("木", ["甲", "丙", "戊"]),
    "卯": ("木", ["乙"]),
    "辰": ("土", ["戊", "乙", "癸"]),
    "巳": ("火", ["丙", "戊", "庚"]),
    "午": ("火", ["丁", "己"]),
    "未": ("土", ["己", "丁", "乙"]),
    "申": ("金", ["庚", "壬", "戊"]),
    "酉": ("金", ["辛"]),
    "戌": ("土", ["戊", "辛", "丁"]),
    "亥": ("水", ["壬", "甲"]),
}
HIDDEN_W = [0.6, 0.3, 0.1]


def element_scores(pillars):
    """天干 1.0；地支本气 0.6 / 中气 0.3 / 余气 0.1"""
    score = {e: 0.0 for e in ["木", "火", "土", "金", "水"]}
    for p in pillars:
        gan, zhi = p[0], p[1]
        score[ELEMENT_OF[gan]] += 1.0
        main, hidden = BRANCH[zhi]
        score[main] += 0.6
        for i, h in enumerate(hidden[1:], start=1):
            score[ELEMENT_OF[h]] += HIDDEN_W[i]
    return {k: round(v, 2) for k, v in score.items()}


def equation_of_time(dt):
    n = dt.timetuple().tm_yday
    b = 2 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


# ---------------- 六壬断课（M2 第一版） ----------------

_HERE = Path(__file__).parent
_KB = next((x for x in (_HERE / "kb" / "keti.json", _HERE.parent / "kb" / "keti.json") if x.exists()),
           _HERE / "kb" / "keti.json")
_KETI = {"keti": [], "jiang": {}}
try:
    import json as _json
    _KETI = _json.loads(_KB.read_text(encoding="utf-8-sig"))
except Exception:
    pass

_WX = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
       "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}
_GAN_WX = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
           "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_ORDER = ["木", "火", "土", "金", "水"]
_JJ = {"贵": "贵人", "蛇": "螣蛇", "雀": "朱雀", "合": "六合", "勾": "勾陈",
       "龙": "青龙", "空": "天空", "虎": "白虎", "常": "太常", "玄": "玄武",
       "阴": "太阴", "后": "天后"}


def _sheng(a, b):
    return (_ORDER.index(a) + 1) % 5 == _ORDER.index(b)


def _ke(a, b):
    return (_ORDER.index(a) + 2) % 5 == _ORDER.index(b)


def _rel(a, b):
    """a 对 b 的关系：生/克/同/被生/被克"""
    if a == b:
        return "同"
    if _sheng(a, b):
        return "生你"
    if _ke(a, b):
        return "克你"
    if _sheng(b, a):
        return "你生"
    return "你克"


def daliuren_reading(chart):
    """把课盘翻成三句话。写的是推断，不是结论。"""
    day = chart["input"]["day"]
    gan, zhi = day[0], day[1]
    gan_wx = _GAN_WX.get(gan, "土")
    name = chart["method"]["name"]
    info = next((k for k in _KETI.get("keti", []) if k["name"] == name), None)
    if info is None and "·" in name:
        short = name.split("·")[-1]
        info = next((k for k in _KETI.get("keti", []) if k["name"] == short), None)

    out = []
    if info:
        out.append({"t": "课体", "v": name,
                    "s": info["tone"], "src": info["source"], "conf": info["confidence"]})
    else:
        out.append({"t": "课体", "v": name, "s": "这一体的含义我还没写。", "src": "—", "conf": "—"})

    # 三传走势
    chuans = chart.get("transmissions", [])
    if len(chuans) == 3:
        wx = [_WX.get(t["branch"], "") for t in chuans]
        chain = []
        for i in range(2):
            chain.append(_rel(wx[i], wx[i + 1]))
        if chain == ["生你", "生你"] or chain == ["生你", "生你"]:
            flow = "初生中、中生末，一路顺下去，事能往前走。"
        elif "克你" in chain:
            flow = "传里有相克，中间会卡一下，卡住那一步是关节。"
        else:
            flow = "三传之间不生不克，走得不快，但也不算阻。"
        first = chuans[0]
        rel_gan = _rel(_WX.get(first["branch"], ""), gan_wx)
        rel_txt = {
            "生你": "初传生你，起手是有人推你一把。",
            "克你": "初传克你，起手就顶着压力。",
            "你生": "初传由你生出，这事是你自己起的头。",
            "你克": "初传被你克，你能压得住开头。",
            "同": "初传与你同气，起手像照镜子。",
        }.get(rel_gan, "")
        out.append({"t": "三传", "v": "→".join(t["branch"] for t in chuans),
                    "s": (rel_txt + flow).strip(), "src": "《六壬大全·课经》三传", "conf": "中"})
        gj = first.get("general", "")
        j = _KETI.get("jiang", {}).get(_JJ.get(gj, gj), "")
        if j:
            out.append({"t": "初传天将", "v": first.get("general", ""),
                        "s": j, "src": "《毕法赋》天将", "conf": "中"})

    out.append({"t": "口径", "v": "",
                "s": "起课是算，断课是读。这里每一句都是推断，标了置信，你可以不信。",
                "src": "", "conf": ""})
    return out


def calc(year, month, day, hour, minute, gender, lon):
    # 真太阳时
    base = datetime(year, month, day, hour, minute)
    eot = equation_of_time(base)
    lon_min = (lon - 120.0) * 4
    true_dt = base + timedelta(minutes=lon_min + eot)

    # 23:00–23:59 为晚子时，按次日子时起（换日说）
    calc_dt = true_dt + timedelta(hours=1) if true_dt.hour == 23 else true_dt
    p = aimood.paipan(calc_dt.year, calc_dt.month, calc_dt.day,
                      calc_dt.hour, calc_dt.minute, gender)
    solar = Solar.fromYmdHms(calc_dt.year, calc_dt.month, calc_dt.day,
                             calc_dt.hour, calc_dt.minute, 0)
    lunar = solar.getLunar()

    power = p["shishen_power"]
    ranked = sorted(power.items(), key=lambda x: -x[1])
    top = ranked[0][0] if ranked else ""
    pillars = [p["year"], p["month"], p["day"], p["hour"]]
    elements = element_scores(pillars)
    weak = [k for k, v in elements.items() if v <= 0.4]

    return {
        "true_solar": true_dt.strftime("%Y-%m-%d %H:%M"),
        "offset_min": round(lon_min + eot, 1),
        "pillars": [p["year"], p["month"], p["day"], p["hour"]],
        "day_gan": p["day_gan"],
        "day_element": ELEMENT_OF.get(p["day_gan"], ""),
        "lunar": lunar.toString(),
        "jieqi": [lunar.getPrevJieQi().getName(), lunar.getNextJieQi().getName()],
        "nayin": [lunar.getYearNaYin(), lunar.getMonthNaYin(), lunar.getDayNaYin()],
        "shishen": [{"name": k, "power": round(v, 2), "text": SHISHEN_TEXT.get(k, "")}
                    for k, v in ranked],
        "elements": elements,
        "weak": weak,
        "top": top,
        "top_text": SHISHEN_TEXT.get(top, ""),
        "dayun": [{"gz": d["ganzhi"], "start": d["start_age"], "end": d["end_age"]}
                  for d in p["dayun"][:8]],
        "shensha": bazi_ext.shensha(pillars),
        "strength": bazi_ext.strength(pillars, p["day_gan"]),
        "pillar_table": bazi_ext.pillar_table(
            pillars, p["day_gan"], HIDDEN,
            [lunar.getYearNaYin(), lunar.getMonthNaYin(), lunar.getDayNaYin(),
             (lunar.getTimeNaYin() if hasattr(lunar, "getTimeNaYin") else "")],
            bazi_ext.shensha(pillars)),
        "_power": {k: round(v, 2) for k, v in power.items()},
        "chenggu": chenggu_of(true_dt, pillars[3][1]),
        "overall": bazi_ext.overall(pillars, elements, ranked, p["day_gan"],
                                    ELEMENT_OF.get(p["day_gan"], ""),
                                    p["dayun"][1]["ganzhi"] if len(p["dayun"]) > 1 else ""),
    }



def chenggu_of(dt, hour_zhi):
    try:
        b = BoneFates(dt.year, dt.month, dt.day, hour_zhi)
        w = b.bone_weight
        liang = int(w)
        qian = int(round((w - liang) * 10))
        text = f"{liang}两{qian}钱" if qian else f"{liang}两"
        return {"weight": w, "text": text, "poem": b.poem}
    except Exception as e:
        return {"error": str(e)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        ip = _client_ip(self)
        if ip not in ("127.0.0.1", "::1") and not _rate_ok(ip):
            msg = "\u592a\u9891\u7e41\u4e86\uff0c\u6b47\u4e00\u5206\u949f\u3002".encode("utf-8")
            self.send_response(429)
            self.send_header("Retry-After", "60")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return
        ok, set_cookie = _allowed(self)
        if not ok:
            body = ("<!doctype html><meta charset=utf-8><title>need key</title>"
                    "<div style=\"font:16px/1.8 system-ui;padding:40px;color:#ddd;background:#0b0d12\">"
                    "<h2 style=\"color:#e2b04a\">\u9700\u8981\u53e3\u4ee4</h2>"
                    "<p>\u8fd9\u4e2a\u9875\u9762\u662f\u79c1\u4eba\u7684\u3002"
                    "\u8bf7\u7528\u5e26 k \u53c2\u6570\u7684\u5b8c\u6574\u94fe\u63a5\u3002</p></div>").encode("utf-8")
            self.send_response(403)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if set_cookie:
            from urllib.parse import urlencode
            qs = parse_qs(u.query)
            qs.pop("k", None)
            newq = urlencode({k: v[0] for k, v in qs.items()})
            loc = u.path + ("?" + newq if newq else "")
            self.send_response(302)
            self.send_header("Set-Cookie",
                             "k=" + TOKEN + "; Path=/; Max-Age=2592000; HttpOnly; SameSite=Lax")
            self.send_header("Location", loc)
            self.end_headers()
            return
        if u.path in ("/", "/index.html"):
            body = (HERE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if u.path.startswith("/assets/"):
            f = HERE / "assets" / u.path[len("/assets/"):]
            if f.is_file():
                body = f.read_bytes()
                ctype = "image/png" if f.suffix.lower() == ".png" else "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()
            return

        if u.path == "/api/bazi":
            q = parse_qs(u.query)
            try:
                _y, _m, _d = int(q["y"][0]), int(q["m"][0]), int(q["d"][0])
                if not (1900 <= _y <= 2100 and 1 <= _m <= 12 and 1 <= _d <= 31):
                    raise ValueError("日期超出范围")
                data = calc(
                    _y, _m, _d,
                    int(q["h"][0]), int(q.get("mi", ["0"])[0]),
                    q.get("g", ["男"])[0],
                    float(q.get("lon", ["120"])[0]),
                )
                body = json.dumps(data, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return


        if u.path == "/api/liunian":
            q = parse_qs(u.query)
            try:
                y = int(q["y"][0]); m = int(q["m"][0]); d = int(q["d"][0])
                h = int(q["h"][0]); g = q.get("g", ["男"])[0]
                base = datetime(y, m, d, h, int(q.get("mi", ["0"])[0]))
                p = aimood.paipan(base.year, base.month, base.day,
                                  base.hour, base.minute, g)
                pillars = [p["year"], p["month"], p["day"], p["hour"]]
                years = [int(v) for v in q.get("years", [""])[0].split(",") if v.strip()]
                out = {"pillars": pillars,
                       "items": [bazi_ext.liunian(pillars, yy) for yy in years]}
                body = json.dumps(out, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return

        if u.path == "/api/hehun":
            q = parse_qs(u.query)
            try:
                def side(pre):
                    y = int(q[pre + "y"][0]); m = int(q[pre + "m"][0]); d = int(q[pre + "d"][0])
                    h = int(q[pre + "h"][0]); mi = int(q.get(pre + "mi", ["0"])[0])
                    g = q.get(pre + "g", ["男"])[0]
                    base = datetime(y, m, d, h, mi)
                    eot = equation_of_time(base)
                    lon = float(q.get(pre + "lon", ["120"])[0])
                    t = base + timedelta(minutes=(lon - 120.0) * 4 + eot)
                    p = aimood.paipan(t.year, t.month, t.day, t.hour, t.minute, g)
                    pillars = [p["year"], p["month"], p["day"], p["hour"]]
                    els = element_scores(pillars)
                    return {
                        "pillars": pillars,
                        "day_gan": p["day_gan"],
                        "day_zhi": pillars[2][1],
                        "elements": els,
                        "weak": [k for k, v in els.items() if v <= 0.4],
                        "gender": g,
                    }
                a = side("a_")
                b = side("b_")
                out = {"a": a, "b": b, "result": bazi_ext.hehun(a, b)}
                body = json.dumps(out, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return


        if u.path == "/api/export":
            self.send_response(410)
            self.end_headers()
            return
        if False:
            q = parse_qs(u.query)
            inner = q.get("q", [""])[0]
            tmp = HERE / "_export_tmp.png"
            try:
                if tmp.exists():
                    tmp.unlink()
                url = "http://127.0.0.1:8765/?" + inner
                edge = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
                r = subprocess.run(
                    [edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                     "--no-first-run", "--no-default-browser-check",
                     "--virtual-time-budget=9000",
                     "--window-size=1100,3800",
                     "--user-data-dir=E:/sd/browser-profile",
                     "--screenshot=" + str(tmp), url],
                    capture_output=True, timeout=120,
                    encoding="utf-8", errors="replace", cwd=str(HERE))
                if not tmp.exists() or tmp.stat().st_size == 0:
                    raise RuntimeError("截图失败: " + (r.stderr or "")[-300:])
                data = tmp.read_bytes()
                tmp.unlink(missing_ok=True)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Disposition", 'attachment; filename="mingpan.png"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return

        if u.path == "/api/cross":
            q = parse_qs(u.query)
            try:
                data = calc(int(q["y"][0]), int(q["m"][0]), int(q["d"][0]),
                            int(q["h"][0]), int(q.get("mi", ["0"])[0]),
                            q.get("g", ["男"])[0], float(q.get("lon", ["120"])[0]))
                idx = int(q["h"][0])
                idx = 0 if idx == 0 else (12 if idx == 23 else (idx + 1) // 2)
                date = "%04d-%02d-%02d" % (int(q["y"][0]), int(q["m"][0]), int(q["d"][0]))
                r = subprocess.run(["node", str(HERE / "ziwei.js"), date, str(idx),
                                    q.get("g", ["男"])[0]],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=60, cwd=str(HERE))
                zw = json.loads(r.stdout.strip() or "{}")
                out = {"items": bazi_ext.cross_read(data, zw)}
                body = json.dumps(out, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return


        if u.path == "/api/daliuren":
            q = parse_qs(u.query)
            try:
                y = int((q.get("y") or ["0"])[0])
                mo = int((q.get("mo") or ["0"])[0])
                d = int((q.get("d") or ["0"])[0])
                hh = int((q.get("h") or ["0"])[0])
                mi = int((q.get("mi") or ["0"])[0])
                if y and mo and d:
                    if not (1900 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31):
                        raise ValueError("日期超出范围")
                    dt = datetime(y, mo, d, hh, mi)
                else:
                    dt = datetime.now()
                chart = liuren_cast(dt)
                reading = daliuren_reading(chart)
                body = json.dumps({"ok": True, "chart": chart, "reading": reading}, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"ok": False, "err": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return

        if u.path == "/api/liuren":
            q = parse_qs(u.query)
            try:
                if q.get("now"):
                    base = datetime.now()
                else:
                    base = datetime(int(q["y"][0]), int(q["m"][0]), int(q["d"][0]),
                                    int(q["h"][0]), int(q.get("mi", ["0"])[0]))
                solar = Solar.fromYmdHms(base.year, base.month, base.day, base.hour, base.minute, 0)
                lunar = solar.getLunar()
                # 时辰序号：子=1 … 亥=12（23点后归子）
                h = base.hour
                idx = ((h + 1) // 2) % 12 + 1 if h != 23 else 1
                r = bazi_ext.liuren(lunar.getMonth(), lunar.getDay(), idx)
                r["solar"] = base.strftime("%Y-%m-%d %H:%M")
                r["lunar"] = lunar.toString()
                r["shichen"] = "子丑寅卯辰巳午未申酉戌亥"[idx - 1] + "时"
                body = json.dumps(r, ensure_ascii=False).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return

        if u.path == "/api/ziwei":
            q = parse_qs(u.query)
            try:
                y = int(q["y"][0]); m = int(q["m"][0]); d = int(q["d"][0])
                h = int(q["h"][0]); g = q.get("g", ["男"])[0]
                idx = 0 if h == 0 else (12 if h == 23 else (h + 1) // 2)
                date = f"{y:04d}-{m:02d}-{d:02d}"
                r = subprocess.run(["node", str(HERE / "ziwei.js"), date, str(idx), g],
                                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, cwd=str(HERE))
                out = r.stdout.strip() or json.dumps({"error": r.stderr[:300]}, ensure_ascii=False)
                body = out.encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}, ensure_ascii=False).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("MINGPAN_PORT", "8765"))
    host = os.environ.get("MINGPAN_HOST", "127.0.0.1")
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"http://{host}:{port}")
    srv.serve_forever()
