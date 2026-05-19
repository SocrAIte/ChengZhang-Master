# Legacy Research Utilities

以下模块属于历史遗留或实验性研究工具，不属于默认只读控制台（/console）体验。

## 模块清单

| 模块 | 用途 | 状态 |
|------|------|------|
| `market_impact_radar/backtest.py` | 隔夜传导统计与回测渲染 | Legacy internal |
| `market_impact_radar/review_feedback.py` | 收盘复盘模板渲染（含胜率列） | Legacy internal |
| `market_impact_radar/scoring.py` | 评分引擎（含胜率 reason 文案） | Legacy internal（评分逻辑本身不改动） |
| `data/scoring_rules.json` | 评分规则配置（含涨停/买入等历史口径） | Legacy internal |

## 定位说明

- 这些模块**不构成交易系统**。
- 它们**不应出现在默认 /console 控制台或只读 API 文档的主路径中**。
- 它们**不应作为产品主页（README）的主功能卖点**。
- README "已实现"主能力列表不得把 backtest / 回测 / 胜率作为正向产品能力。
- CLI 子命令 `backtest` 和 `backtest-batch` 仍可运行，但属于 legacy research utilities。
- 本轮不删除这些模块，不改变其业务逻辑。

## 后续方向

如需继续保留这些模块，应：

1. 在文档中明确标注为 legacy / experimental / internal
2. 确保不与默认只读研究体验混淆
3. 考虑迁移到独立的 legacy / experimental 命名空间
