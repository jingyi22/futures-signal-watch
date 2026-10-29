"""
抓取外盘实时报价（LME/COMEX/CBOT/马棕油等），输出 data/foreign.json。
只有6个国内品种有对应外盘（见 config.py 的 foreign_symbol），其余为 None，
整体抓取失败时所有品种的外盘数据留空，不中断流程。
"""
import json
import os
import sys

import akshare as ak

sys.path.insert(0, os.path.dirname(__file__))
from config import VARIETIES, DATA_DIR


def main():
    mapped = [v for v in VARIETIES if v["foreign_symbol"]]
    symbols = [v["foreign_symbol"] for v in mapped]

    result = {}
    try:
        df = ak.futures_foreign_commodity_realtime(symbol=symbols)
    except Exception as e:
        print(f"[fetch_foreign] 抓取失败: {e}")
        df = None

    if df is not None and not df.empty and len(df) == len(mapped):
        for v, (_, row) in zip(mapped, df.iterrows()):
            result[v["code"]] = {
                "foreign_name": str(row["名称"]),
                "last_price": float(row["最新价"]),
                "chg_pct": float(row["涨跌幅"]),
            }
            print(f"[fetch_foreign] {v['name']}({v['code']}) -> {row['名称']} {row['最新价']}")
    else:
        print("[fetch_foreign] 返回数据为空或行数不匹配，全部留空")

    for v in VARIETIES:
        if v["code"] not in result:
            result[v["code"]] = None

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "foreign.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[fetch_foreign] 写入 {out_path}")


if __name__ == "__main__":
    main()
