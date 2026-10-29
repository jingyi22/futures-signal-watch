"""
抓取东财全球财经快讯（stock_info_global_em，每次约200条，覆盖美联储/央行/地缘政治等宏观新闻），
与已有 data/macro_news.json 合并去重后保存，累积模式同 fetch_news.py。
"""
import json
import os
import sys

import akshare as ak

sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_DIR

MAX_KEEP = 2000  # 保留最近的快讯条数上限，避免文件无限增长


def main():
    out_path = os.path.join(DATA_DIR, "macro_news.json")

    existing = []
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    try:
        df = ak.stock_info_global_em()
    except Exception as e:
        print(f"[fetch_macro_news] 抓取失败: {e}")
        df = None

    fetched = []
    if df is not None and not df.empty:
        for _, row in df.iterrows():
            fetched.append({
                "time": str(row["发布时间"]),
                "title": str(row["标题"]),
                "content": str(row["摘要"]),
            })
        print(f"[fetch_macro_news] 本次抓取 {len(fetched)} 条")
    else:
        print("[fetch_macro_news] 本次未抓到新数据，仅保留历史")

    seen = {(item["time"], item["title"]) for item in existing}
    merged = list(existing)
    for item in fetched:
        key = (item["time"], item["title"])
        if key not in seen:
            merged.append(item)
            seen.add(key)

    merged.sort(key=lambda x: x["time"])
    merged = merged[-MAX_KEEP:]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"[fetch_macro_news] 合并后共 {len(merged)} 条，写入 {out_path}")


if __name__ == "__main__":
    main()
