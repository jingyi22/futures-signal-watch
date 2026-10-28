# 期货行情信号参考（futures-signal-watch）

每个交易日自动抓取国内期货10个主流品种的行情数据和新闻快讯，基于**趋势+情绪规则打分**生成"偏多 / 中性 / 偏空"方向性标签，通过 GitHub Actions 定时更新，GitHub Pages 免费托管。

在线页面：`https://<your-github-username>.github.io/futures-signal-watch/`

## 覆盖品种

螺纹钢、铁矿石、豆粕、玉米、棕榈油、铜、黄金、白银、甲醇、PTA（黑色系/农产品/有色/贵金属/能化各板块代表品种）。

## 方法说明

- **趋势分**：基于 MA5/MA20 相对位置、近期涨跌幅方向、持仓量变化方向，综合给出 -1/0/+1
- **情绪分**：从期货新闻快讯中用关键词词典做正负面计数，按品种/板块关键词匹配相关快讯，综合给出 -1/0/+1
- **综合标签**：趋势分和情绪分加权合并为"偏多/中性/偏空"，附带一句话依据说明

## 风险声明

⚠️ 期货为高风险杠杆交易，多数散户长期亏损，不存在稳赚不赔的策略。本站内容基于公开数据和规则化方法自动生成，**不针对任何品种给出具体买卖点位，不对任何交易结果做出收益承诺**，仅为投资知识科普参考，不构成任何形式的投资建议。市场有风险，入市需谨慎。

## 数据来源

- 行情：新浪财经期货数据（通过 [akshare](https://github.com/akfamily/akshare) 封装）
- 新闻：上海有色网（SHMET）期货快讯（通过 akshare 封装）

## 本地运行

```bash
pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/fetch_news.py
python scripts/score.py
python scripts/build_site.py
```
