"""
趋势分计算 + 综合打分，输出 data/signals.json。

趋势分（-1/0/+1）：综合三个子信号多数表决
  1. MA5 相对 MA20：在上方 +1，在下方 -1，基本重合 0
  2. 最近5日涨跌幅方向：上涨 +1，下跌 -1，基本走平 0
  3. 最近5日持仓量变化方向：增加 +1，减少 -1，基本不变 0
  三者取多数（和的符号），全为0则0

综合标签：趋势分 * 2 + 情绪分，再映射到 偏多/中性/偏空，
趋势权重更高，因为趋势基于价格本身，情绪是辅助判断。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import VARIETIES, DATA_DIR
from sentiment import score_news_for_variety

FLAT_PCT = 0.5  # 涨跌幅/持仓量变化在此百分比以内视为走平


def _direction(pct: float) -> int:
    if pct > FLAT_PCT:
        return 1
    if pct < -FLAT_PCT:
        return -1
    return 0


def compute_trend(quote: dict) -> dict:
    closes = quote["close"]
    holds = quote["hold"]
    if len(closes) < 20:
        return {"score": 0, "reason": "历史数据不足20日，暂不计算趋势", "ma5": None, "ma20": None}

    ma5 = sum(closes[-5:]) / 5
    ma20 = sum(closes[-20:]) / 20
    ma_signal = 1 if ma5 > ma20 else (-1 if ma5 < ma20 else 0)

    chg_pct = (closes[-1] - closes[-6]) / closes[-6] * 100
    chg_signal = _direction(chg_pct)

    hold_pct = (holds[-1] - holds[-6]) / holds[-6] * 100
    hold_signal = _direction(hold_pct)

    total = ma_signal + chg_signal + hold_signal
    trend_score = 1 if total > 0 else (-1 if total < 0 else 0)

    parts = []
    parts.append(f"MA5{'高于' if ma_signal==1 else ('低于' if ma_signal==-1 else '接近')}MA20")
    parts.append(f"近5日涨跌幅{chg_pct:+.1f}%")
    parts.append(f"持仓量变化{hold_pct:+.1f}%")

    return {
        "score": trend_score,
        "reason": "，".join(parts),
        "ma5": round(ma5, 1),
        "ma20": round(ma20, 1),
        "chg_pct": round(chg_pct, 2),
        "hold_pct": round(hold_pct, 2),
    }


def combine_label(trend_score: int, sentiment_score: int) -> str:
    total = trend_score * 2 + sentiment_score
    if total >= 2:
        return "偏多"
    if total <= -2:
        return "偏空"
    return "中性"


def main():
    quotes_path = os.path.join(DATA_DIR, "quotes.json")
    news_path = os.path.join(DATA_DIR, "news.json")

    with open(quotes_path, "r", encoding="utf-8") as f:
        quotes = json.load(f)

    news_list = []
    if os.path.exists(news_path):
        with open(news_path, "r", encoding="utf-8") as f:
            news_list = json.load(f)

    signals = []
    for v in VARIETIES:
        code, name, sector = v["code"], v["name"], v["sector"]
        quote = quotes.get(code)

        if quote is None:
            signals.append({
                "code": code, "name": name, "sector": sector,
                "available": False,
            })
            continue

        trend = compute_trend(quote)
        sentiment = score_news_for_variety(news_list, code, sector)
        label = combine_label(trend["score"], sentiment["score"])

        reason_parts = [trend["reason"]]
        if sentiment["matched"] > 0:
            reason_parts.append(
                f"相关快讯{sentiment['matched']}条，正面{sentiment['positive_hits']}/负面{sentiment['negative_hits']}"
            )
            if sentiment["evidence"]:
                reason_parts.append(sentiment["evidence"])
        else:
            reason_parts.append("暂无相关快讯")

        signals.append({
            "code": code,
            "name": name,
            "sector": sector,
            "available": True,
            "label": label,
            "trend_score": trend["score"],
            "sentiment_score": sentiment["score"],
            "last_close": quote["close"][-1],
            "last_date": quote["dates"][-1],
            "reason": "；".join(reason_parts),
        })
        print(f"[score] {name}({code}) -> {label}")

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "signals.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    print(f"[score] 写入 {out_path}")


if __name__ == "__main__":
    main()
