# MEMORY.md - 长期记忆

## 经验总结
- Python PATH: WindowsApps stub → 用完整路径 `C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe`
- Clash 导致 Gateway 断开: `gateway.cmd` 添加 `NO_PROXY` 绕过 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn
- Capacitor/Vite 白屏: `vite.config.ts` 中添加 `base: './'`
- Claude Code: `claude --version` = 2.1.79; Dev agent timeout: 1小时; 用 `--permission-mode bypassPermissions --print`
- GitHub CLI: `winget install GitHub.cli` + `gh auth login`; ClawHub: `clawhub install <skill>`
- **开发流程**: 每次迭代后必须测试，测试通过再打包 APK

## AI Agent 赚钱机会 (2026-04-19 分析)
- 报告位置: `~/.openclaw/workspace/ai_money_opportunities.md`
- **第一优先级**: 垂直领域 AI SaaS（法律/金融/医疗）— YC 最看好，护城河最深
- **第二优先级**: Claude Code/GPTs 套利 — 门槛低、快速变现、但护城河弱
- **第三优先级**: AI 研究/情报 Agent — 细分数领域存在机会
- **EUREKA**: 法律"第二意见"定位 > "AI替代律师"；PE/VC Pre-DD筛选是金融AI切入点
- **最小Wedge**: 单个垂直 Skill（$5-20购买）→ 法律 Agent 月订阅($500-2000)
- Web Search 不可用(Brave API未配置)，已用 web_fetch + GitHub Trending 替代分析

## AI Trader 状态 (2026-04-17)
- ETH: -$36.91 | BTC: -$354.10 | Total: -$391.01
- 持仓: 1.49 ETH @ 2205, 0.444 BTC @ 71067

## Polymarket Elon Tracker (revised 2026-04-19)
- **系统**: `C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\`
- **Cron**: `f5c6ff90-7ef1-40f6-958e-3a4c1705c644` every 1h; message运行run_hourly.py发送Feishu报告
- **核心文件**:
  - `src/full_analyzer.py` — v2引擎: 多桶概率+bucket combos+双向边缘+Kelly+小时倒计时
  - `run_hourly.py` — 主入口: 分析+生成Feishu消息保存到 output/latest_feishu_msg.txt
  - `fetch_live_counts.py` — 通过browser relay抓Polymarket页面TWEET COUNT
  - `backtest.py` — 日均速率校准
- **数据源**: xtrack权威数据（xtrack.com被封锁，用hardcoded值: apr14-21=184, apr17-24=68, may2026=0）
- **真实日均**: ~30 tweets/day（Polymarket Apr14-19校准）
- **高峰时段UTC**: 22,23,0,1,7,8（late night US + morning US）
- **当前判决** (2026-04-19 15:45 HKT):
  - apr14-21: xtrack=184/190, YES@88%, Edge=+12% → **BUY YES**; combo 240-259+260-279: P=95%, cost=35%, edge=+60%
  - apr17-24: xtrack=68/200, YES@85%, Edge=+15% → **BUY YES**; combo 220-239+240-259: P=87%, cost=34%, edge=+53%
  - may2026: xtrack=0/800, YES@85%, Edge=+15% → **BUY YES**; combo 800-899+900-999: P=99%, cost=29%, edge=+70%
- **Bug修复**: result dict缺少xtrack_confirmed字段 → 已修复; cron timeout问题 → 调查隔离agent启动慢

## 项目
- **FormForge** (port 8001): FastAPI + PyMuPDF + PaddleOCR + Ollama; E2E 12/12 EN10204 ✅; commit aed462e
- **Polymarket Elon Tracker** (`polymarket-elon-tracker/`): xTracker Clone，SQLite + browser CLI采集 + 3情景MC分析
- **Lucky Defense** (`lucky-defense/index.html`): 单文件 HTML5塔防游戏，5 lanes，6 类型，auto-merge
- **LearnAny** (port 8003): ✅ 费曼+苏格拉底学习引擎
- **AI News** (port 8002): ✅ | **WorldPredict** (port 8011): ✅
- **Douyin Game Forge** (port 8010): Claude Code fallback bug; 项目目录已移除

## Polymarket Elon 市场分析 (2026-04-19)
- **日均速率**: ~30 tweets/day（从Polymarket Apr14-19数据校准）
- **xtrack规则**: 主贴+quote posts+reposts计入；纯回复不计入；community reposts不计入
- **xtrack.com封锁**: 用Polymarket market页面的TWEET COUNT字段作为代理
- **bucket combos**: 可以在Polymarket买多个桶，EV = sum(P_i) - sum(price_i)
- **Apr14-21** (目标190): xtrack=184, 只需再发6帖, P(YES)≈100%, YES@88% → edge+12%
- **Apr17-24** (目标200): xtrack=68, 需再发132帖, P(YES)≈100%, YES@85% → edge+15%
- **May2026** (目标800): xtrack=0(未开始), YES@85%, MC P≈100% → edge+15%
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
