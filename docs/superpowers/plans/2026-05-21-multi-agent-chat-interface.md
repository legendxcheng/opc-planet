---
title: 多 Agent 聊天界面设计与实现计划
type: plan
status: draft
tags: [agent, ui, chat, multi-agent]
created: 2026-05-21
---

# 多 Agent 聊天界面设计与实现计划

## 背景

当前 OPC Planet 已经具备：
- ✅ better-auth 用户认证
- ✅ 多线程对话管理（chat_threads, chat_messages）
- ✅ Knowledge Gateway 和 metadata 层
- ✅ 基础的 agent/corpus 数据模型

但是前端界面还是单一 Agent 的体验。用户需要能够：
1. 在多个 Agent 之间切换
2. 每个 Agent 维护独立的对话历史
3. 清晰地看到当前使用的是哪个 Agent
4. 方便地管理不同 Agent 的对话

参考 MetaWise.OS 的设计，我们需要实现一个多 Agent 聊天界面。

## 目标

### 前端交互设计（详细）
1. 设计清晰的 Agent 选择和切换界面
2. 设计 Agent 特定的对话历史管理
3. 设计 Agent 信息展示和配置入口
4. 保持良好的用户体验和视觉一致性

### 后端支持（初步规划）
1. 扩展现有的 metadata 层支持多 Agent
2. 调整 API 接口支持 Agent 切换
3. 确保对话历史按 Agent 隔离
4. 为未来的 Agent 配置预留扩展点

## 前端交互设计

### 1. 整体布局结构

```
┌─────────────────────────────────────────────────────────────┐
│  Header (Logo, User Menu)                                    │
├──────────┬──────────────────────────────────┬───────────────┤
│          │                                  │               │
│  Agent   │     Chat Area                    │   History     │
│  List    │                                  │   Panel       │
│          │  ┌────────────────────────────┐  │   (可折叠)    │
│  • Agent1│  │  Agent Info Bar            │  │               │
│  • Agent2│  ├────────────────────────────┤  │  Filter:      │
│  • Agent3│  │                            │  │  □ All        │
│          │  │  Message Thread            │  │  ☑ Agent1     │
│          │  │                            │  │  □ Agent2     │
│          │  │                            │  │               │
│          │  └────────────────────────────┘  │  Threads:     │
│          │  ┌────────────────────────────┐  │  • Thread 1   │
│          │  │  Input Area                │  │  • Thread 2   │
│          │  └────────────────────────────┘  │  • Thread 3   │
│          │                                  │               │
└──────────┴──────────────────────────────────┴───────────────┘
```

### 2. Agent 列表设计（左侧边栏）

**展示形式：分组列表 + 卡片混合模式**

```
┌─────────────────────┐
│  🔍 搜索 Agent       │
├─────────────────────┤
│  📌 常用 (Pinned)    │
│  ┌─────────────────┐│
│  │ 🤖 OPC 助手     ││  ← 卡片式
│  │ 在线 · 2 条未读  ││     头像+名称+状态
│  └─────────────────┘│
│                     │
│  📂 内容创作         │  ← 分类折叠
│  ┌─────────────────┐│
│  │ ✍️ 文案专家     ││
│  │ 活跃 · 5 条历史  ││
│  └─────────────────┘│
│                     │
│  📂 数据分析         │
│  📂 商业智库         │
│                     │
│  ➕ 发现更多 Agent   │
└─────────────────────┘
```

**Agent 卡片包含：**
- 头像/图标（32x32px）
- 名称（最多 2 行）
- 状态指示器（在线/活跃/空闲）
- 未读消息数（红色徽章）
- 最后活动时间
- 快捷操作（hover 显示）

### 3. Chat Area 设计（中间对话区）

**Agent 信息卡片（顶部固定，可折叠）：**
```
┌──────────────────────────────────────────────────────┐
│  🤖 OPC 助手 - 战略咨询                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  💡 当前能力: 战略分析、定价咨询、市场洞察            │
│  📊 今日使用: 12 次对话 · 平均响应 2.3s               │
│                                                      │
│  [新建对话] [查看能力详情] [⚙️ 设置]                  │
└──────────────────────────────────────────────────────┘
```

