# 跨市场传导雷达

Global Signal -> China A-share Playbook.

这个项目用于在 A 股开盘前，把美股、日股、台股、商品期货等隔夜异动，映射成 A 股 ETF/个股候选，并给出风险过滤与盘中验证条件。

当前版本是 MVP：不依赖外部服务，先用 JSON/CSV 输入跑通核心链路。

## 已实现

- 外盘个股/指数/商品异动识别
- 成交量放大与上涨/下跌方向识别
- 板块共振分数
- 外盘资产 -> 主题 -> A股 ETF/个股池映射
- 历史传导胜率、A股提前反应、高开、拥挤度、大盘环境评分
- 每日 Markdown 报告生成
- 简易隔夜传导回测统计
- 批量隔夜传导回测和边际分排序
- 强信号 / 可观察 / 弱观察 / 风险不追 分层日报
- 跨市场冲击事件生成
- 回测结果写回 `historical_edges`，用于评分反哺
- 收盘复盘模板生成
- 评分规则配置化：`data/scoring_rules.json`
- 输入 JSON schema 校验
- 收盘复盘结果汇总并生成复盘版 `historical_edges`
- 风险规则命中明细：展示是哪条规则扣了多少分
- 盘中验证快照：确认、降级、失败、观察
- 静态 HTML 看板生成
- 公开市场列表爬取与知识图谱扩容

## 快速开始

```powershell
cd D:\Code\Projects\ChengZhang-Master
python -m market_impact_radar report `
  --external data\sample_external_snapshot.json `
  --context data\sample_a_share_context.json `
  --mapping data\mappings.json `
  --scoring-rules data\scoring_rules.json `
  --output outputs\daily_report.md
```

生成的报告会写入：

```text
outputs/daily_report.md
```

也可以直接打印到终端：

```powershell
python -m market_impact_radar report --external data\sample_external_snapshot.json
```

## 扩容知识图谱

当前 `data/mappings.json` 是手工精选 MVP。可以用公开数据源扩容候选池：

```powershell
python -m market_impact_radar crawl-knowledge `
  --mapping data\mappings.json `
  --rules data\theme_rules.json `
  --generated-dir data\generated `
  --output data\mappings.enriched.json
```

如果东方财富接口临时 502 或断连，可以先跳过它，只抓美股、台股和交易所基础列表：

```powershell
python -m market_impact_radar crawl-knowledge `
  --skip-eastmoney `
  --generated-dir data\generated `
  --output data\mappings.enriched.json
```

如果需要走本地代理：

```powershell
python -m market_impact_radar crawl-knowledge `
  --proxy http://127.0.0.1:10793 `
  --generated-dir data\generated `
  --output data\mappings.enriched.json
```

脚本会尽量抓取：

- NasdaqTrader 美股代码目录
- TWSE/TPEx 台湾上市柜公司列表
- 东方财富 A股列表、ETF列表、概念/行业板块和部分板块成分

输出分两层：

- `data/generated/*.json`：原始市场宇宙和关键词匹配候选
- `data/mappings.enriched.json`：把候选合入后的知识图谱

注意：爬虫生成的候选是关键词/板块匹配结果，适合扩容和人工复核，不应直接等同于强交易映射。

## 简易回测

```powershell
python -m market_impact_radar backtest `
  --history data\sample_transmission_history.csv `
  --external-symbol MU `
  --theme 存储芯片 `
  --threshold 5
```

回测口径是：

```text
外盘 T 日涨跌幅 -> A股主题 T+1 日表现
```

## 批量回测

批量统计所有 `外盘代码 -> A股主题` 的隔夜传导表现：

```powershell
python -m market_impact_radar backtest-batch `
  --history data\sample_transmission_history.csv `
  --thresholds 3,5,8 `
  --min-events 3 `
  --output outputs\batch_backtest.md `
  --edges-output data\historical_edges.generated.json
```

也可以输出 CSV：

```powershell
python -m market_impact_radar backtest-batch `
  --history data\sample_transmission_history.csv `
  --thresholds 3,5 `
  --min-events 3 `
  --output outputs\batch_backtest.csv
```

输出指标包括：

- 样本数
- 胜率
- 平均开盘涨幅
- 平均最高涨幅
- 平均收盘涨幅
- 最大回撤
- 高开回落率
- 边际分

生成的 `data\historical_edges.generated.json` 可以在日报里作为历史边际输入：

```powershell
python -m market_impact_radar report `
  --external data\sample_external_snapshot.json `
  --context data\sample_a_share_context.json `
  --historical-edges data\historical_edges.generated.json `
  --output outputs\daily_report.md
