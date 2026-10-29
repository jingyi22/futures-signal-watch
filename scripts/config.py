"""品种配置：代码、中文名、板块、外盘对应代码。所有脚本共享此配置，保持单一来源。"""

# foreign_symbol 用于 ak.futures_foreign_commodity_realtime，取自 ak.futures_hq_subscribe_exchange_symbol()
# 螺纹钢/铁矿石/甲醇/PTA 是内贸定价品种，没有活跃外盘对应盘，foreign_symbol 为 None
VARIETIES = [
    {"code": "RB0", "name": "螺纹钢", "sector": "黑色系",   "foreign_symbol": None},
    {"code": "I0",  "name": "铁矿石", "sector": "黑色系",   "foreign_symbol": None},
    {"code": "M0",  "name": "豆粕",   "sector": "农产品",   "foreign_symbol": "SM"},
    {"code": "C0",  "name": "玉米",   "sector": "农产品",   "foreign_symbol": "C"},
    {"code": "P0",  "name": "棕榈油", "sector": "农产品",   "foreign_symbol": "FCPO"},
    {"code": "CU0", "name": "铜",     "sector": "有色金属", "foreign_symbol": "CAD"},
    {"code": "AU0", "name": "黄金",   "sector": "贵金属",   "foreign_symbol": "GC"},
    {"code": "AG0", "name": "白银",   "sector": "贵金属",   "foreign_symbol": "SI"},
    {"code": "MA0", "name": "甲醇",   "sector": "能化",     "foreign_symbol": None},
    {"code": "TA0", "name": "PTA",    "sector": "能化",     "foreign_symbol": None},
]

DATA_DIR = "data"
