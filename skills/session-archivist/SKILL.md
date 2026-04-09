# SESSION-ARCHIVIST SKILL

## 概念
Automatic session archiving and searchable history. Enables "did we discuss X last week?" queries.

## 存储结构
```
~/.openclaw/sessions/
├── 2026-04/
│   ├── 2026-04-09-123456.json   # 主会话
│   ├── 2026-04-09-subagent-1.json
│   └── 2026-04-08-ai-money-hunter.json
├── 2026-04/
│   └── ...
└── index.json  # 快速搜索索引
```

## 自动归档规则

### 1. 触发条件
- 主会话每 30 分钟自动保存
- Subagent 会话结束后保存
- 用户明确请求时保存
- 重要决策/教训时立即保存

### 2. Session 内容
```json
{
  "timestamp": "2026-04-09T12:34:56+08:00",
  "session_key": "agent:main:...",
  "channel": "feishu",
  "duration_minutes": 45,
  "summary": "讨论了 Hermes Agent, 清理了 workspace",
  "key_outcomes": [
    "调研了 Hermes Agent 自循环系统",
    "拆解为 4 个 OpenClaw skills",
    "清理了 16 个旧 APK 文件"
  ],
  "decisions": [
    "采用 auto-skill-creator skill 设计"
  ],
  "lessons": [
    "Hermes skill_manage 在复杂任务后触发"
  ],
  "message_count": 24,
  "tools_used": ["sessions_spawn", "read", "write", "exec"]
}
```

### 3. 搜索接口
```
命令: /search-sessions [query]

返回:
- 最相关的 5 个会话
- 每个会话的 summary + timestamp
- 使用 find / grep 实现简单 FTS
```

## 搜索实现
```bash
# 简单全文搜索
cd ~/.openclaw/sessions
grep -r "Hermes" --include="*.json" -l
grep -r "Hermes" --include="*.json" -A2 -B2

# 索引搜索
# index.json 包含每个会话的关键词向量
```

## 与 Hermes Session Search 对比
| Feature | Hermes | OpenClaw (本实现) |
|---------|--------|-------------------|
| 存储 | SQLite + FTS5 | JSON 文件 + grep |
| 搜索 | 原生 SQL FTS | find + grep |
| 摘要 | Gemini Flash | 本地 LLM 调用 |
| 延迟 | 即时 | 按需搜索 |

## 集成 HEARTBEAT
```javascript
// 每小时 HEARTBEAT
if (heartbeat.hour % 1 === 0) {
  archiveCurrentSession();
  cleanupOldSessions(); // 保留最近 90 天
}
```

## 清理规则
- 超过 90 天的会话 → 压缩到 monthly archive
- 超过 180 天的会话 → 删除原文，保留 summary
- 重要会话 (标记了 key_outcomes) → 永久保留
