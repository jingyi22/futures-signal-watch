"""读 data/signals.json，渲染成 docs/index.html（纯字符串模板，无前端框架/构建步骤）。"""
import html
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_DIR

LABEL_CLASS = {"偏多": "bull", "中性": "neutral", "偏空": "bear"}

CARD_TEMPLATE = """
<div class="card {cls}">
  <div class="card-head">
    <span class="name">{name}</span>
    <span class="sector">{sector}</span>
    <span class="label {cls}">{label}</span>
  </div>
  <div class="price">最新收盘：{last_close} （{last_date}）</div>
  <div class="reason">{reason}</div>
</div>
"""

UNAVAILABLE_TEMPLATE = """
<div class="card unavailable">
  <div class="card-head">
    <span class="name">{name}</span>
    <span class="sector">{sector}</span>
    <span class="label unavailable">数据暂不可用</span>
  </div>
  <div class="reason">本次未能成功抓取该品种行情，已跳过，不影响其他品种展示。</div>
</div>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>期货行情信号参考</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <h1>期货行情信号参考</h1>
  <p class="updated">数据更新时间：{updated_at}</p>
</header>

<main>
  <div class="grid">
    {cards}
  </div>
</main>

<footer>
  <p class="warn">
    ⚠️ 期货为高风险杠杆交易，多数散户长期亏损，不存在稳赚不赔的策略。本站内容基于公开数据和规则化方法自动生成，
    <strong>不针对任何品种给出具体买卖点位，不对任何交易结果做出收益承诺</strong>，
    仅为投资知识科普参考，不构成任何形式的投资建议。市场有风险，入市需谨慎。
  </p>
  <p class="method">
    方法说明：标签综合"趋势分"（MA5/MA20相对位置、近5日涨跌幅方向、持仓量变化方向）
    和"情绪分"（新闻快讯关键词正负面计数）规则打分得出，趋势权重更高，仅为方向性参考，不构成交易建议。
  </p>
  <p class="source">
    数据来源：新浪财经期货行情、上海有色网（SHMET）期货快讯，经 <a href="https://github.com/akfamily/akshare" target="_blank">akshare</a> 封装获取。
  </p>
</footer>
</body>
</html>
"""


def render_card(signal: dict) -> str:
    if not signal.get("available"):
        return UNAVAILABLE_TEMPLATE.format(
            name=html.escape(signal["name"]), sector=html.escape(signal["sector"])
        )
    cls = LABEL_CLASS.get(signal["label"], "neutral")
    return CARD_TEMPLATE.format(
        cls=cls,
        name=html.escape(signal["name"]),
        sector=html.escape(signal["sector"]),
        label=html.escape(signal["label"]),
        last_close=signal["last_close"],
        last_date=html.escape(signal["last_date"]),
        reason=html.escape(signal["reason"]),
    )


def main():
    signals_path = os.path.join(DATA_DIR, "signals.json")
    with open(signals_path, "r", encoding="utf-8") as f:
        signals = json.load(f)

    cards_html = "\n".join(render_card(s) for s in signals)
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    page = PAGE_TEMPLATE.format(cards=cards_html, updated_at=updated_at)

    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[build_site] 写入 {out_path}")


if __name__ == "__main__":
    main()
