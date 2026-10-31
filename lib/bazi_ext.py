# -*- coding: utf-8 -*-
"""八字扩展：神煞 + 流年。"""

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
ELEM = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
        "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

ORDER = ["木", "火", "土", "金", "水"]


def shishen(day_gan, other_gan):
    di, oi = GAN.index(day_gan), GAN.index(other_gan)
    same = (di % 2) == (oi % 2)
    rel = (ORDER.index(ELEM[other_gan]) - ORDER.index(ELEM[day_gan])) % 5
    table = {
        (0, True): "比肩", (0, False): "劫财",
        (1, True): "食神", (1, False): "伤官",
        (2, True): "偏财", (2, False): "正财",
        (3, True): "七杀", (3, False): "正官",
        (4, True): "偏印", (4, False): "正印",
    }
    return table[(rel, same)]


# --- 神煞 ---
TIANYI = {"甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
          "乙": ["子", "申"], "己": ["子", "申"],
          "丙": ["亥", "酉"], "丁": ["亥", "酉"],
          "壬": ["卯", "巳"], "癸": ["卯", "巳"],
          "辛": ["午", "寅"]}

# 三合局：申子辰 / 寅午戌 / 巳酉丑 / 亥卯未
GROUPS = {
    "申子辰": {"桃花": "酉", "驿马": "寅", "华盖": "辰", "将星": "子"},
    "寅午戌": {"桃花": "卯", "驿马": "申", "华盖": "戌", "将星": "午"},
    "巳酉丑": {"桃花": "午", "驿马": "亥", "华盖": "丑", "将星": "酉"},
    "亥卯未": {"桃花": "子", "驿马": "巳", "华盖": "未", "将星": "卯"},
}

YANGREN = {"甲": "卯", "乙": "寅", "丙": "午", "丁": "巳", "戊": "午",
           "己": "巳", "庚": "酉", "辛": "申", "壬": "子", "癸": "亥"}

WENCHANG = {"甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
            "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯"}


def group_of(zhi):
    for k in GROUPS:
        if zhi in k:
            return k
    return None


TAIJI = {"甲": ["子", "午"], "乙": ["子", "午"], "丙": ["卯", "酉"], "丁": ["卯", "酉"],
         "戊": ["辰", "戌", "丑", "未"], "己": ["辰", "戌", "丑", "未"],
         "庚": ["寅", "亥"], "辛": ["寅", "亥"], "壬": ["巳", "申"], "癸": ["巳", "申"]}
LUSHEN = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
          "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
JINYU = {"甲": "辰", "乙": "巳", "丙": "未", "丁": "申", "戊": "未",
         "己": "申", "庚": "戌", "辛": "亥", "壬": "丑", "癸": "寅"}
# 三合局 → 劫煞 / 灾煞 / 亡神
JIESHA = {"申子辰": "巳", "寅午戌": "亥", "巳酉丑": "寅", "亥卯未": "申"}
ZAISHA = {"申子辰": "午", "寅午戌": "子", "巳酉丑": "卯", "亥卯未": "酉"}
WANGSHEN = {"申子辰": "亥", "寅午戌": "巳", "巳酉丑": "申", "亥卯未": "寅"}
# 三会 → 孤辰 / 寡宿
GUCHEN = {"亥子丑": ("寅", "戌"), "寅卯辰": ("巳", "丑"),
          "巳午未": ("申", "辰"), "申酉戌": ("亥", "未")}
HONGLUAN = {"子": "卯", "丑": "寅", "寅": "丑", "卯": "子", "辰": "亥", "巳": "戌",
            "午": "酉", "未": "申", "申": "未", "酉": "午", "戌": "巳", "亥": "辰"}
YUEDE = {"寅午戌": "丙", "申子辰": "壬", "亥卯未": "甲", "巳酉丑": "庚"}
TIANDE = {"寅": "丁", "卯": "申", "辰": "壬", "巳": "辛", "午": "亥", "未": "甲",
          "申": "癸", "酉": "寅", "戌": "丙", "亥": "乙", "子": "巳", "丑": "庚"}


