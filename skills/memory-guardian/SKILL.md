# MEMORY-GUARDIAN SKILL

## 概念
Bounded memory management with automatic consolidation. Keeps MEMORY.md and USER.md focused and efficient.

## 容量限制
| 文件 | 硬上限 | 建议上限 | 触发精简 |
|------|--------|----------|----------|
| MEMORY.md | 5,000 chars | 4,000 chars (80%) | >3,200 chars |
| USER.md | 3,000 chars | 2,400 chars (80%) | >1,920 chars |

## 自动行为

### 1. 添加前检查
```javascript
beforeAddingToMemory(content) {
  const currentSize = read("MEMORY.md").length;
  const newSize = currentSize + content.length;
  
  if (newSize > 4000) {
    // 触发 consolidation
    consolidateMemory();
    // 重试添加
  }
  
  addMemoryEntry(content);
}
```

### 2. Consolidation 流程
```
触发条件: 使用率 > 80%

步骤:
1. 读取当前所有条目
2. 识别可合并的条目 (相同主题)
3. 识别过时条目 (>30天无更新)
4. 压缩冗余描述
5. 合并为精简版本
6. 保存前验证大小
```

### 3. Entry 格式标准
```
格式: [类别] 描述 | 上下文
分隔符: § (section sign)

示例:
[项目] AI News 在 localhost:8002 运行 § 使用 FastAPI + React
[工具] Claude Code 在 C:\Users\Administrator\AppData\Local\Programs\Claude Desktop 用
[规则] Bounty Hunt 前必须验证真钱 § GitHub Issue 写明 $XX 或 token
```

## Nudge 触发 (HEARTBEAT)

每 2 小时 HEARTBEAT 检查:
1. MEMORY.md 使用率
2. USER.md 使用率  
3. 是否有未保存的重要信息
4. 是否有条目超过 30 天未访问

```javascript
if (heartbeat.hour % 2 === 0) {
  checkMemoryUsage();
  nudgeIfNeeded();
}
```

## 保存规则
| 情况 | 操作 |
|------|------|
| 用户偏好 | → USER.md |
| 环境事实 | → MEMORY.md |
| 纠正/教训 | → MEMORY.md + .learnings/ |
| 大型项目状态 | → 独立文件，MEMORY.md 只存路径 |
| API keys/secrets | → 不存，只存使用方式 |

## 跳过规则
- 明显/琐碎的信息
- 容易重新发现的事实
- 原始数据 dump (日志、代码)
- 会话特定的临时信息
- 已存在于 AGENTS.md/SOUL.md 的内容

## 验证
```javascript
// 保存后验证
const size = read("MEMORY.md").length;
if (size > 5000) {
  throw new Error("MEMORY.md exceeded hard limit!");
}
```
