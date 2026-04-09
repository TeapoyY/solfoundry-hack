# MEMORY.md - 长期记忆

## 经验总结

### Capacitor/Vite 白屏问题 ⚠️
- **原因**: Vite 默认使用绝对路径 `/assets/...`，Capacitor 从文件系统加载时无效
- **解决**: 在 `vite.config.ts` 中添加 `base: './'`
- **验证**: 检查构建输出的 `index.html` 中资源路径是否为 `./assets/...` 而非 `/assets/...`

### APK 签名
- AI Phone Agent keystore: `C:\Users\Administrator\.openclaw\workspace\ai-phone-agent\ai-phone-agent-release.keystore`
- Alias: aiphonagent, Storepass: android123, Keypass: android123
- 签名命令: `jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore <keystore> -storepass <pass> <apk> <alias>`

### 飞书云盘 API 限制
- 文件夹权限设置 API `type=folder` 有诸多限制
- 解决方案: 为每个文件单独设置 `link_share_entity: "anyone_readable"` 公开链接
- APK 下载文件夹 token: `C6lffONgvlxfZRdtZdfcwZCHnQh`

### 任务错误处理原则 ⚠️
- **遇到任务错误时，主动调查原因而不是只汇报错误**
- 检查 cron job 历史、错误日志、进程状态
- 尝试重现问题并修复
- 记录调查过程和解决方案

### 环境安装
- **遇到没有安装的环境时，尝试自行安装** (如 Python, yt-dlp 等)
- Windows 上可用: winget, choco, scoop, npm 等安装工具
- 如果 skill 需要 Python 但没有，可以用 `winget install Python` 安装

### 代理问题
- Clash 代理可能导致 Gateway 断开
- 解决：在 `gateway.cmd` 中添加 `NO_PROXY` 环境变量
- 需绕过: 127.0.0.1, localhost, *.local, feishu-cn, openapi.feishu.cn

### Skills
- ClawHub: `clawhub install <skill>` 
- 遇到 rate limit 等一会再试

## 开发任务规则 ⚠️
**运行开发任务时，使用 Claude Code 进行开发！**
- Skill: `coding-agent` (已安装，支持 Claude Code)
- 命令: `claude --permission-mode bypassPermissions --print 'task'`
- 不要手动编写代码，让 Claude Code 代劳

## Bounty Hunt 规则 ⚠️
**使用 Claude Code + GStack QA 开发！**
1. 找 Bounty: BountyHub.dev / GitHub `💎 bounty` label
2. 认领: `/attempt #ISSUE`
3. 开发: `claude --permission-mode bypassPermissions --print "fix issue"`
4. 测试: 使用 GStack QA skill (`~/.claude/skills/gstack/qa/SKILL.md`)
5. 提交 PR
6. 记录到 `.learnings/bounty-hunt.md`

### ⚠️ 验证规则
- **验证规则: `bounty` 标签 ≠ 真钱！**
  - 必须验证实际金额: GitHub Issue 正文中写明 `$XX` 美元金额
  - 或 verified 可交易的 token (如 FNDRY = SolFoundry 平台币)
  - 很多仓库用 `bounty` 标签做内部积分系统，并非真实现金
- **PR 必须验证**: subagent 报告可能造假！每次用 `gh pr list --author TeapoyY` 核实真实作者

## 运行中的 Subagents
| 名称 | 功能 | 状态 |
|------|------|------|
| app-dev | AI News + WorldPredict 开发 | ✅ |
| stock-monitor | 股票盯盘 (3只股票) | ✅ |
| ai-trader | AI Trader 加密货币交易 | ✅ |
| ai-money-hunter | AI自动赚钱机会探索 | ✅ |

## Cron Jobs
| Job | Schedule | Status |
|-----|----------|--------|
| ai-money-hunter-hourly | every 1h | ✅ |

## AI Money Hunter 分析
### TOP 方向
1. **Voice AI Agent** 🥇 - 语音替身，最后一个未被颠覆的高价值行为（电话）
2. **Computer-Using Agent (CUA)** 🥇 - 自动化电脑操作
3. **MCP 开发者服务** - 2026年的"网站"机会（平台转移红利）
4. **AI 电话助理 (Voice Agent)** ⭐⭐⭐⭐⭐
5. **视频 AI 摘要 + 剪辑** ⭐⭐⭐⭐⭐

