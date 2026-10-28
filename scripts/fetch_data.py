"""
抓取10个品种的日线历史行情（含持仓量），输出 data/quotes.json。
单个品种抓取失败时标记为不可用，不影响其他品种，不中断整体流程。
"""
import json
import os
import sys

import akshare as ak

sys.path.insert(0, os.path.dirname(__file__))
from config import VARIETIES, DATA_DIR


def fetch_one(code: str) -> dict | None:
    try:
        df = ak.futures_zh_daily_sina(symbol=code)
    except Exception as e:
        print(f"[fetch_data] {code} 抓取失败: {e}")
        return None
    if df is None or df.empty:
        print(f"[fetch_data] {code} 返回为空")
        return None
    df = df.sort_values("date")
    recent = df.tail(30)
    return {
        "dates": recent["date"].astype(str).tolist(),
        "close": recent["close"].astype(float).tolist(),
        "volume": recent["volume"].astype(float).tolist(),
        "hold": recent["hold"].astype(float).tolist(),
    }


def main():
    result = {}
    for v in VARIETIES:
        data = fetch_one(v["code"])
        if data is not None:
            result[v["code"]] = data
            print(f"[fetch_data] {v['name']}({v['code']}) OK，{len(data['dates'])}条")
        else:
            result[v["code"]] = None

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "quotes.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[fetch_data] 写入 {out_path}")


if __name__ == "__main__":
    main()
