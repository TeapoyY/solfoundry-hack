# MEMORY.md - 长期记忆

## 经验总结
- Python PATH: WindowsApps stub → 用完整路径 `C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe`
- Clash 导致 Gateway 断开: `gateway.cmd` 添加 `NO_PROXY` 绕过 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn
- Capacitor/Vite 白屏: `vite.config.ts` 中添加 `base: './'`
- Claude Code: `claude --version` = 2.1.79; Dev agent timeout: 1小时; 用 `--permission-mode bypassPermissions --print`
- GitHub CLI: `winget install GitHub.cli` + `gh auth login`; ClawHub: `clawhub install <skill>`

## AI Trader 状态 (2026-04-17)
- ETH: -$36.91 | BTC: -$354.10 | Total: -$391.01
- 持仓: 1.49 ETH @ 2205, 0.444 BTC @ 71067

## 项目
- **FormForge** (port 8001): FastAPI + PyMuPDF + PaddleOCR + Ollama; E2E 12/12 EN10204 ✅; Vision endpoint intermittent; PaddleOCR reader per-call fix (commit aed462e)
- **LearnAny** (port 8003): ✅ 费曼+苏格拉底学习引擎
- **Douyin Game Forge** (port 8010): Claude Code fallback bug, Chinese encoding issue
- **AI News** (port 8002): ✅
- **WorldPredict** (port 8011): ✅
- **AI Phone Agent**: APK v0.8.12, no Python backend

## 服务重启记录 (2026-04-17)
- AI News / WorldPredict / LearnAny: 06:54 重启 (ports 8002/8003/8011)
- FormForge: 2026-04-16 22:18 重启

## Bounty Hunt
- 目标: BountyHub.dev / Algora.io; **验证真钱**: Issue 正文写 `$XX`
- 无 open PR (last: #887, #875)

## Cron Jobs
| Job | Schedule | Status |
|-----|----------|--------|
| gateway-keepalive | every 10m | ✅ |
| bounty-hunt-monitor | every 1h | ✅ |
| ai-money-hunter | every 1h | ✅ |

## 应用状态 (2026-04-17)
| Port | Service | Status |
|------|---------|--------|
| 8001 | FormForge | ✅ |
| 8002 | AI News | ✅ (restarted 06:54) |
| 8003 | LearnAny | ✅ (restarted 06:54) |
| 8010 | Douyin Game Forge backend | ✅ |
| 8011 | WorldPredict | ✅ (restarted 06:54) |
| 3000 | Douyin Game Forge frontend | ✅ IPv6 localhost |