**消息流区域：**
- 按时间分组（今天、昨天、本周）
- Agent 消息：左对齐，浅灰背景，支持 Markdown
- 用户消息：右对齐，蓝色背景
- 系统提示：居中显示
- 加载状态：打字机效果

**输入区域（底部固定）：**
```
┌──────────────────────────────────────────────────────┐
│  📎 [附件] 💬 [提示词库] 🎤 [语音输入]                │
│  ┌────────────────────────────────────────────────┐ │
│  │ 输入消息...                                     │ │
│  └────────────────────────────────────────────────┘ │
│  Shift+Enter 换行 · Enter 发送          [🚀 发送]   │
└──────────────────────────────────────────────────────┘
```

### 4. History Panel 设计（右侧历史面板）

**筛选器区域：**
```
┌─────────────────────┐
│  📜 对话历史         │
├─────────────────────┤
│  🔍 搜索历史...      │
│                     │
│  筛选:              │
│  [全部 Agent ▾]     │
│  [最近 7 天 ▾]      │
│                     │
│  排序: [最新优先 ▾] │
└─────────────────────┘
```

**线程列表：**
```
┌─────────────────────┐
│  今天                │
│  ┌─────────────────┐│
│  │ 🤖 OPC 助手     ││
│  │ 如何制定定价策略...││
│  │ 5 条消息 · 10分钟前││
│  └─────────────────┘│
│                     │
│  昨天                │
│  ┌─────────────────┐│
│  │ ✍️ 文案专家     ││
│  │ 小红书文案优化... ││
│  │ 8 条消息 · 昨天  ││
│  └─────────────────┘│
└─────────────────────┘
```

### 5. Agent 切换交互流程

**场景 1: 当前对话为空**
```
用户点击 Agent B
  ↓
立即切换到 Agent B
  ↓
显示欢迎消息 + 能力介绍
  ↓
准备新对话
```

**场景 2: 当前对话有内容但未保存**
```
用户点击 Agent B
  ↓
弹出确认对话框:
  "当前对话尚未保存，是否切换？"
  [保存并切换] [直接切换] [取消]
  ↓
根据选择执行操作
```

**场景 3: 当前对话已保存**
```
用户点击 Agent B
  ↓
自动保存当前状态
  ↓
切换到 Agent B
  ↓
加载 Agent B 的最近对话或新建对话
```

### 6. URL 路由设计

```
/chat                          → 默认 Agent + 新对话
/chat/[agentId]               → 指定 Agent + 新对话
/chat/[agentId]/[threadId]    → 指定 Agent + 指定线程
```

**示例：**
- `/chat/opc-assistant` → OPC 助手的新对话
- `/chat/opc-assistant/thread-123` → OPC 助手的历史对话 123

### 7. 响应式设计

**移动端 (< 768px):**
- 全屏 Chat Area
- 汉堡菜单打开 Agent 列表（左侧抽屉）
- 更多按钮打开历史记录（右侧抽屉）

**平板端 (768px - 1024px):**
- Agent Sidebar (180px) + Chat Area
- History Panel 通过按钮切换（覆盖层）

**桌面端 (> 1024px):**
- 完整三栏布局
- Agent Sidebar (240px) + Chat Area + History Panel (320px)

### 8. React 组件结构

```
app/chat/layout.tsx
└── ChatLayout
    ├── ChatHeader
    │   ├── UserMenu
    │   └── GlobalSearch
    │
    ├── AgentSidebar
    │   ├── AgentSearchBar
    │   ├── AgentList
    │   │   └── AgentCard
    │   └── DiscoverAgents
    │
    ├── ChatArea
    │   ├── AgentInfoCard
    │   ├── MessageList
    │   │   └── Message
    │   └── MessageInput
    │
    └── HistoryPanel
        ├── HistoryFilters
        └── ThreadList
            └── ThreadCard
```

