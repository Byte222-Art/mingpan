#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mingpan —— 命盘命令行

用法：
    python bin/mingpan.py bazi "2000-12-12" "20:00" --lon 121 --gender 男
    python bin/mingpan.py liuren                       # 用现在起课
    python bin/mingpan.py liuren --at "2026-10-31 21:57"
    python bin/mingpan.py strength "2000-12-12" "20:00" --lon 121
    python bin/mingpan.py rules --limit 6              # 看看断语库里有什么

只做三件事：排盘、算旺衰、起六壬课。
不发任何网络请求，不写任何文件。
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))

import app as core          # noqa: E402
from liuren_core import cast_at          # noqa: E402
from liuren_core.text import chart_text  # noqa: E402


def _calc(args):
    y, m, d = [int(x) for x in args.date.replace("/", "-").split("-")]
    hh, mm = [int(x) for x in args.time.split(":")]
    return core.calc(y, m, d, hh, mm, args.gender, args.lon)


def cmd_bazi(a):
    r = _calc(a)
    print(f"四柱：{' '.join(r['pillars'])}")
    print(f"真太阳时：{r['true_solar']}（修正 {r['offset_min']} 分）")
    print(f"农历：{r['lunar']}")
    if r.get("strength"):
        s = r["strength"]
        print(f"旺衰：{s['total']} {s['level']}"
              f"（得令 {s['ling']} / 得地 {s['de']} / 得势 {s['shi']}）")
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))


def cmd_strength(a):
    r = _calc(a)
    s = r["strength"]
    print(f"日主 {r['day_gan']}（{r['day_element']}）　旺衰 {s['total']}　{s['level']}")
    print(f"　得令 {s['ling']}（月令{s['month_element']}，{s['month_relation']}）")
    print(f"　得地 {s['de']}（通根 {('、'.join(s['roots']) or '无')}）")
    print(f"　得势 {s['shi']}")
    print("算法：满分 100，得令 40 / 得地 30 / 得势 30。")


def cmd_liuren(a):
    dt = datetime.strptime(a.at, "%Y-%m-%d %H:%M") if a.at else datetime.now()
    chart = cast_at(dt)
    if a.json:
        reading = core.daliuren_reading(chart)
        print(json.dumps({"chart": chart, "reading": reading}, ensure_ascii=False, indent=1))
        return
    print(chart_text(chart))
    print()
    for seg in core.daliuren_reading(chart):
        head = f"[{seg['t']}]"
        if seg["v"]:
            head += f" {seg['v']}"
        print(head)
        print("  " + seg["s"])
        if seg["src"]:
            print(f"  —— {seg['src']}　置信 {seg['conf']}")


def cmd_rules(a):
    kb = json.loads((ROOT / "kb" / "rules.json").read_text(encoding="utf-8-sig"))
    rules = kb["rules"]
    print(f"断语库共 {len(rules)} 条。\n")
    for r in rules[: a.limit]:
        print(f"· [{r['category']}] {r['conclusion'][:46]}…")
        print(f"  条件 {json.dumps(r['condition'], ensure_ascii=False)}")
        print(f"  出处 {r['source']}　置信 {r['confidence']}\n")


def main():
    ap = argparse.ArgumentParser(prog="mingpan", description="命盘 CLI：八字、旺衰、大六壬")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(p):
        p.add_argument("date", help="公历生日 2000-12-12")
        p.add_argument("time", help="出生时间 20:00（24 小时制）")
        p.add_argument("--lon", type=float, default=120.0, help="出生地经度，默认 120")
        p.add_argument("--lat", type=float, default=30.0, help="出生地纬度，默认 30")
        p.add_argument("--gender", default="男", choices=["男", "女"])
        p.add_argument("--json", action="store_true")

    b = sub.add_parser("bazi", help="排四柱 + 旺衰")
    add_common(b)
    b.set_defaults(fn=cmd_bazi)

    s = sub.add_parser("strength", help="只算旺衰，并摊开算法")
    add_common(s)
    s.set_defaults(fn=cmd_strength)

    l = sub.add_parser("liuren", help="大六壬起课（默认用现在）")
    l.add_argument("--at", default="", help='指定时间 "2026-10-31 21:57"')
    l.add_argument("--json", action="store_true")
    l.set_defaults(fn=cmd_liuren)

    k = sub.add_parser("rules", help="看断语库")
    k.add_argument("--limit", type=int, default=5)
    k.set_defaults(fn=cmd_rules)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
