# MetaWise.OS Agent 交互架构分析

## 概述

MetaWise.OS 是一个 AI 内容创作平台，提供了多个专业化的 Agent 工具。本文档分析了其 Agent 交互架构，为我们的 OPC Planet 项目提供参考。

访问地址：http://8.138.196.136/

## 核心架构特点

### 1. 多 Agent 系统

平台提供了多个专业化的 Agent，每个 Agent 针对不同的应用场景：

- **低粉爆款雷达** - 内容发现工具
- **一键提取文案** - 文案提取工具
- **爆款文案工坊** - 文案创作工具
- **AI 克隆音色** - 语音克隆
- **数字人视频** - 视频生成
- **Agent X 深度创作** - 深度内容创作（重点分析对象）
- **AI 商业智库** - 商业咨询

### 2. Agent X 深度创作引擎架构

#### 2.1 平台模式选择

Agent X 提供了两种平台模式，每种模式对应不同的知识库和系统提示词：

**微信公众号模式** 📰
- 适合：长文、深度分析、行业评论和复杂结构内容
- 工作流：搜索 → 提纲 → 正文 → 排版
- 特点：结构化创作流程，适合长篇内容

**小红书模式** 📕
- 适合：高互动、强情绪和强视觉内容
- 工作流：对话式创作流程
- 特点：边聊边改，灵活互动

#### 2.2 核心功能组件

**模型选择系统**
- 支持多种 AI 模型：
  - GPT-5.4 / GPT-5.5 / GPT-5.4 Mini / GPT-5.2
  - DeepSeek V4 Pro / DeepSeek V3 / DeepSeek R1
  - Claude Sonnet
- 用户可根据需求切换不同模型

**图片生成集成**
- GPT Image 2 ☁️
- Doubao Seedream 5.0 ☁️
- 纯文字模式（不生图）

**辅助功能**
- 🌐 联网搜索：支持带检索的内容创作
- ✨ 特殊功能按钮
- 🖼️ 上传参考图：支持图片参考输入

#### 2.3 对话历史管理

**过往记录面板**
- 位置：右侧滑出面板
- 筛选功能：
  - 全部记录
  - 公众号记录
  - 小红书记录
- 功能：直接恢复历史创作会话

**快捷模板系统**
- 深度行业分析
- 爆款小红书
- 公众号洗稿
- 产品种草

### 3. UI/UX 设计特点

#### 3.1 布局结构

**左侧边栏（256px）**
- 品牌标识区
- 功能导航菜单
- 用户信息卡片
- 暗黑模式切换

**主内容区**
- 动态内容展示
- 根据选择的 Agent 切换界面

**右侧面板（可滑出）**
- 历史记录管理
- 按需显示，不占用主要空间

#### 3.2 交互设计

**模式切换**
- 清晰的视觉区分（emoji + 标题 + 描述）
- 卡片式布局，易于选择

**状态反馈**
- 按钮状态：active、disabled
- 用户权限显示
- 算力和产出统计

### 4. 技术架构推测

#### 4.1 前端技术栈
- 现代化的 React/Vue 框架
- 响应式布局设计
- 组件化架构

#### 4.2 Agent 系统设计

**多 Agent 架构**
```
┌─────────────────────────────────────┐
│         Agent 选择层                 │
│  (低粉爆款雷达、Agent X、商业智库等)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Agent 配置层                    │
│  - 平台模式（公众号/小红书）          │
│  - 模型选择（GPT/DeepSeek/Claude）   │
│  - 功能开关（联网/生图）              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      对话管理层                      │
│  - 会话创建                          │
│  - 历史记录                          │
│  - 会话恢复                          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      AI 引擎层                       │
│  - 多模型调度                        │
│  - 知识库检索                        │
│  - 提示词管理                        │
└─────────────────────────────────────┘
```

## 5. 对 OPC Planet 的启发

### 5.1 必须实现的核心功能

1. **多 Agent 管理**
   - 每个 Agent 对应不同的知识库
   - 每个 Agent 有独立的系统提示词
   - Agent 之间相互独立

2. **多对话管理**
   - 每个 Agent 可以创建多个对话
   - 对话历史持久化
   - 快速切换和恢复对话

3. **模型选择**
   - 支持多种 AI 模型
   - 用户可自由切换
   - 不同 Agent 可配置默认模型

4. **知识库集成**
   - Agent 与知识库绑定
   - 支持 RAG 检索
   - 联网搜索能力

### 5.2 UI/UX 设计建议

1. **清晰的信息架构**
   - 左侧：Agent 列表
   - 中间：对话界面
   - 右侧：历史记录（可折叠）

2. **直观的 Agent 切换**
   - 卡片式展示
   - 图标 + 标题 + 描述
   - 清晰的功能说明

3. **便捷的对话管理**
   - 侧边栏历史记录
   - 按 Agent 分类
   - 搜索和筛选功能

### 5.3 技术实现要点

1. **数据模型设计**
```typescript
// Agent 模型
interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  systemPrompt: string;
  knowledgeBaseId?: string;
  defaultModel: string;
  capabilities: string[];
}

// 对话模型
interface Conversation {
  id: string;
  agentId: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
  metadata: {
    model: string;
    settings: ConversationSettings;
  };
}

// 消息模型
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
  };
}
```

2. **状态管理**
   - 当前选中的 Agent
   - 当前活跃的对话
   - 对话历史列表
   - 用户设置和偏好

3. **API 设计**
   - `/api/agents` - Agent 管理
   - `/api/conversations` - 对话管理
   - `/api/messages` - 消息发送
   - `/api/knowledge-bases` - 知识库管理

## 6. 下一步行动

1. **设计数据库 Schema**
   - Agent 表
   - Conversation 表
   - Message 表
   - KnowledgeBase 表

2. **实现核心 API**
   - Agent CRUD
   - Conversation CRUD
   - Message 流式传输
   - 知识库检索

3. **开发前端界面**
   - Agent 选择页面
   - 对话界面
   - 历史记录面板
   - 设置面板

4. **集成 AI 能力**
   - 多模型支持
   - RAG 检索
   - 流式响应
   - 上下文管理

## 附录

### 截图
- `metawise-agent-interface.png` - Agent X 创作界面截图

### 参考链接
- 网站地址：http://8.138.196.136/
- 测试账号：88194406@qq.com / 999999999
