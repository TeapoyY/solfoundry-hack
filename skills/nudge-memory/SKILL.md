# NUDGE-MEMORY SKILL

## 概念
Periodic nudge system that prompts the agent to persist important knowledge learned during the session. Triggered by HEARTBEAT.

## Nudge 触发时机
| 频率 | 触发条件 |
|------|----------|
| 每 30 分钟 | 检查是否需要保存当前会话 |
| 每小时 | 全面检查 MEMORY 使用率 |
| 每天 | 回顾并更新 MEMORY |

## Nudge 类型

### 1. Post-Task Nudge (最紧急)
```
场景: 刚完成复杂任务或修复错误
问题: "你刚才解决了 [问题X]。这经验值得保存到 .learnings/ 吗？"

触发条件:
- 任务涉及错误修复
- 用户纠正了方法
- 发现新的工作区规则
```

### 2. Hourly Memory Check
```
场景: 每小时 HEARTBEAT
检查:
1. MEMORY.md 使用率 > 70%?
   → "MEMORY 使用率已达 75%。是否需要精简？"
2. 过去 1 小时有重要发现?
   → "今天学到了 [X]，要保存吗？"
3. 有未记录的工具/规则?
   → "你用了 [tool]，结果如何？"
```

### 3. Daily Review (早晨)
```
场景: 每天第一次 HEARTBEAT
问题:
- "昨天的关键进展有哪些？"
- "有什么需要更新到 MEMORY.md？"
- "有过时条目需要清理？"
```

## Nudge 实现

### HEARTBEAT 集成
```javascript
// 在 HEARTBEAT.md 的检查列表中添加
const nudgeCheck = () => {
  // 1. 检查 MEMORY 使用率
  const memSize = read("MEMORY.md").length;
  if (memSize > 3200) {
    return "MEMORY 使用率较高: " + Math.round(memSize/4000*100) + "%";
  }
  
  // 2. 检查当前会话是否有值得保存的
  const recentTools = getRecentToolCalls(30); // 最近 30 分钟
  if (recentTools.length > 10) {
    return "近期有复杂任务完成，考虑保存经验？";
  }
  
  // 3. 检查是否有错误修复
  const errors = getRecentErrors();
  if (errors.length > 0 && errors[0].resolved) {
    return "错误已解决，要保存解决方案吗？";
  }
  
  return null; // 无需 nudge
};
```

### Nudge 响应流程
```
收到 Nudge
    ↓
评估是否需要保存
    ↓
需要保存 → 写入适当位置
    ↓
回复 HEARTBEAT_OK
```

## 保存位置决策
| 内容类型 | 目标位置 |
|----------|----------|
| 工具技巧 | TOOLS.md |
| 行为模式 | SOUL.md |
| 工作流改进 | AGENTS.md |
| 普遍教训 | .learnings/LEARNINGS.md |
| 命令错误 | .learnings/ERRORS.md |
| 用户请求 | .learnings/FEATURE_REQUESTS.md |
| 项目状态 | memory/YYYY-MM-DD.md |

## 防打扰设计
- 连续 3 次 nudge 被忽略 → 降低频率
- 用户明确说"不用提醒" → 静默模式
- 凌晨 23:00-07:00 → 不打扰

## 与 Hermes Nudge 对比
| 特性 | Hermes | OpenClaw |
|------|--------|----------|
| 触发 | 周期性 + 事件驱动 | HEARTBEAT 驱动 |
| 持久化 | 直接写 memory | 写文件 + nudge 主会话 |
| 自动化 | 完全自主 | 半自主 (需要主会话确认) |
