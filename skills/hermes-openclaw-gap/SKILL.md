# HERMES-OPENCLAW-GAP-ANALYSIS SKILL

## 概述
本 Skill 分析 Hermes Agent 与 OpenClaw 的功能差距，帮助判断是否需要迁移或如何整合两者优势。

## 版本
- 分析日期: 2026-04-09
- Hermes 版本: latest (Nous Research)
- OpenClaw 版本: latest

---

## 一、核心架构对比

| 维度 | Hermes Agent | OpenClaw | 差距 |
|------|-------------|----------|------|
| **定位** | 自改进 AI Agent | 多平台 Agent 编排层 | 互补 |
| **核心循环** | 内置学习循环 | 依赖 Skills/HEARTBEAT | ⚠️ |
| **Agent 实现** | AIAgent (~9200行 Python) | 会话管理层 | N/A |
| **部署模式** | CLI + Gateway + Serverless | Gateway 守护进程 | ⚠️ |

### Hermes 核心循环
```
任务 → 自我评估 → skill_manage.create() → Skill保存
     → memory consolidation → 记忆精简
     → nudge → 周期性提醒
     → session_search → 会话归档
```

### OpenClaw 现有循环
```
任务 → subagent → sessions_spawn → 结果返回
     → .learnings/ → 错误记录
     → HEARTBEAT → 状态监控
     → skills/ → 人工创建的 Skills
```

---

## 二、功能对比表

### 2.1 Skill 系统

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| Skill 存储 | `~/.hermes/skills/` | `~/.openclaw/skills/` | 无 |
| Skill 创建者 | Agent 自动 (skill_manage) | 人工创建 | ⚠️⚠️ |
| Skill 格式 | SKILL.md + metadata | SKILL.md | ✅ 相似 |
| 渐进披露 | Level 0/1/2 三级 | 全量加载 | ⚠️ |
| Skill Hub | skills.sh, 官方, GitHub | ClawHub | ⚠️ |
| Skill 搜索 | `hermes skills search` | `clawhub search` | ✅ |
| 外部 Skill 目录 | `external_dirs` 配置 | 不支持 | ⚠️ |
| Skill 条件激活 | `fallback_for_toolsets` | 无 | ⚠️ |
| 必需工具集 | `requires_toolsets` | 无 | ⚠️ |

### 2.2 记忆系统

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| 持久记忆 | MEMORY.md (2,200 chars) | MEMORY.md (无硬限制) | ⚠️ |
| 用户画像 | USER.md (1,375 chars) | USER.md (无硬限制) | ⚠️ |
| 记忆注入 | Session 开头自动 | 手动读取 | ⚠️ |
| 记忆上限 | 硬性字符限制 | 无 | ⚠️⚠️ |
| 自动精简 | 80% 时触发 consolidation | 无 | ⚠️⚠️ |
| 会话搜索 | SQLite + FTS5 | sessions_history API | ✅ |
| 外部记忆提供商 | Honcho, Mem0 等 8 种 | 无 | ⚠️ |
| 记忆持久化 | 自动 + 事件驱动 | 手动/HEARTBEAT | ⚠️ |

### 2.3 平台集成

| 平台 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| Telegram | ✅ | ✅ | 无 |
| Discord | ✅ | ✅ | 无 |
| Slack | ✅ | ✅ | 无 |
| WhatsApp | ✅ | ✅ | 无 |
| Signal | ✅ | ❌ | ⚠️ |
| Email | ✅ | ❌ | ⚠️ |
| Feishu | ❌ | ✅ | ⚠️ |
| WeChat | ❌ | ❌ | N/A |
| CLI | ✅ (高级 TUI) | ✅ | ✅ |
| Web | ✅ | ❌ | ⚠️ |

### 2.4 工具系统

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| 工具数量 | 47 工具, 40 toolsets | 取决于配置 | - |
| 终端后端 | 6 种 (local, Docker, SSH, Daytona, Singularity, Modal) | 1 种 (local) | ⚠️⚠️ |
| 浏览器自动化 | 5 种后端 | 无 | ⚠️⚠️ |
| MCP 集成 | ✅ (内置 MCP client) | ✅ (via mcporter skill) | ✅ |
| 子 Agent | delegate_tool | sessions_spawn | ✅ 相似 |
| 代码执行 | execute_code sandbox | 无内置 | ⚠️ |
| 文件操作 | read_file, write_file, patch, search_files | read, write, edit | ✅ |
| Web 搜索 | web_search, web_extract (4 backends) | web_search | ⚠️ |

### 2.5 调度系统

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| Cron 调度 | 内置 | Cron jobs | ✅ 相似 |
| 自然语言配置 | ✅ | ❌ | ⚠️ |
| 平台交付 | 任意平台 | 消息推送 | ✅ |
| 会话创建 | 独立 AIAgent | 新 subagent | ⚠️ |

### 2.6 安全模型

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| 命令审批 | approval.py | gateway 配置 | ✅ 相似 |
| DM 配对 | pairing.py | 配置文件 | ✅ |
| 容器隔离 | ✅ | ❌ | ⚠️ |
| 环境变量传递 | env_passthrough | 无内置 | ⚠️ |
| 安全扫描 | Skill 安全扫描 | 无内置 | ⚠️ |