```

## 盘中验证

9:25 或开盘 15 分钟后，可以把 ETF 表现、龙头是否回落、板块扩散数量和量能写成盘中快照，再验证早盘信号是否成立：

```powershell
python -m market_impact_radar intraday-validate `
  --external data\sample_external_snapshot.json `
  --context data\sample_a_share_context.json `
  --mapping data\mappings.json `
  --scoring-rules data\scoring_rules.json `
  --intraday data\intraday_snapshot.sample.json `
  --output outputs\intraday_report.md
```

输出会把每个主题标记为：

- `confirmed`：传导被盘中走势确认
- `downgraded`：有反应但追高或风险较大
- `failed`：龙头回落、ETF 下杀或板块没有扩散
- `watch`：继续观察
- `missing`：缺少该主题盘中数据

## HTML 看板

如果想直接给自己看一页更清晰的结果，可以生成静态 HTML：

```powershell
python -m market_impact_radar dashboard `
  --external data\sample_external_snapshot.json `
  --context data\sample_a_share_context.json `
  --mapping data\mappings.json `
  --scoring-rules data\scoring_rules.json `
  --intraday data\intraday_snapshot.sample.json `
  --output outputs\dashboard.html
```

看板包含冲击事件、信号分层、规则命中明细、ETF/个股候选，以及可选的盘中验证结果。

## 收盘复盘模板

每天收盘后可以生成复盘表，用来记录早盘预测是否兑现：

```powershell
python -m market_impact_radar review-template `
  --external data\sample_external_snapshot.json `
  --context data\sample_a_share_context.json `
  --mapping data\mappings.json `
  --scoring-rules data\scoring_rules.json `
  --historical-edges data\historical_edges.generated.json `
  --output outputs\review_template.md
```

填好收盘结果后，可以汇总复盘并生成可反哺评分的边际文件：

```powershell
python -m market_impact_radar review-summarize `
  --review data\review_result.sample.json `
  --output outputs\review_summary.md `
  --edges-output data\review_edges.generated.json
```

## 输入校验

所有关键 JSON 都可以先做 schema 校验：

```powershell
python -m market_impact_radar validate-json `
  --file data\sample_external_snapshot.json `
  --schema external_snapshot.schema.json
```

可用 schema：

- `external_snapshot.schema.json`
- `a_share_context.schema.json`
- `historical_edges.schema.json`
- `review_result.schema.json`
- `scoring_rules.schema.json`
- `intraday_snapshot.schema.json`

如果临时想跳过校验，日报、复盘模板、盘中验证和看板命令支持 `--no-validate`。

## 调整评分规则

风险扣分、分层阈值、历史边际权重都在：

```text
data/scoring_rules.json
```

例如可以直接调：

- `tier_thresholds.strong`
- `risk_rules.auction_open_gap_pct`
- `risk_rules.three_day_change_pct`
- `stock_risk_penalty`
- `historical_edge_score`

## 本地验证

```powershell
python -m compileall -q market_impact_radar
python -m unittest discover -s tests
```

## 数据文件

- `data/mappings.json`：人工精选知识图谱
- `data/theme_rules.json`：爬虫扩容用主题关键词、外盘代码提示、风险规则
- `data/sample_external_snapshot.json`：隔夜外盘快照示例
- `data/sample_a_share_context.json`：A股昨日表现、竞价、大盘环境、历史边际示例
- `data/intraday_snapshot.sample.json`：盘中验证快照示例
- `data/sample_transmission_history.csv`：回测样例

## 后续接入真实数据

MVP 的输入已经抽象成快照格式。真实数据源只需要输出类似结构：

```json
{
  "as_of": "2026-05-14T07:30:00+08:00",
  "assets": [
    {
      "symbol": "MU",
      "change_pct": 8.2,
      "volume_ratio": 2.4,
      "reason_tags": ["industry_price", "ai_demand"],
      "reason_summary": "存储涨价预期与 AI 服务器需求推动"
    }
  ]
}
```

下一阶段建议按这个顺序推进：

1. 接真实行情源，自动生成外盘快照。
2. 接新闻/公告摘要，填充 `reason_tags` 和 `reason_summary`。
3. 沉淀历史行情，自动更新 `historical_edges`。
4. 9:25 后接集合竞价数据，生成盘中验证版报告。