### 9. 状态管理

**URL 状态（Next.js App Router）：**
- `agentId`: 当前 Agent ID
- `threadId`: 当前线程 ID

**Server State（SWR/React Query）：**
- Agent 列表
- 线程列表
- 消息列表

**Client State（Zustand/Context）：**
- UI 折叠状态
- 输入框内容
- 临时数据

## 后端规划

### 1. 数据模型扩展

当前已有的表：
- ✅ `agents` - Agent 元数据
- ✅ `corpora` - 知识库
- ✅ `agent_corpora` - Agent 与知识库关联
- ✅ `users` - 用户
- ✅ `chat_threads` - 对话线程
- ✅ `chat_messages` - 消息

需要扩展的字段：

**agents 表扩展：**
```sql
ALTER TABLE agents ADD COLUMN IF NOT EXISTS category TEXT; -- 分类（内容创作、数据分析等）
ALTER TABLE agents ADD COLUMN IF NOT EXISTS icon TEXT; -- 图标/emoji
ALTER TABLE agents ADD COLUMN IF NOT EXISTS color TEXT; -- 主题色
ALTER TABLE agents ADD COLUMN IF NOT EXISTS capabilities TEXT; -- 能力描述（JSON）
ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE; -- 是否置顶
ALTER TABLE agents ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0; -- 排序
```

**chat_threads 表扩展：**
```sql
ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS agent_id TEXT NOT NULL; -- 关联的 Agent
ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS title TEXT; -- 对话标题
ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP; -- 最后消息时间
ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0; -- 消息数量
ALTER TABLE chat_threads ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE; -- 是否归档
```

### 2. API 接口设计

**Agent 相关：**
```
GET  /api/agents                    - 获取 Agent 列表
GET  /api/agents/:agentId           - 获取 Agent 详情
POST /api/agents/:agentId/pin       - 置顶/取消置顶 Agent
```

**Thread 相关（扩展现有接口）：**
```
GET  /api/chat/threads              - 获取线程列表（支持 agentId 筛选）
GET  /api/chat/threads/:threadId    - 获取线程详情
POST /api/chat/threads              - 创建新线程（需要 agentId）
PATCH /api/chat/threads/:threadId   - 更新线程（标题、归档状态）
DELETE /api/chat/threads/:threadId  - 删除线程
```

**Chat 相关（调整现有接口）：**
```
POST /api/chat                      - 发送消息（需要 agentId 和 threadId）
```

### 3. 后端服务层调整

**AgentService（新增）：**
```typescript
class AgentService {
  async listAgents(userId: string): Promise<Agent[]>
  async getAgent(agentId: string): Promise<Agent>
  async pinAgent(userId: string, agentId: string): Promise<void>
  async unpinAgent(userId: string, agentId: string): Promise<void>
}
```

**ThreadService（扩展）：**
```typescript
class ThreadService {
  // 现有方法
  async createThread(userId: string, agentId: string): Promise<Thread>
  async getThread(threadId: string, userId: string): Promise<Thread>
  async listThreads(userId: string, filters?: ThreadFilters): Promise<Thread[]>
  
  // 新增方法
  async updateThreadTitle(threadId: string, title: string): Promise<void>
  async archiveThread(threadId: string): Promise<void>
  async deleteThread(threadId: string): Promise<void>
  async getThreadsByAgent(userId: string, agentId: string): Promise<Thread[]>
}
```

**ChatService（调整）：**
```typescript
class ChatService {
  // 调整现有方法，确保传入 agentId
  async sendMessage(
    userId: string,
    agentId: string,
    threadId: string,
    message: string
  ): Promise<Message>
}
```

### 4. 权限控制

**Agent 访问权限：**
- 所有认证用户可以访问所有 Agent
- 未来可扩展：VIP Agent、私有 Agent

**Thread 访问权限：**
- 用户只能访问自己创建的 Thread
- Thread 必须属于指定的 Agent

**消息访问权限：**
- 用户只能访问自己 Thread 中的消息

