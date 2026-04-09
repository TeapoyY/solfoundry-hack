# AUTO-SKILL-CREATOR SKILL

## 概念
Monitors task complexity and automatically creates reusable Skills from successful workflows.

## 触发条件
自动检测以下情况并创建 Skill:
1. **复杂任务**: 单次任务使用 5+ tool calls
2. **错误解决**: 遇到错误后找到正确方法
3. **用户纠正**: 用户纠正了 agent 的方法
4. **非平凡工作流**: 发现值得复用的模式

## 自动创建流程

### 1. 监控 (在主会话中)
```
当 tool_calls >= 5 时:
  - 记录任务摘要 (goal, approach, outcome)
  - 记录关键 tool calls 序列
  - 标记为"候选 Skill"
```

### 2. 评估 (任务完成后)
```
候选 Skill 检查:
  - 是否有通用性? (不是纯一次性)
  - 步骤是否可复用?
  - 是否已存在类似 Skill?
  
如果值得创建 → 调用 create-skill-from经验()
```

### 3. 创建 Skill
```javascript
// 使用 sessions_spawn 创建独立 skill 文件
const skillContent = `---
name: auto-generated-[task-type]
description: [一句话描述]
version: 1.0.0
trigger: [什么情况触发]
---

# [Task Name]

## When to Use
[触发条件描述]

## Procedure
[步骤序列，使用实际 tool names]

## Example
[如果适用，添加示例]
`;

write_to_file(`~/.openclaw/skills/auto-created/[skill-name]/SKILL.md`, skillContent);
```

## Skill 注册
```javascript
// 通知 ClawHub 索引新 Skill
exec("clawhub sync"); 
// 或手动添加到已知 skills 列表
```

## 防重复
- 创建前搜索现有 Skills 描述
- 如果高度相似 ( cosine similarity > 0.8 )，则 patch 而非 create
- 同一工作流只创建一次

## 验证
```javascript
// 创建后自动测试
const test_prompt = "触发条件描述";
// 尝试使用新 Skill 执行简单测试
// 成功则保留，失败则 patch 或删除
```
