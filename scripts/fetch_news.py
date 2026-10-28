"""
抓取期货新闻快讯（SHMET，近期滚动窗口，一次约100条/3小时），
与已有 data/news.json 合并去重后保存，让历史快讯随每次 run 累积，
而不是每次都被最新的窗口覆盖掉。
"""
import json
import os
import sys

import akshare as ak

sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_DIR

MAX_KEEP = 2000  # 保留最近的快讯条数上限，避免文件无限增长


def main():
    out_path = os.path.join(DATA_DIR, "news.json")

    existing = []
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    try:
        df = ak.futures_news_shmet(symbol="全部")
    except Exception as e:
        print(f"[fetch_news] 抓取失败: {e}")
        df = None

    fetched = []
    if df is not None and not df.empty:
        for _, row in df.iterrows():
            fetched.append({"time": str(row["发布时间"]), "content": str(row["内容"])})
        print(f"[fetch_news] 本次抓取 {len(fetched)} 条")
    else:
        print("[fetch_news] 本次未抓到新数据，仅保留历史")

    seen = {(item["time"], item["content"]) for item in existing}
    merged = list(existing)
    for item in fetched:
        key = (item["time"], item["content"])
        if key not in seen:
            merged.append(item)
            seen.add(key)

    merged.sort(key=lambda x: x["time"])
    merged = merged[-MAX_KEEP:]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[fetch_news] 合并后共 {len(merged)} 条，写入 {out_path}")


if __name__ == "__main__":
    main()