### 2.7 模型支持

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| OpenRouter | 200+ 模型 | 取决于配置 | - |
| Nous Portal | ✅ | ❌ | ⚠️ |
| Kimi/Moonshot | ✅ | ✅ | 无 |
| MiniMax | ✅ | ✅ | 无 |
| OpenAI | ✅ | ✅ | 无 |
| Anthropic | ✅ | ✅ | 无 |
| 本地模型 | ✅ | ✅ (Ollama) | 无 |
| 模型切换 | `hermes model` | 配置 | ⚠️ |

### 2.8 自改进能力

| 功能 | Hermes | OpenClaw | 差距 |
|------|--------|----------|------|
| 自动 Skill 创建 | ✅ (skill_manage) | ❌ | ⚠️⚠️ |
| 记忆自动精简 | ✅ (80% threshold) | ❌ | ⚠️⚠️ |
| 周期性 Nudge | ✅ | ❌ (HEARTBEAT 不同) | ⚠️ |
| 学习循环 | 闭环 | 开环 | ⚠️ |
| 错误模式检测 | 无 | .learnings/ERRORS | ✅ |

---

## 三、差距优先级

### P0 - 关键差距 (影响核心体验)

1. **Skill 自动创建** - Hermes 可从经验自动生成 Skills，OpenClaw 需人工
2. **有界记忆** - Hermes 强制 2,200/1,375 chars 上限，OpenClaw 无
3. **自动精简** - Hermes 80% 时自动 consolidation，OpenClaw 无

### P1 - 重要差距 (影响工作效率)

4. **终端后端多样性** - Hermes 支持 6 种部署方式，OpenClaw 仅 local
5. **浏览器自动化** - Hermes 有 5 种后端，OpenClaw 无
6. **渐进披露** - Hermes Level 0/1/2 加载，OpenClaw 全量
7. **Feishu 集成** - OpenClaw 有，Hermes 无

### P2 - 次要差距 (影响便利性)

8. **Signal/Email** - Hermes 支持，OpenClaw 不支持
9. **外部记忆提供商** - Hermes 支持 8 种，OpenClaw 无
10. **容器隔离** - Hermes 有，OpenClaw 无
11. **Cron 平台交付** - Hermes 可任意平台，OpenClaw 仅消息

---

## 四、OpenClaw 优势

| 优势 | 说明 |
|------|------|
| **Feishu 集成** | 原生支持飞书，Hermes 无 |
| **Gateway 守护进程** | 稳定的长期运行服务 |
| **HEARTBEAT 系统** | 主动任务监控和提醒 |
| **Subagent 隔离** | sessions_spawn 实现任务隔离 |
| **ClawHub** | Skill 市场 |
| **YC 创业方法论** | GStack 集成 |
| **简单部署** | Windows 原生支持 |

---

## 五、迁移建议

### 场景 1: 纯 OpenClaw 用户 (不迁移)
**判断条件**: 主要使用飞书、已有成熟 Skills

**建议**:
- 采用 Hermes 的 self-improvement loop 设计
- 使用 auto-skill-creator, memory-guardian 等 Skills 补充
- 保持 OpenClaw，利用 ClawHub 扩展

### 场景 2: 考虑迁移到 Hermes
**判断条件**:
- 主要使用 Telegram/Discord/CLI
- 需要自改进能力
- 需要多种终端后端
- 需要 Signal/Email 集成

**迁移步骤**:
```bash
# 1. 安装 Hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 2. 迁移 OpenClaw 数据
hermes claw migrate --dry-run  # 预览
hermes claw migrate             # 执行
```

### 场景 3: 两者并存
**判断条件**:
- 需要飞书 (OpenClaw)
- 也需要 Telegram/CLI (Hermes)
- 需要自改进能力

**建议**:
- OpenClaw: 飞书主对话、长期任务
- Hermes: CLI 开发、自动化任务
- 共享 MEMORY.md: 手动同步关键记忆

---

## 六、OpenClaw 实现 Hermes 核心功能

### 6.1 自动 Skill 创建 (auto-skill-creator)
```
触发: tool_calls >= 5
↓
提取工作流
↓
检查通用性
↓
生成 SKILL.md
↓
保存到 skills/
```

### 6.2 有界记忆 (memory-guardian)
```
硬上限: 4,000 chars (MEMORY), 2,400 chars (USER)
80% 警告
↓
超过 80% → consolidation
↓
合并相似条目
↓
删除过时条目
↓
压缩描述
```

### 6.3 周期性 Nudge (nudge-memory)
```
每小时 HEARTBEAT
↓
检查: 新学到? 错误解决? 用户纠正?
↓
需要保存 → 写入适当文件
↓
返回 HEARTBEAT_OK
```

---

## 七、结论

| 方面 | 评估 |
|------|------|
| **架构完整性** | Hermes 更完整 (内置闭环) |
| **平台集成** | 各有侧重 (Hermes 国际, OpenClaw 中国) |
| **自改进能力** | Hermes 强，OpenClaw 需补充 |
| **易用性** | OpenClaw 更简单 |
| **迁移价值** | 低 (目标不同) |

### 最终建议

**OpenClaw 用户继续使用 OpenClaw**，通过新增 Skills 补充 Hermes 的自改进能力:
- `auto-skill-creator`
- `memory-guardian`
- `nudge-memory`
- `session-archivist`

**只有当**:
- 需要 Signal/Email 集成
- 需要多种终端后端
- 需要完全闭环的自改进

才考虑迁移到 Hermes 或两者并存。