### 5. 数据库查询优化

**索引建议：**
```sql
-- agents 表
CREATE INDEX IF NOT EXISTS idx_agents_category ON agents(category);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- chat_threads 表
CREATE INDEX IF NOT EXISTS idx_threads_user_agent ON chat_threads(user_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_threads_last_message ON chat_threads(last_message_at DESC);
CREATE INDEX IF NOT EXISTS idx_threads_archived ON chat_threads(is_archived);

-- chat_messages 表
CREATE INDEX IF NOT EXISTS idx_messages_thread ON chat_messages(thread_id, created_at);
```

### 6. 实时更新策略

**轮询方案（MVP）：**
- 前端每 30 秒轮询线程列表
- 检查 `last_message_at` 是否有更新

**WebSocket 方案（未来）：**
- 实时推送新消息
- 实时更新线程状态
- 多设备同步

### 7. 缓存策略

**Agent 列表：**
- 服务端缓存 5 分钟
- 客户端 SWR 缓存

**Thread 列表：**
- 服务端不缓存（实时性要求高）
- 客户端 SWR 缓存 30 秒

**消息列表：**
- 服务端不缓存
- 客户端缓存直到手动刷新

## 实现计划

### Phase 1: 数据层准备（1-2 天）

**任务：**
1. 扩展 `agents` 表字段（category, icon, color, capabilities）
2. 扩展 `chat_threads` 表字段（agent_id, title, last_message_at）
3. 更新 metadata seed 数据，添加多个 Agent
4. 创建数据库索引
5. 编写数据迁移脚本

**验收标准：**
- 数据库 schema 更新完成
- 至少有 3 个不同类型的 Agent seed 数据
- 所有索引创建成功

### Phase 2: 后端 API 实现（2-3 天）

**任务：**
1. 实现 AgentService
2. 扩展 ThreadService（标题、归档、删除）
3. 调整 ChatService（支持 agentId）
4. 实现 Agent 相关 API 路由
5. 调整 Thread 相关 API 路由
6. 添加权限校验
7. 编写单元测试

**验收标准：**
- 所有 API 接口通过 Postman/curl 测试
- 权限校验正常工作
- 单元测试覆盖核心逻辑

### Phase 3: 前端组件开发（3-4 天）

**任务：**
1. 创建 ChatLayout 组件
2. 实现 AgentSidebar 组件
   - AgentList
   - AgentCard
   - AgentSearchBar
3. 调整 ChatArea 组件
   - 添加 AgentInfoCard
   - 保持现有 MessageList 和 MessageInput
4. 实现 HistoryPanel 组件
   - HistoryFilters
   - ThreadList
   - ThreadCard
5. 实现状态管理（Zustand store）
6. 实现 URL 路由同步

**验收标准：**
- 三栏布局正常显示
- Agent 切换功能正常
- 历史记录筛选正常
- URL 路由同步正常

### Phase 4: 交互优化（2-3 天）

**任务：**
1. 实现响应式设计（移动端适配）
2. 添加加载状态和错误处理
3. 实现 Agent 切换确认对话框
4. 添加快捷键支持
5. 优化动画和过渡效果
6. 添加空状态提示

**验收标准：**
- 移动端体验良好
- 所有交互流程顺畅
- 错误提示清晰
- 性能良好（无明显卡顿）

### Phase 5: 测试和优化（1-2 天）

**任务：**
1. 端到端测试
2. 性能优化（虚拟滚动、懒加载）
3. 可访问性测试
4. 浏览器兼容性测试
5. 修复发现的 bug

**验收标准：**
- 所有核心功能正常工作
- 性能指标达标
- 无严重 bug

## 技术风险和缓解措施

### 风险 1: 状态同步复杂度

**风险：** URL、Server State、Client State 三层状态同步可能出现不一致

**缓解：**
- 使用 URL 作为单一真实来源
- Server State 通过 SWR 自动同步
- Client State 仅用于 UI 临时状态

### 风险 2: 性能问题

