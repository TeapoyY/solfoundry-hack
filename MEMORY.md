# MEMORY.md - 长期记忆

## 经验总结

### Capacitor/Vite 白屏问题
- 解决: `vite.config.ts` 中添加 `base: './'`

### APK 签名
- keystore: `ai-phone-agent-release.keystore`, Alias: aiphonagent, Storepass/Keypass: android123

### 飞书云盘 API
- APK 下载文件夹 token: `C6lffONgvlxfZRdtZdfcwZCHnQh`

### 任务错误处理原则 ⚠️
- 遇到错误主动调查，不只汇报：检查 cron 日志、错误日志、进程状态，尝试重现并修复

### 环境安装
- 遇到未安装环境时尝试自行安装 (winget, choco, scoop, npm)

### 代理问题
- Clash 可能导致 Gateway 断开: 在 `gateway.cmd` 添加 `NO_PROXY` 绕过 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn

## 开发任务规则 ⚠️
- 使用 Claude Code: `claude --permission-mode bypassPermissions --print 'task'`
- 不要手动编写代码

## Bounty Hunt 规则 ⚠️
1. 找 Bounty: BountyHub.dev / Algora.io / GitHub `💎 bounty` label
2. **验证真钱**: Issue 正文中写明 `$XX` 或 verified token; `bounty` 标签 ≠ 真钱
3. Claude Code: `claude --print "implement..."`
4. PR 必须 `gh pr list --author TeapoyY` 核实真实作者

### Active PRs
| PR | Repo | Bounty | Status |
|----|------|--------|--------|
| #887 | SolFoundry/solfoundry | T1: countdown + search bar | ✅ OPEN |
| #875 | SolFoundry/solfoundry | T1: Fix GitHub OAuth | ✅ OPEN |

## AI Money Hunter 深度分析 (2026-04-13 更新)
详见: ai_money_opportunities.md

**TOP 3 机会 (更新版):**
1. **AI Phone Agent** 🥇 - $5K-100K/mo (电话自动化，企业10x性价比)
2. **AI 合同审查** 🥈 - $5K-50K/mo (法律行业切入，合规风险低)
3. **Multi-Agent 工作流** 🥉 - $10K-200K/mo (企业AI团队，长期护城河最高)

**关键数据 (OpenAI 2026-04):** 
- 企业收入占比 40%+，年底预计与消费者持平
- Codex 3M 周活，5X 增长
- Multi-agent 已验证落地 (OpenAI 销售团队全自动化)

**EUREKA 更新:**
- Gen1 AI = 内容工具红海，Gen2 AI = 任务执行蓝海
- 企业要"统一AI操作系统层"
- 最容易变现的AI产品 = "AI文书工具"
- 壁垒是 prompt 质量 + 工作流积累，不是数据集

**本周行动:** AI Phone Agent MVP (诊所/餐厅垂直)

## 运行中的 Subagents
| 名称 | 功能 |
|------|------|
| app-dev | AI News + WorldPredict 开发 |
| stock-monitor | 股票盯盘 (拓维信息/华胜天成/心动公司) |
| ai-trader | AI Trader 加密货币交易 |
| ai-money-hunter | AI自动赚钱机会探索 |


## 工具和 Skills
- GitHub CLI: `winget install GitHub.cli` → `gh auth login`; ClawHub: `clawhub install <skill>`
- Learnings 目录: `C:\Users\Administrator\.openclaw\workspace\.learnings\`
- Claude Code CLI: `claude --version` = 2.1.79; Dev agent timeout: 1小时

## 应用开发

### LearnAny (2026-04-12 新建)
- 仓库: https://github.com/TeapoyY/learn-any; FastAPI (port 8003) + 单文件 SPA
- 费曼+苏格拉底 8阶段渐进学习引擎; UI原则: tacit knowledge

### AI News / WorldPredict
- AI News: port 8002/3002; WorldPredict: port 8011/3004

### AI Phone Agent
- 仓库: https://github.com/TeapoyY/ai-phone-agent; APK: ai-phone-agent-v0.8.12-aligned.apk

### FormForge (AI Form Filler)
- 仓库: https://github.com/TeapoyY/ai-form-filler; FastAPI + PaddleOCR/EasyOCR + OpenRouter (gemini-2.5-flash-image); ports 8001+8002
- E2E: 12/12 EN 10204 fields ✅ (2-step + Vision both passing as of 2026-04-13)
- PRIMARY: 2-step path (PyMuPDF text + gemini-2.0-flash via OpenRouter)
- Vision path (gemini-2.5-flash-image): ✅ 12/12 fields stable
- OCR engines: PyMuPDF (text PDFs) ✅ | PaddleOCR: DISABLED on Windows CPU (PIR NotImplementedError) | DeepSeek-OCR: installed 0.3.0 (needs SiliconFlow/DeepSeek API key) | EasyOCR: DISABLED
- ⚠️ Python PATH issue: WindowsApps stub (0 bytes) can shadow real python.exe. _hourly_test.py has PATH fix for Python312/Python311 paths. Use `py` launcher or set PATH explicitly.
- Hourly cron: job id `910ff854-7da2-4cc8-a6f6-407129b3eb17`

### Parallax Train Widget
- 仓库: https://github.com/TeapoyY/parallax-train-widget; 模式: Normal / Transparent / Desktop


