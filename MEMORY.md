# MEMORY.md - 长期记忆

## 经验总结
- Python PATH: WindowsApps stub → 用完整路径 `C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe`
- Clash 导致 Gateway 断开: `gateway.cmd` 添加 `NO_PROXY` 绕过 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn
- Capacitor/Vite 白屏: `vite.config.ts` 中添加 `base: './'`
- Claude Code: `claude --version` = 2.1.79; Dev agent timeout: 1小时; 用 `--permission-mode bypassPermissions --print`
- GitHub CLI: `winget install GitHub.cli` + `gh auth login`; ClawHub: `clawhub install <skill>`
- **开发流程**: 每次迭代后必须测试，测试通过再打包 APK

## AI Trader 状态 (2026-04-17)
- ETH: -$36.91 | BTC: -$354.10 | Total: -$391.01
- 持仓: 1.49 ETH @ 2205, 0.444 BTC @ 71067

## Polymarket Elon Tracker 🆕
- **系统**: `C:\Users\Administrator\.openclaw\workspace\polymarket-elon-analyzer\`
- **Cron**: `f5c6ff90-7ef1-40f6-958e-3a4c1705c644` (polymarket-elon-monitor) every 1h
- **入口**: `run_monitor.py` (每小时自动运行)
- **核心**: ThresholdEngine + VelocityAnalysis; Kelly criterion + velocity ratio signal
- **策略**: velocity ratio >= 1.5 且价格 < 95% → BET YES
- **限制**: Polymarket API 被防火墙封锁，用 OpenClaw browser 爬取; xtracker.polymarket.com 返回 404
- **信号**: 2个 YES (Apr14-21 116posts 57% @ conf 73.1%, May2026 50% @ conf 81.0%)

## 项目
- **FormForge** (port 8001): FastAPI + PyMuPDF + PaddleOCR + Ollama; E2E 12/12 EN10204 ✅; commit aed462e
- **Polymarket Elon Tracker** (`polymarket-elon-tracker/`): xTracker Clone，SQLite + browser CLI采集 + 3情景MC分析
- **Lucky Defense** (`lucky-defense/index.html`): 单文件 HTML5塔防游戏，5 lanes，6 类型，auto-merge
- **LearnAny** (port 8003): ✅ 费曼+苏格拉底学习引擎
- **AI News** (port 8002): ✅ | **WorldPredict** (port 8011): ✅
- **Douyin Game Forge** (port 8010): Claude Code fallback bug; 项目目录已移除

## Polymarket Elon 市场分析 (2026-04-18)
- **覆盖校正**: 1.909x (xtracker Apr16-18=42 vs BrowserRelay=22)
- **真实日均**: ~57条/天
- **Apr14-21** (目标190): 55条确认，P=96%，边缘+39%，Kelly¼=20% → **强买入信号**
- **Apr17-24** (目标200): 55条确认(部分重叠)，P≈100%，边缘+50% → **强买入信号**
- **May2026** (目标800): P≈100% → **强买入信号**
- **采集方式**: Node.js CLI + `openclaw.mjs browser evaluate` → Chrome Browser Relay Tab

## 服务状态 (2026-04-18)
- 8002/8003/8011: 05:40 批量重启恢复（上次崩溃 ~06:54 yesterday）
- FormForge (8001): down（2026-04-17 22:18 重启）

## Bounty Hunt
- 目标: BountyHub.dev / Algora.io; **验证真钱**: Issue 正文写 `$XX`
- 无 open PR (last: #887, #875)

## Cron Jobs
| Job | Schedule | Status |
|-----|----------|--------|
| gateway-keepalive | every 10m | ✅ |
| bounty-hunt-monitor | every 1h | ✅ |
| ai-money-hunter | every 1h | ✅ |

## ClawColony
- pendingVotes: 1; enrolledProposals: [539, 540]; lastVote: #541 (yes, 2026-03-19)
