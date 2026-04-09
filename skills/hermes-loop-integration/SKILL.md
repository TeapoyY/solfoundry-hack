# HERMES-LOOP-INTEGRATION SKILL

## 概念
Ties together the self-improvement components into a cohesive loop. Activates after complex sessions.

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Self-Improvement Loop                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Session Ends] → [Session-Archivist] → [归档会话]            │
│         ↓                                                    │
│  [复杂任务?] → [Auto-Skill-Creator] → [创建/更新 Skill]      │
│         ↓                                                    │
│  [Memory Check] → [Memory-Guardian] → [ Consolidation]       │
│         ↓                                                    │
│  [Periodic] → [Nudge-Memory] → [Persists Knowledge]         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 激活条件
```
在以下情况下触发完整循环:
1. 用户明确请求 "review and improve"
2. HEARTBEAT 检测到复杂会话 (>10 tool calls)
3. 手动触发 /self-improve
```

## 执行步骤

### Step 1: Session Review (session-archivist)
```javascript
// 归档当前会话
const session_data = {
  timestamp: new Date().toISOString(),
  duration: minutesSinceSessionStart,
  tool_calls: countToolCalls(),
  outcomes: getKeyOutcomes(),
  errors: getResolvedErrors(),
  lessons: getLessonsLearned()
};

archiveSession(session_data);
```

### Step 2: Skill Creation Check (auto-skill-creator)
```javascript
// 检查是否需要创建新 Skill
if (session_data.tool_calls >= 5) {
  const workflow = extractWorkflow(session_data);
  if (isGeneralizable(workflow)) {
    createSkill(workflow);
  }
}
```

### Step 3: Memory Consolidation (memory-guardian)
```javascript
// 检查并维护容量
const memSize = read("MEMORY.md").length;
if (memSize > 3200) {
  consolidateMemoryEntries();
}

// 检查是否有新内容需要添加
const newInfo = extractNewInfo(session_data);
if (newInfo.length > 0) {
  addMemoryEntry(newInfo);
}
```

### Step 4: Knowledge Persistence (nudge-memory)
```javascript
// 确保重要知识已保存
const importantLearnings = extractImportantLearnings(session_data);
for (const learning of importantLearnings) {
  persistToAppropriateFile(learning);
}
```

## 与 OpenClaw 的集成点

| Hermes 组件 | OpenClaw 现有 | 差距 |
|-------------|---------------|------|
| skill_manage tool | ClawHub / skills/ | 需实现自动创建 |
| memory tool | MEMORY.md, USER.md | 需实现 bounded + consolidation |
| session_search | sessions_history API | 需实现持久化 + 搜索 |
| nudge system | HEARTBEAT.md | 需实现周期性检查 |

## 使用方式
```
用户: "/self-improve"
→ 触发本 Skill
→ 自动执行 Step 1-4
→ 报告所有变更
```

## 自动触发配置
```javascript
// 在 AGENTS.md 中配置
self_improve: {
  auto_trigger: true,
  min_tool_calls: 10,
  after_hours: false,
  frequency: "post_session"
}
```