**风险：** 大量历史线程和消息可能导致性能下降

**缓解：**
- 实现虚拟滚动
- 分页加载历史记录
- 懒加载非可见内容

### 风险 3: 移动端体验

**风险：** 三栏布局在移动端难以适配

**缓解：**
- 采用抽屉式设计
- 优先显示 Chat Area
- 手势支持（左滑/右滑）

### 风险 4: Agent 切换时的状态丢失

**风险：** 切换 Agent 时可能丢失未保存的输入

**缓解：**
- 实现输入框内容的本地存储
- 切换前弹出确认对话框
- 提供"保存草稿"功能

## 成功指标

### 用户体验指标
- Agent 切换响应时间 < 500ms
- 历史记录加载时间 < 1s
- 消息发送响应时间 < 2s
- 移动端首屏加载时间 < 3s

### 功能完整性指标
- 支持至少 3 个不同类型的 Agent
- 支持按 Agent 筛选历史记录
- 支持线程重命名和删除
- 支持响应式设计（移动端 + 桌面端）

### 代码质量指标
- TypeScript 类型覆盖率 100%
- 单元测试覆盖率 > 80%
- 无严重的 ESLint 警告
- 构建成功且无错误

## 参考资料

- MetaWise.OS 分析文档：`docs/reference/metawise-agent-analysis.md`
- 当前架构文档：`docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`
- assistant-ui 文档：https://www.assistant-ui.com/
- Next.js App Router 文档：https://nextjs.org/docs/app

## 附录

### A. Agent Seed 数据示例

```typescript
const agentSeeds = [
  {
    id: 'opc-assistant',
    name: 'OPC 战略助手',
    category: '战略咨询',
    icon: '🤖',
    color: '#3B82F6',
    capabilities: ['战略分析', '定价咨询', '市场洞察'],
    status: 'active',
    prompt_ref: 'opc-assistant-v1',
    model: 'gpt-4',
  },
  {
    id: 'content-creator',
    name: '内容创作专家',
    category: '内容创作',
    icon: '✍️',
    color: '#10B981',
    capabilities: ['文案撰写', 'SEO 优化', '热点追踪'],
    status: 'active',
    prompt_ref: 'content-creator-v1',
    model: 'gpt-4',
  },
  {
    id: 'data-analyst',
    name: '数据分析师',
    category: '数据分析',
    icon: '📊',
    color: '#8B5CF6',
    capabilities: ['数据可视化', '趋势分析', '报告生成'],
    status: 'active',
    prompt_ref: 'data-analyst-v1',
    model: 'gpt-4',
  },
];
```

### B. Thread 数据结构示例

```typescript
interface Thread {
  id: string;
  user_id: string;
  agent_id: string;
  title: string; // "如何制定定价策略？"
  last_message_at: Date;
  message_count: number;
  is_archived: boolean;
  created_at: Date;
  updated_at: Date;
}
```

### C. API 请求示例

**获取 Agent 列表：**
```bash
GET /api/agents
Authorization: Bearer <token>

Response:
{
  "agents": [
    {
      "id": "opc-assistant",
      "name": "OPC 战略助手",
      "category": "战略咨询",
      "icon": "🤖",
      "color": "#3B82F6",
      "capabilities": ["战略分析", "定价咨询", "市场洞察"],
      "status": "active"
    }
  ]
}
```

**获取线程列表（按 Agent 筛选）：**
```bash
GET /api/chat/threads?agentId=opc-assistant
Authorization: Bearer <token>

Response:
{
  "threads": [
    {
      "id": "thread-123",
      "agent_id": "opc-assistant",
      "title": "如何制定定价策略？",
      "last_message_at": "2026-05-21T10:30:00Z",
      "message_count": 5,
      "is_archived": false,
      "created_at": "2026-05-21T10:00:00Z"
    }
  ]
}
```

**发送消息：**
```bash
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "agentId": "opc-assistant",
  "threadId": "thread-123",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "如何制定定价策略？"
        }
      ]
    }
  ]
}
```