### 资源
- GStack (YC创业方法论AI工具): `~/.claude/skills/gstack`
- Skills: `/office-hours`, `/plan-ceo-review`, `/review`, `/qa`, `/ship` 等

## Stock Monitor
- 位置: `C:\Users\Administrator\.openclaw\workspace\scripts\stock_monitor_sina.py`
- 监控股票: 拓维信息(sz002261), 华胜天成(sh600410), 心动公司(hk02400)
- 数据源: 新浪财经API

## GStack (YC创业方法论AI工具)
- **来源**: YC CEO Garry Tan 开源
- **GitHub**: github.com/garrytan/gstack
- **简介**: 将YC千家创业公司验证的思维框架封装为15个专业角色
- **成绩**: 两周 3.3万星，MIT协议开源

## 应用开发

### AI News
- **仓库**: https://github.com/TeapoyY/ai-news (私有)
- **后端**: Python FastAPI, port 8002
- **前端**: React, port 3002
- **状态**: ✅ 运行中

### WorldPredict
- **仓库**: https://github.com/TeapoyY/world-predict (私有)
- **后端**: Python FastAPI, port 8011
- **前端**: React, port 3004
- **状态**: ✅ 运行中

### AI Phone Agent
- **仓库**: https://github.com/TeapoyY/ai-phone-agent
- **最新APK**: ai-phone-agent-v0.8.12-aligned.apk
- **状态**: ✅ 开发中

### FormForge (AI Form Filler)
- **仓库**: https://github.com/TeapoyY/ai-form-filler (私有)
- **后端**: `backend/main.py` (FastAPI, port 8002)
- **前端**: `frontend/` (React + Vite)
- **测试文件**: `backend/test_samples/`
- **技术栈**: PyMuPDF + EasyOCR + Ollama (minicpm-v + gemma3:1b)
- **状态**: ✅ 测试完成

### Parallax Train Widget
- **仓库**: https://github.com/TeapoyY/parallax-train-widget
- **功能**: 视差火车动画 + 番茄钟 + Todo
- **模式**: Normal / Transparent / Desktop (透明嵌入)
- **构建**: `npm run build:portable`, `npm run build:installer`, `npm run build:editable`

## 工具和 Skills

### GitHub
- 安装: `winget install GitHub.cli`
- 认证: `gh auth login`
- Skill: `C:\Users\Administrator\AppData\Roaming\npm\node_modules\openclaw\skills\github\SKILL.md`

### Self-Improving Agent Skill
- 位置: `C:\Users\Administrator\.openclaw\workspace\skills\self-improving-agent`
- Learnings: `C:\Users\Administrator\.openclaw\workspace\.learnings\`
  - `LEARNINGS.md` - 纠正、最佳实践、知识差距
  - `ERRORS.md` - 命令失败、集成错误
  - `FEATURE_REQUESTS.md` - 用户请求的功能

## Hermes Agent (Nous Research) ⚠️ 新发现
- **官网**: https://hermes-agent.nousresearch.com
- **GitHub**: https://github.com/NousResearch/hermes-agent
- **特点**:
  - 自改进AI Agent，内置学习循环
  - 从经验中创建 Skills，使用时自我改进
  - 多平台: Telegram, Discord, Slack, WhatsApp, Signal, CLI
  - 模型无关: OpenRouter (200+), Nous Portal, Kimi, MiniMax, OpenAI 等
  - 内存系统: FTS5会话搜索，LLM摘要，跨会话记忆
  - 计划任务: 内置cron调度器
  - 子Agent: 并行工作流的隔离子Agent
  - Serverless: Daytona和Modal支持，闲置时休眠，几乎零成本
- **安装**: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
- **OpenClaw迁移**: `hermes claw migrate` 可自动导入OpenClaw配置

## 重要提醒
- **在必要时使用 self-improving-agent 的 skill** 来记录学习、错误和修正
- **所有任务执行前**: 先读取 `.learnings/LEARNINGS.md` 和 `.learnings/ERRORS.md` 避免重复错误
- **所有任务执行后**: 记录结果到 `.learnings/` 相应文件

## Claude Code CLI
- `claude --version` 返回 2.1.79
- Claude Code = Developer（执行开发）
- OpenClaw Subagent = Reviewer（审核、验证、循环直到没问题）
- Dev agent timeout: 1小时
