# HEARTBEAT.md - Active Tasks Monitor
Updated: 2026-04-23 19:05 HKT

## Polymarket Elon Tracker (v3)
- **Repo**: `polymarket-elon-tracker/`
- **入口**: `run_hourly.py` (cron `f5c6ff90`)
- **核心**: `src/full_analyzer.py` — multi-outcome bucket analysis + bidirectional edge
- ⚠️ **2026-04-23 Bug**: `sessionTarget: "main"` + `agentTurn` 不兼容，scheduler 重启后 polymarket job 被 skip
- ✅ **已修复**: jobs.json 中改为 `sessionTarget: "isolated"`，下次 scheduler 加载生效
- 数据源: Polymarket HTML `__NEXT_DATA__` + browser relay fallback

### 当前信号（最后成功运行 10:03 HKT）
- apr17-24: xtrack=93/200, BUY_NO (P_NO=100%, PM YES=85%)
- may2026: xtrack=0/800, BUY_YES (P_YES=100%, PM YES=85%, edge +15%)
- apr14-21: 已过期

## Gateway 崩溃（2026-04-23）
- **崩溃1**: ~10:11 HKT，自动恢复（13:18 HKT）
- **崩溃2**: ~17:02 HKT，手动恢复（18:02 HKT）
- **根因**: Feishu delivery queue 积压 → 投递目标 "heartbeat" user_id 无效 → 163条消息永久失败 → gateway 重试阻塞 → 崩溃
- **处置**: 清空了 delivery queue（493个历史垃圾 + 82个今日失败消息）
- **待办**: 调查 "heartbeat" contact 来源，禁用 bounty-hub-hunter（browser relay 长期断开）

## Bounty Hunt
- **来源**: BountyHub.dev only（Algora 已禁用）
- **Cron**: `bounty-hub-hunter` every 2h（状态: error — browser relay 断开）
- ⚠️ 建议禁用：browser relay 长期不可用，持续产生垃圾投递

## Cron Jobs
| Job | Schedule | Status | 备注 |
|-----|----------|--------|------|
| gateway-keepalive | every 10m | ✅ ok | |
| polymarket-elon-monitor | every 1h | ⚠️ skipped→fixed | 需下次scheduler加载 |
| bounty-hub-hunter | every 2h | ❌ error | 建议禁用 |
| ai-money-hunter-hourly | every 1h | ❌ error | Feishu 400错误 |
| ainews-wp-daily-report | every 1d | ✅ ok | |
| Daily PR Review | every 1d | ❌ error | |
| crypto-daily-check | daily 09:00 | ✅ ok | |

## Service Ports
| Port | Service | Status (2026-04-23) |
|------|---------|---------------------|
| 18789 | OpenClaw Gateway | ✅ Listen |
| 8001 | FormForge backend | ⚠️ DOWN |
| 8002 | AI News backend | ⚠️ DOWN |
| 8003 | LearnAny backend | ⚠️ DOWN |
| 8011 | WorldPredict backend | ⚠️ DOWN |

## Self-Improvement Loop

### 每30分钟:
- [ ] 检查是否需要归档会话 (session-archivist)
- [ ] 检查是否需要创建新 Skill (auto-skill-creator)

### 每小时:
- [ ] MEMORY.md 使用率检查 (>80% → consolidation)

### 每天:
- [ ] 回顾昨天关键事件
- [ ] 清理过时的HEARTBEAT项目