def _hui_group(zhi):
    for k in GUCHEN:
        if zhi in k:
            return k
    return None


GUOYIN = {"甲": "戌", "乙": "亥", "丙": "丑", "丁": "寅", "戊": "丑",
          "己": "寅", "庚": "辰", "辛": "巳", "壬": "未", "癸": "申"}
# 十恶大败：日柱为下列之一
SHIE = {"甲辰", "乙巳", "丙申", "丁亥", "戊戌", "己丑",
        "庚辰", "辛巳", "壬申", "癸亥"}
# 德秀贵人（三命通会）：按月支三合局，定德干与秀干
DEXIU = {
    "寅午戌": (set("丙丁"), set("戊癸")),
    "申子辰": (set("壬癸戊己"), set("丙辛甲己")),
    "巳酉丑": (set("庚辛"), set("乙庚")),
    "亥卯未": (set("甲乙"), set("丁壬")),
}


def shensha(pillars):
    """pillars: ['庚辰','戊子','甲辰','甲戌']"""
    year_gz, month_gz, day_gz, hour_gz = pillars
    day_gan = day_gz[0]
    branches = [p[1] for p in pillars]
    labels = ["年", "月", "日", "时"]
    out = []

    for name, targets in [("天乙贵人", TIANYI.get(day_gan, []))]:
        for t in targets:
            if t in branches:
                out.append({"name": name, "branch": t,
                            "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    g = group_of(year_gz[1]) or group_of(day_gz[1])
    if g:
        for name in ["桃花", "驿马", "华盖", "将星"]:
            t = GROUPS[g][name]
            if t in branches:
                out.append({"name": name, "branch": t,
                            "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    for name, t in [("羊刃", YANGREN.get(day_gan)), ("文昌", WENCHANG.get(day_gan)),
                    ("禄神", LUSHEN.get(day_gan)), ("金舆", JINYU.get(day_gan))]:
        if t and t in branches:
            out.append({"name": name, "branch": t,
                        "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    for t in TAIJI.get(day_gan, []):
        if t in branches:
            out.append({"name": "太极贵人", "branch": t,
                        "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    g2 = group_of(year_gz[1]) or group_of(day_gz[1])
    if g2:
        for name, table in [("劫煞", JIESHA), ("灾煞", ZAISHA), ("亡神", WANGSHEN)]:
            t = table.get(g2)
            if t and t in branches:
                out.append({"name": name, "branch": t,
                            "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    hui = _hui_group(year_gz[1])
    if hui:
        gu, gua = GUCHEN[hui]
        for name, t in [("孤辰", gu), ("寡宿", gua)]:
            if t in branches:
                out.append({"name": name, "branch": t,
                            "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    hl = HONGLUAN.get(year_gz[1])
    if hl:
        for name, t in [("红鸾", hl), ("天喜", CHONG.get(hl, ""))]:
            if t and t in branches:
                out.append({"name": name, "branch": t,
                            "where": [labels[i] for i, b in enumerate(branches) if b == t]})

    # 天德 / 月德（月支起）
    yd = YUEDE.get(group_of(month_gz[1]) or "")
    if yd and yd in [p[0] for p in pillars]:
        out.append({"name": "月德贵人", "branch": yd,
                    "where": [labels[i] for i, p in enumerate(pillars) if p[0] == yd]})
    td = TIANDE.get(month_gz[1])
    if td and td in branches + [p[0] for p in pillars]:
        out.append({"name": "天德贵人", "branch": td,
                    "where": [labels[i] for i, p in enumerate(pillars)
                              if p[0] == td or p[1] == td]})

    # 国印贵人（日干起）
    gy = GUOYIN.get(day_gan)
    if gy and gy in branches:
        out.append({"name": "国印贵人", "branch": gy,
                    "where": [labels[i] for i, b in enumerate(branches) if b == gy]})

    # 十恶大败（日柱）
    if day_gz in SHIE:
        out.append({"name": "十恶大败", "branch": day_gz,
                    "where": ["日"]})

    # 德秀贵人（月支三合局 → 天干）
    grp = group_of(month_gz[1])
    if grp and grp in DEXIU:
        de, xiu = DEXIU[grp]
        stems = [p[0] for p in pillars]
        hit_de = [(i, g) for i, g in enumerate(stems) if g in de]
        hit_xiu = [(i, g) for i, g in enumerate(stems) if g in xiu]
        if hit_de or hit_xiu:
            out.append({"name": "德秀贵人", "branch": "/".join(sorted({g for _, g in hit_de + hit_xiu})),
                        "where": [labels[i] for i, _ in sorted(hit_de + hit_xiu)]})

    # 天罗地网
    if "戌" in branches or "亥" in branches:
        out.append({"name": "天罗", "branch": "戌亥",
                    "where": [labels[i] for i, b in enumerate(branches) if b in ("戌", "亥")]})
    if "辰" in branches or "巳" in branches:
        out.append({"name": "地网", "branch": "辰巳",
                    "where": [labels[i] for i, b in enumerate(branches) if b in ("辰", "巳")]})

    return out


# --- 流年 ---
CHONG = {"子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
         "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳"}
HE = {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
      "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午"}
HAI = {"子": "未", "未": "子", "丑": "午", "午": "丑", "寅": "巳", "巳": "寅",
       "卯": "辰", "辰": "卯", "申": "亥", "亥": "申", "酉": "戌", "戌": "酉"}
XING = {"寅": ["巳", "申"], "巳": ["申", "寅"], "申": ["寅", "巳"],
        "丑": ["戌", "未"], "戌": ["未", "丑"], "未": ["丑", "戌"],
        "子": ["卯"], "卯": ["子"], "辰": ["辰"], "午": ["午"], "酉": ["酉"], "亥": ["亥"]}


def ganzhi_of_year(y):
    i = (y - 4) % 60
    return GAN[i % 10], ZHI[i % 12]


def liunian(pillars, year):
    year_gz, month_gz, day_gz, hour_gz = pillars
    day_gan = day_gz[0]
    g, z = ganzhi_of_year(year)
    rels = []
    labels = ["年", "月", "日", "时"]
    for i, p in enumerate(pillars):
        b = p[1]
        if CHONG.get(z) == b:
            rels.append(f"冲{labels[i]}支{b}")
        if HE.get(z) == b:
            rels.append(f"合{labels[i]}支{b}")
        if HAI.get(z) == b:
            rels.append(f"害{labels[i]}支{b}")
        if b in XING.get(z, []):
            rels.append(f"刑{labels[i]}支{b}")
    return {
        "year": year,
        "ganzhi": g + z,
        "gan": g, "zhi": z,
        "shishen_gan": shishen(day_gan, g),
        "relations": rels,
        "age": year - int(pillars and 2000) if False else None,
    }


# --- 合婚 ---
LIUHE = {"子": "丑", "丑": "子", "寅": "亥", "亥": "寅", "卯": "戌", "戌": "卯",
         "辰": "酉", "酉": "辰", "巳": "申", "申": "巳", "午": "未", "未": "午"}
SANHE = [("申", "子", "辰"), ("寅", "午", "戌"), ("巳", "酉", "丑"), ("亥", "卯", "未")]
PO = {"子": "酉", "酉": "子", "卯": "午", "午": "卯", "辰": "未", "未": "辰",
      "戌": "丑", "丑": "戌", "寅": "亥", "亥": "寅", "巳": "申", "申": "巳"}

ELEM_HINT = {
    "木": "生长、开创、直来直去",
    "火": "表达、热度、外放",
    "土": "稳、守、能扛",
    "金": "规矩、边界、执行力",
    "水": "思考、流动、收纳",
}


def hehun(a, b):
    """a/b: dict(pillars=[...], elements={...}, day_gan, day_zhi, weak=[...])"""
    score = 60
    notes = []

    az, bz = a["day_zhi"], b["day_zhi"]
    if LIUHE.get(az) == bz:
        score += 12
        notes.append(f"日支六合（{az}–{bz}）：夫妻宫对得上，相处有天然的顺。")
    elif any(az in g and bz in g for g in SANHE):
        score += 8
        notes.append(f"日支三合（{az}–{bz}）：同属一局，想法接近。")
    if CHONG.get(az) == bz:
        score -= 12
        notes.append(f"日支相冲（{az}–{bz}）：夫妻宫正对，容易硬碰硬，谁都不退。")
    if HAI.get(az) == bz:
        score -= 6
        notes.append(f"日支相害（{az}–{bz}）：不是大吵，是暗暗消耗。")
    if PO.get(az) == bz:
        score -= 3
        notes.append(f"日支相破（{az}–{bz}）：不致命，但总有一处卡着。")
    if bz in XING.get(az, []):
        score -= 6
        notes.append(f"日支相刑（{az}–{bz}）：容易小事拖成心结。")

    # 五行互补：一方弱、另一方强
    comp = []
    for e in a["weak"]:
        if b["elements"].get(e, 0) >= 1.5:
            score += 5
            comp.append(f"你缺{e}，对方{e}旺——{ELEM_HINT[e]}，正好补你。")
    for e in b["weak"]:
        if a["elements"].get(e, 0) >= 1.5:
            score += 5
            comp.append(f"对方缺{e}，你{e}旺——你在给他{ELEM_HINT[e]}。")

    # 日主关系
    rel = shishen(a["day_gan"], b["day_gan"])
    day_note = {
        "正财": "对方在你这儿是“正财”——踏实、能一起过日子。",
        "偏财": "对方在你这儿是“偏财”——心动多、安稳少。",
        "正官": "对方在你这儿是“正官”——你愿意被管。",
        "七杀": "对方在你这儿是“七杀”——压得住你，也容易伤你。",
        "正印": "对方在你这儿是“正印”——像长辈，护着你。",
        "偏印": "对方在你这儿是“偏印”——懂你，但不好相处。",
        "食神": "对方在你这儿是“食神”——你愿意对他好。",
        "伤官": "对方在你这儿是“伤官”——你会想挑他的刺。",
        "比肩": "对方在你这儿是“比肩”——像自己人，也像对手。",
        "劫财": "对方在你这儿是“劫财”——容易为你破财。",
    }.get(rel, "")

    score = max(30, min(95, score))
    level = "很合" if score >= 80 else ("不错" if score >= 68 else ("一般" if score >= 58 else "磨合多"))

    return {
        "score": score,
        "level": level,
        "day_branches": [az, bz],
        "day_gan_rel": rel,
        "day_note": day_note,
        "relations": notes,
        "complement": comp,
    }

# --- 整体解说 ---
def overall(pillars, elements, shishen_ranked, day_gan, day_element, current_dayun):
    """给一段人话总结。"""
    top = shishen_ranked[0][0] if shishen_ranked else ""
    weak = [k for k, v in elements.items() if v <= 0.4]
    strong = [k for k, v in elements.items() if v >= 2.4]

    p1 = f"日主{day_gan}{day_element}。"
    if day_element == "木":
        p1 += "木是长出来的东西——向上、要空间、不服压。"
    elif day_element == "火":
        p1 += "火是烧出来的东西——要表达、要被看见。"
    elif day_element == "土":
        p1 += "土是承住的东西——能扛、慢热、认死理。"
    elif day_element == "金":
        p1 += "金是砍出来的东西——讲规矩、有边界、下得去手。"
    elif day_element == "水":
        p1 += "水是流过去的东西——能忍、会绕、想得多。"

    p2 = ""
    if strong:
        p2 = f"盘里{('、'.join(strong))}最旺。"
        if "土" in strong:
            p2 += "土旺的人，做事先求稳，钱要看得见才踏实；缺点是慢，机会来了容易犹豫。"
        elif "木" in strong:
            p2 += "木旺的人，主意正、要强，喜欢自己扛；缺点是硬，不爱低头。"
        elif "金" in strong:
            p2 += "金旺的人，边界清楚、说一不二；缺点是容易把人推远。"
        elif "水" in strong:
            p2 += "水旺的人，脑子转得快、能忍；缺点是容易内耗。"
        elif "火" in strong:
            p2 += "火旺的人，外放、藏不住；缺点是急。"

    p3 = ""
    if weak:
        p3 = f"{('、'.join(weak))}偏弱。"
        if "火" in weak:
            p3 += "火弱，是心里有热但不常拿出来；需要主动表达、主动见人，闷着会凉。"
        elif "水" in weak:
            p3 += "水弱，是容易一根筋；需要多听、多留一手。"
        elif "木" in weak:
            p3 += "木弱，是自己立不住；需要先长根，再谈扩张。"
        elif "金" in weak:
            p3 += "金弱，是界限不清；需要学会说不。"
        elif "土" in weak:
            p3 += "土弱，是容易飘；需要一件事做够久。"

    p4 = ""
    if top:
        top_text = {
            "偏财": "偏财最旺——机会多、路子杂，赚钱方式不止一种；但也容易半途换道。",
            "正财": "正财最旺——靠一份稳定的事慢慢积累，不快，但踏实。",
            "比肩": "比肩最旺——自我最强，喜欢自己说了算；合伙要先把账算清。",
            "七杀": "七杀最旺——压力就是你的燃料，越逼越出活；但也容易把自己逼伤。",
            "正官": "正官最旺——适合在有规矩的地方往上走，稳，但少了野。",
            "正印": "正印最旺——靠学习和吸收吃饭，想明白才动手。",
            "偏印": "偏印最旺——直觉准、思路偏门，适合做别人想不到的事。",
            "食神": "食神最旺——适合做内容、做手艺，越做越有味。",
            "伤官": "伤官最旺——锋利、不服管，容易出头也容易得罪人。",
            "劫财": "劫财最旺——朋友多、机会多，但钱容易从手里漏。",
        }.get(top, "")
        p4 = top_text

    p5 = ""
    if current_dayun:
        p5 = f"现在走{current_dayun}运。" + "大运是十年的底色，流年是每年的天气。底色定了，天气只是加减。"

    return [x for x in [p1, p2, p3, p4, p5] if x]

# --- 小六壬 ---
LIUREN = [
    {"name": "大安", "god": "青龙", "elem": "木", "luck": "吉", "dir": "东",
     "duan": "事事昌。求谋在东方，失物去不远，宅舍保安康，行人身未动，病者主无妨。",
     "note": "稳。不动为上，守成则吉。"},
    {"name": "留连", "god": "螣蛇", "elem": "土", "luck": "凶", "dir": "北",
     "duan": "事难成。求谋日未明，官事只宜缓，去者未回程，失物南方见，急讨方称心。",
     "note": "拖。事情黏住了，越急越慢，缓一缓反而通。"},
    {"name": "速喜", "god": "朱雀", "elem": "火", "luck": "吉", "dir": "南",
     "duan": "喜来临。求财向南行，失物申未午，逢人路上寻，官事有福德，病者无祸侵。",
     "note": "快。有消息、有人来，事情会突然推进。"},
    {"name": "赤口", "god": "白虎", "elem": "金", "luck": "凶", "dir": "西",
     "duan": "主口舌。官非切要防，失物急去寻，行人有惊慌，鸡犬多作怪，病者出西方。",
     "note": "争。容易起口角、惹是非，少说一句就少一场。"},
    {"name": "小吉", "god": "玄武", "elem": "水", "luck": "吉", "dir": "东北",
     "duan": "最吉昌。路上好商量，阴人来报喜，失物在坤方，行人即便至，交关甚是强。",
     "note": "顺。有人帮、有回音，是六个里最舒服的一个。"},
    {"name": "空亡", "god": "勾陈", "elem": "土", "luck": "凶", "dir": "中央",
     "duan": "事不祥。阴人少商量，求财无有利，行人有灾殃，失物寻不见，官事主刑伤。",
     "note": "空。白忙一场，或者根本没这回事——先别下注。"},
]


def liuren(lunar_month, lunar_day, shichen):
    """月、日、时辰（子=1…亥=12）三步入宫。"""
    steps = []
    pos = (lunar_month - 1) % 6
    steps.append({"step": "月", "value": lunar_month, "land": LIUREN[pos]["name"]})
    pos = (pos + lunar_day - 1) % 6
    steps.append({"step": "日", "value": lunar_day, "land": LIUREN[pos]["name"]})
    pos = (pos + shichen - 1) % 6
    steps.append({"step": "时", "value": shichen, "land": LIUREN[pos]["name"]})
    return {"steps": steps, "result": LIUREN[pos], "index": pos}


# --- 两盘互证 ---
ZIWEI_WEALTH = {"武曲", "天府", "太阴", "禄存", "贪狼"}
ZIWEI_CAREER = {"紫微", "天府", "廉贞", "天相", "太阳", "武曲"}
ZIWEI_LOVE = {"天相", "太阴", "天同", "太阳"}

def cross_read(bazi, ziwei):
    """bazi: calc() 的返回；ziwei: /api/ziwei 的返回。"""
    out = []

    def palace(name):
        for p in ziwei.get("palaces", []):
            if p.get("name") == name:
                return p
        return {}

    def star_names(p):
        return [x["name"] for x in p.get("majorStars", [])]

    # 1 性格
    day_elem = bazi.get("day_element", "")
    top = bazi.get("top", "")
    ming = palace("命宫")
    ming_stars = star_names(ming)
    same = []
    if day_elem == "木" and set(ming_stars) & {"天机", "贪狼"}:
        same.append("都指向「会想、会转」")
    if day_elem == "木" and set(ming_stars) & {"紫微", "天府", "天相"}:
        same.append("都指向「要立得住、要体面」")
    if day_elem == "木" and set(ming_stars) & {"太阳", "太阴"}:
        same.append("都指向「要往外长、要被看见」")
    if day_elem in ("金",) and set(ming_stars) & {"武曲", "七杀", "紫微"}:
        same.append("都指向「硬、有主张」")
    if day_elem == "土" and set(ming_stars) & {"天府", "天梁", "天相"}:
        same.append("都指向「稳、能扛」")
    out.append({
        "topic": "性格底色",
        "a": f"日主{elem_name(day_elem)}，最旺十神是{top}",
        "b": "命宫" + ("、".join(ming_stars) if ming_stars else "空宫"),
        "verdict": "一致" if same else "各说各的",
        "note": ("；".join(same) + "。") if same else "两边侧重不同，不必硬凑，可以都记着。",
    })

    # 2 财
    cai = sum(v for k, v in bazi.get("_power", {}).items() if k in ("偏财", "正财"))
    cai_p = palace("财帛")
    cai_stars = star_names(cai_p)
    cai_strong = bool(set(cai_stars) & ZIWEI_WEALTH)
    a_text = f"财星 {cai:.1f}（{'旺' if cai >= 2 else '中' if cai >= 1 else '弱'}）"
    b_text = "财帛宫" + ("、".join(cai_stars) if cai_stars else "空宫")
    if cai >= 2 and cai_strong:
        verdict, note = "一致", "两边都说财路是活的——但两边也都没说能守住。"
    elif cai >= 2 and not cai_strong:
        verdict, note = "打架", "八字说财旺，紫微财帛宫却不硬：多半是「机会多、存不住」。"
    elif cai < 1 and cai_strong:
        verdict, note = "打架", "紫微财帛宫有实力星，八字财星却弱：可能是「家里/平台给力，自己不太主动」。"
    else:
        verdict, note = "一致", "两边都不算财旺，靠一样手艺吃饭更稳。"
    out.append({"topic": "财", "a": a_text, "b": b_text, "verdict": verdict, "note": note})

    # 3 官 / 位置
    guan = sum(v for k, v in bazi.get("_power", {}).items() if k in ("正官", "七杀"))
    guan_p = palace("官禄")
    guan_stars = star_names(guan_p)
    guan_strong = bool(set(guan_stars) & ZIWEI_CAREER)
    a_text = f"官杀 {guan:.1f}（{'有' if guan >= 1 else '弱'}）"
    b_text = "官禄宫" + ("、".join(guan_stars) if guan_stars else "空宫")
    if guan_strong and guan >= 1:
        verdict, note = "一致", "位置感是有的，而且两边都指向「在规则里做出来」。"
    elif guan_strong and guan < 1:
        verdict, note = "互补", "紫微说官禄宫不弱，八字官杀却不显：机会多来自平台，不是自己争的。"
    elif not guan_strong and guan >= 1:
        verdict, note = "互补", "八字自带压力，紫微官禄宫却淡：你扛得住事，但不一定想要那个位置。"
    else:
        verdict, note = "一致", "两边都不强求位置，做手艺比做管理顺。"
    out.append({"topic": "官与位置", "a": a_text, "b": b_text, "verdict": verdict, "note": note})

    # 4 感情
    day_zhi = bazi.get("pillars", ["", "", "", ""])[2][1] if bazi.get("pillars") else ""
    love_p = palace("夫妻")
    love_stars = star_names(love_p)
    if set(love_stars) & {"破军", "七杀", "贪狼"}:
        verdict, note = "打架", "八字那边看日支，紫微夫妻宫却是变动星：感情上起伏比命里其它事都大。"
    elif set(love_stars) & ZIWEI_LOVE:
        verdict, note = "一致", "两边都说感情偏稳，慢热型。"
    else:
        verdict, note = "各说各的", "两边没直接对上，感情这条先别下结论。"
    out.append({
        "topic": "感情",
        "a": f"日支{day_zhi}（夫妻宫）",
        "b": "夫妻宫" + ("、".join(love_stars) if love_stars else "空宫"),
        "verdict": verdict, "note": note,
    })

    return out


def elem_name(e):
    return {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}.get(e, e)


# --- 四柱表：藏干/副星/星运/自坐/空亡/纳音/神煞 ---
ZHI_LIST = list("子丑寅卯辰巳午未申酉戌亥")
CHANGSHENG = {"甲":"亥","乙":"午","丙":"寅","丁":"酉","戊":"寅",
              "己":"酉","庚":"巳","辛":"子","壬":"申","癸":"卯"}
CS_NAMES = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
YANG = set("甲丙戊庚壬")


def changsheng(gan, zhi):
    start = ZHI_LIST.index(CHANGSHENG[gan])
    z = ZHI_LIST.index(zhi)
    step = (z - start) % 12 if gan in YANG else (start - z) % 12
    return CS_NAMES[step]


def kongwang(gan, zhi):
    g = "甲乙丙丁戊己庚辛壬癸".index(gan)
    z = ZHI_LIST.index(zhi)
    start = (z - g) % 12
    return ZHI_LIST[(start + 10) % 12] + ZHI_LIST[(start + 11) % 12]


def pillar_table(pillars, day_gan, hidden_map, nayin_list, shensha_list):
    """pillars: ['庚辰',...]; hidden_map: {'辰': ['戊','乙','癸'], ...}"""
    labels = ["年", "月", "日", "时"]
    out = []
    for i, gz in enumerate(pillars):
        gan, zhi = gz[0], gz[1]
        hid = hidden_map.get(zhi, [])
        cang = [{"gan": h, "star": shishen(day_gan, h)} for h in hid]
        ss = [x["name"] for x in shensha_list if labels[i] in x.get("where", [])]
        out.append({
            "label": labels[i],
            "gan": gan,
            "zhi": zhi,
            "ganzhi": gz,
            "main_star": "日主" if i == 2 else shishen(day_gan, gan),
            "cang": cang,
            "xingyun": changsheng(day_gan, zhi),
            "zizuo": changsheng(gan, zhi),
            "kongwang": kongwang(gan, zhi),
            "nayin": nayin_list[i] if i < len(nayin_list) else "",
            "shensha": ss,
        })
    return out

# ---------------- 旺衰量化 ----------------

BRANCH_ELEM = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
               "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

HIDDEN_STEMS = {"子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
                "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "戊", "庚"],
                "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
                "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]}

SEASON = {"寅": "春", "卯": "春", "辰": "春",
          "巳": "夏", "午": "夏", "未": "夏",
          "申": "秋", "酉": "秋", "戌": "秋",
          "亥": "冬", "子": "冬", "丑": "冬"}

# 月令对日主的五种状态：旺(当令) 相(令生我) 休(我生令) 囚(克令) 死(令克我)
LING_SCORE = {"旺": 40, "相": 34, "休": 14, "囚": 8, "死": 4}


def _sheng(a, b):
    """a 生 b"""
    order = ["木", "火", "土", "金", "水"]
    return (order.index(a) + 1) % 5 == order.index(b)


def _ke(a, b):
    """a 克 b"""
    order = ["木", "火", "土", "金", "水"]
    return (order.index(a) + 2) % 5 == order.index(b)


def _relation(month_el, day_el):
    """月令与日主的关系名。"""
    if month_el == day_el:
        return "旺"
    if _sheng(month_el, day_el):
        return "相"
    if _sheng(day_el, month_el):
        return "休"
    if _ke(day_el, month_el):
        return "囚"
    if _ke(month_el, day_el):
        return "死"
    return "休"


def strength(pillars, day_gan):
    """返回旺衰分与三项明细。"""
    day_el = ELEM[day_gan]
    month_zhi = pillars[1][1]
    month_el = BRANCH_ELEM[month_zhi]
    rel = _relation(month_el, day_el)
    ling = LING_SCORE[rel]

    # 得地：通根。日支权重最高
    roots = 0.0
    root_at = []
    where_w = [1.0, 1.1, 1.3, 1.0]  # 年 月 日 时
    for i, gz in enumerate(pillars):
        zhi = gz[1]
        hid = HIDDEN_STEMS.get(zhi, [])
        for j, h in enumerate(hid):
            he = ELEM[h]
            w = [1.0, 0.6, 0.3][j] if len(hid) == 3 else ([1.0, 0.4][j] if len(hid) == 2 else 1.0)
            if he == day_el:
                roots += w * where_w[i]
                root_at.append(zhi)
            elif _sheng(he, day_el):
                roots += w * 0.5 * where_w[i]
    di = min(30, roots * 11)

    # 得势：天干（除日干）中的比劫与印
    shi = 0.0
    for i, gz in enumerate(pillars):
        if i == 2:
            continue
        g = gz[0]
        ge = ELEM[g]
        if ge == day_el:
            shi += 1.0
        elif _sheng(ge, day_el):
            shi += 0.85
    shi_score = min(30, shi * 13)

    total = round(ling + di + shi_score, 1)
    if total >= 76:
        level = "极旺"
    elif total >= 60:
        level = "偏旺"
    elif total >= 45:
        level = "中和"
    elif total >= 30:
        level = "偏弱"
    else:
        level = "极弱"

    return {
        "total": total,
        "level": level,
        "day_element": day_el,
        "month_element": month_el,
        "month_relation": rel,
        "ling": ling,
        "de": round(di, 1),
        "shi": round(shi_score, 1),
        "roots": sorted(set(root_at)),
        "season": SEASON.get(month_zhi, ""),
    }
