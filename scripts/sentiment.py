"""
关键词词典 + 新闻情绪打分。

逻辑：
1. 判断一条快讯是否与某个品种"相关"——命中该品种的别名词、所属板块的板块词、
   或该板块的宏观触发词（如贵金属板块的"美联储/加息"），才算相关，
   避免无关新闻（比如纯地震快讯）稀释信号。宏观触发词不要求同时出现品种名，
   因为FOMC声明原文不会提"黄金"，但对贵金属板块仍是强相关信号。
2. 只在相关快讯里，用该品种所属板块的正负面关键词词典做计数，
   net = 正面命中数 - 负面命中数，再映射到 -1/0/+1。

本模块是纯函数，不做任何网络请求，方便单独测试。
"""

# 品种别名：用于判断一条快讯是否与该品种相关
VARIETY_ALIASES = {
    "RB0": ["螺纹钢", "螺纹"],
    "I0": ["铁矿石", "铁矿"],
    "M0": ["豆粕"],
    "C0": ["玉米"],
    "P0": ["棕榈油"],
    "CU0": ["铜", "铜价"],
    "AU0": ["黄金", "金价"],
    "AG0": ["白银", "银价"],
    "MA0": ["甲醇"],
    "TA0": ["PTA", "精对苯二甲酸"],
}

# 板块词：也用于相关性判断（覆盖"黑色系整体"这种泛指表述）
SECTOR_ALIASES = {
    "黑色系": ["黑色系", "黑色建材"],
    "农产品": ["农产品"],
    "有色金属": ["有色金属", "有色"],
    "贵金属": ["贵金属"],
    "能化": ["能化", "化工"],
}

# 按板块给出的正负面关键词词典
SECTOR_KEYWORDS = {
    "黑色系": {
        "positive": ["限产", "减产", "去库", "检修", "环保限产", "提价", "补库存"],
        "negative": ["累库", "增产", "过剩", "降价", "需求疲软", "停工", "拖累"],
    },
    "农产品": {
        "positive": ["减产", "干旱", "洪涝", "天气灾害", "库存下降", "进口减少", "出口增加"],
        "negative": ["丰产", "增产", "库存上升", "抛储", "进口增加", "供应充足"],
    },
    "有色金属": {
        "positive": ["减产", "罢工", "矿端扰动", "库存下降", "需求回暖", "供应中断"],
        "negative": ["累库", "增产", "需求疲软", "贸易摩擦", "供应过剩"],
    },
    "贵金属": {
        "positive": ["降息", "避险", "地缘冲突", "美元走弱", "通胀上升", "降息预期"],
        "negative": ["加息", "美元走强", "风险偏好回升", "经济数据强劲", "鹰派"],
    },
    "能化": {
        "positive": ["装置检修", "减产", "成本上升", "原油上涨", "开工率下降"],
        "negative": ["装置重启", "增产", "库存上升", "原油下跌", "需求疲软", "开工率上升"],
    },
}

# 板块宏观触发词：命中即判定相关，不要求同时出现品种名/板块名
# 用于匹配宏观快讯（如FOMC声明、央行讲话、地缘政治），这类新闻通常不会出现具体品种词
SECTOR_MACRO_TRIGGERS = {
    "黑色系": ["基建", "房地产", "钢铁行业", "地产政策"],
    "农产品": ["天气", "关税", "贸易战", "贸易协定", "极端天气"],
    "有色金属": ["美联储", "美元", "加息", "降息", "工业产出", "制造业PMI"],
    "贵金属": ["美联储", "美元", "加息", "降息", "FOMC", "非农", "CPI", "通胀", "避险情绪", "地缘冲突"],
    "能化": ["原油", "OPEC", "美联储", "美元", "地缘冲突"],
}


def is_relevant(content: str, code: str, sector: str) -> bool:
    for alias in VARIETY_ALIASES.get(code, []):
        if alias in content:
            return True
    for alias in SECTOR_ALIASES.get(sector, []):
        if alias in content:
            return True
    for trigger in SECTOR_MACRO_TRIGGERS.get(sector, []):
        if trigger in content:
            return True
    return False


def score_news_for_variety(news_list: list[dict], code: str, sector: str) -> dict:
    """返回 {score: -1/0/1, matched: 命中快讯数, positive_hits, negative_hits, evidence: str|None}"""
    keywords = SECTOR_KEYWORDS.get(sector, {"positive": [], "negative": []})
    positive_hits = 0
    negative_hits = 0
    matched = 0
    evidence = None

    for item in news_list:
        content = item.get("content", "")
        if not is_relevant(content, code, sector):
            continue
        matched += 1

        item_pos = [kw for kw in keywords["positive"] if kw in content]
        item_neg = [kw for kw in keywords["negative"] if kw in content]
        positive_hits += len(item_pos)
        negative_hits += len(item_neg)

        if evidence is None and (item_pos or item_neg):
            hit = (item_pos + item_neg)[0]
            evidence = f"快讯提及“{hit}”"

    net = positive_hits - negative_hits
    if net > 0:
        score = 1
    elif net < 0:
        score = -1
    else:
        score = 0

    return {
        "score": score,
        "matched": matched,
        "positive_hits": positive_hits,
        "negative_hits": negative_hits,
        "evidence": evidence,
    }
