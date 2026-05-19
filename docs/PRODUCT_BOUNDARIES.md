# 产品边界

## 定位

跨市场传导雷达（Market Impact Radar）是一个**只读研究型分析网站**，用于帮助用户理解美股、日股、台股、商品期货等海外异动如何可能传导到 A 股主题。

核心价值是：更快地获取跨市场热点的证据链、观察池、风险提示和数据可信度，辅助研究判断。

## 默认体验包含

- 海外异动识别与 A 股主题映射
- ETF / 个股观察池（observation candidates）
- 信号证据链（external triggers, mapping reason, transmission logic）
- 风险提示（risk level, caution notes）
- 数据质量与来源可信度（data quality, source coverage, fetched_at freshness）
- 历史观察趋势（historical theme trends, recurring candidates）
- 跨日期变化对比（date-over-date changes）
- 研究摘要生成（daily research brief, morning brief）
- 只读控制台（/console）与只读 API

## 明确不是

- **不是交易系统**：不提供下单、持仓管理、账户接口
- **不是荐股系统**：不提供买入、卖出建议或 target price
- **不是收益回测系统**：不提供 win rate、profit、alpha 等收益指标作为产品功能
- **不是自动交易系统**：不执行任何交易操作
- **不是确定性预测系统**：所有信号均为观察线索，需要用户自行判断

## 表达规范

默认用户可见界面和文档中：

- 使用 "observation candidates"（观察池），不使用 "buy list"
- 使用 "signal score"（信号分数），不使用 "expected return"
- 使用 "watch theme"（观察主题），不使用 "recommended sector"
- 使用 "research brief"（研究摘要），不使用 "trading plan"
- 使用 "data quality"（数据质量），不使用 "prediction accuracy"
- 使用 "signal score delta"（信号分数变化），不使用 "profit/loss"
- 使用 "requires confirmation"（需要确认），不使用 "guaranteed"

## 遗留模块

仓库中存在部分历史遗留模块（如 backtest.py、review_feedback.py、scoring.py），它们属于 legacy internal research utilities，不在默认只读控制台体验中。详见 [LEGACY_RESEARCH_UTILITIES.md](LEGACY_RESEARCH_UTILITIES.md)。

## README 主路径规范

- README 默认入口和"已实现"主能力列表不得把 legacy backtest / 回测 / 胜率作为当前正向产品能力。
- backtest / 回测 / 胜率等历史口径只能出现在 Legacy Research Utility 小节，并明确标注不属于默认只读研究控制台。
- README 第一屏应明显表明这是只读研究型分析网站，不是交易系统。
