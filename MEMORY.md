# MEMORY.md - 长期记忆

## 经验总结

### Capacitor/Vite 白屏问题 ⚠️
- 解决: `vite.config.ts` 中添加 `base: './'`

### APK 签名
- keystore: `ai-phone-agent-release.keystore`, Alias: aiphonagent, Storepass/Keypass: android123
- 签名: `jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore <keystore> -storepass <pass> <apk> <alias>`

### 飞书云盘 API
- 文件夹权限限制: 单独设置 `link_share_entity: "anyone_readable"`
- APK 下载文件夹 token: `C6lffONgvlxfZRdtZdfcwZCHnQh`

### 任务错误处理原则 ⚠️
- 遇到错误主动调查，不只汇报：检查 cron 日志、错误日志、进程状态，尝试重现并修复

### 环境安装
- 遇到未安装环境时尝试自行安装 (winget, choco, scoop, npm); skill 需要 Python 可用 `winget install Python`

### 代理问题
- Clash 可能导致 Gateway 断开: 在 `gateway.cmd` 添加 `NO_PROXY` 绕过 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn

## 开发任务规则 ⚠️
- 使用 Claude Code: `claude --permission-mode bypassPermissions --print 'task'`
- 不要手动编写代码

## Bounty Hunt 规则 ⚠️
1. 找 Bounty: BountyHub.dev / Algora.io / GitHub `💎 bounty` label
2. **验证真钱**: Issue 正文中写明 `$XX` 或 verified token (如 FNDRS); `bounty` 标签 ≠ 真钱
3. Claude Code: `claude --print "implement..."`
4. PR 必须 `gh pr list --author TeapoyY` 核实真实作者

## 运行中的 Subagents
| 名称 | 功能 | 状态 |
|------|------|------|
| app-dev | AI News + WorldPredict 开发 | ✅ |
| stock-monitor | 股票盯盘 (3只股票) | ✅ |
| ai-trader | AI Trader 加密货币交易 | ✅ |
| ai-money-hunter | AI自动赚钱机会探索 | ✅ |

## AI Money Hunter TOP 方向 (YC 六问评分)
1. **AI 法律合同审查** 🥇 - 需求极强 + 付费意愿极高 + 规模独角兽级
2. **AI SMB 客服自动化** 🥈 - Shopify 商家, 极广市场, 2周可MVP
3. **垂直领域 MCP Server** 🥉 - 低执行成本, 平台期占位

**核心洞察:**
- 最佳机会 = "X + AI 最后一公里"，非"AI 新行业定义"
- 套利: 东南亚双语团队服务欧美 Shopify 中国卖家
- EUREKA: AI 降低服务成本 → 需求扩张而非需求破坏
- 资源: GStack `~/.claude/skills/gstack`

## Stock Monitor
- 脚本: `scripts\stock_monitor_sina.py`; 监控: 拓维信息(sz002261), 华胜天成(sh600410), 心动公司(hk02400); 数据源: 新浪财经API

## 应用开发

### AI News / WorldPredict
- AI News: port 8002 (后端), 3002 (前端); WorldPredict: port 8011 (后端), 3004 (前端)

### AI Phone Agent
- 仓库: https://github.com/TeapoyY/ai-phone-agent; 最新APK: ai-phone-agent-v0.8.12-aligned.apk

### FormForge (AI Form Filler)
- 仓库: https://github.com/TeapoyY/ai-form-filler; Stack: FastAPI + PyMuPDF + PaddleOCR/EasyOCR + Ollama (gemma3:1b + minicpm-v); 后端 port 8001
- PRIMARY: 2-step path (OCR + gemma3:1b) ✅ 化学元素全对 + 机械性能完整
- Vision path (minicpm-v): ✅ 12/12 fields stable, issuer cross-validation working
- Regex fallback: 补全被截断的 LLM 输出（Impact Test / Hardness 等）
- OCR engines: PaddleOCR (3.0.0) ✅ WORKING on Windows CPU, EasyOCR fallback
- DISABLE_PADDLEOCR=0 (enabled); DISABLE_EASYOCR=0; OCR_TIMEOUT=180
- Known issues fixed: issuer ' & ' separator (LLM joins two signatories), hardness hallucination, heat_number hallucination
- GitHub push BLOCKED: 7 commits pending (network/proxy issue)
- 启动: `python main.py` from backend dir; server auto-reloads on code changes

### Parallax Train Widget
- 仓库: https://github.com/TeapoyY/parallax-train-widget; 模式: Normal / Transparent / Desktop

## 工具和 Skills
- GitHub CLI: `winget install GitHub.cli` → `gh auth login`; ClawHub: `clawhub install <skill>`
- Learnings 目录: `C:\Users\Administrator\.openclaw\workspace\.learnings\`
- Claude Code CLI: `claude --version` = 2.1.79; Dev agent timeout: 1小时
