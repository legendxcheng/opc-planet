# AI聊天应用交互体验改进方案

## 1. 方案概述

本方案旨在改进OPC Planet AI聊天应用的用户体验，解决三个核心问题：AI思考时缺少状态提示、缺少新对话功能、Agent切换后无法跳转到最新会话。

参考项目：Vercel AI Chatbot (github.com/vercel/chatbot)，该项目在流式UI、加载状态和会话管理方面有成熟实践。

技术栈：基于现有的 Next.js + @assistant-ui/react + Zustand 架构，保持与现有代码的兼容性。

## 2. 技术选型

### 2.1 借鉴的技术组件

- **流式加载指示器**：参考 Vercel Chatbot 的 `StreamableUI` 组件设计
- **状态管理模式**：使用 @assistant-ui/react 的 `useAuiState` 监听运行状态
- **UI组件**：复用现有 shadcn/ui 组件库，新增 Spinner 和 ThinkingIndicator 组件
- **会话切换逻辑**：扩展现有 `useChatStore` 和 `chat-thread-service.ts`

### 2.2 不采用的技术

- 不引入 AI SDK hooks（与 @assistant-ui/react 冲突）
- 不使用 React Server Components（现有架构为 Client Components）

## 3. 详细设计

### 3.1 加载状态指示器

**问题分析**：当前 `thread.tsx` 中 AI 消息渲染时，没有明确的"思考中"状态提示，用户无法感知 AI 是否在处理请求。

**解决方案**：

1. **新增 ThinkingIndicator 组件**
   - 位置：`web/components/assistant-ui/thinking-indicator.tsx`
   - 功能：显示动画点点点效果 + "思考中..." 文本
   - 样式：参考 Vercel Chatbot 的脉动动画效果

2. **修改 AssistantMessage 组件**
   - 文件：`web/components/assistant-ui/thread.tsx`
   - 在 `MessagePrimitive.GroupedParts` 前添加状态检测
   - 使用 `useAuiState((s) => s.message.status.type)` 判断是否为 "running"
   - 当状态为 "running" 且无内容时，显示 ThinkingIndicator

3. **技术实现**
   ```tsx
   const isRunning = useAuiState((s) => s.message.status.type === "running");
   const hasContent = useAuiState((s) => s.message.content.length > 0);
   
   if (isRunning && !hasContent) {
     return <ThinkingIndicator />;
   }
   ```

**预期效果**：用户发送消息后，立即看到"思考中..."动画，直到 AI 开始输出内容。

### 3.2 新对话按钮

**问题分析**：当前只能通过历史面板的"新建线程"按钮创建对话，位置不够显眼，且在历史面板折叠时无法访问。

**解决方案**：

1. **在 Composer 区域添加新对话按钮**
   - 位置：`web/components/assistant-ui/thread.tsx` 的 `Composer` 组件
   - 按钮位置：输入框左上角，与附件按钮并列
   - 图标：使用 `PlusIcon` 或 `MessageSquarePlusIcon`

2. **实现新对话逻辑**
   - 调用 `useRemoteThreadListRuntime` 的 `switchToNewThread()` 方法
   - 清空当前输入框内容
   - 滚动到顶部显示欢迎界面

3. **技术实现**
   ```tsx
   import { useThreadListRuntime } from "@assistant-ui/react";
   
   const threadListRuntime = useThreadListRuntime();
   const handleNewChat = () => {
     threadListRuntime.switchToNewThread();
   };
   ```

**预期效果**：用户可以随时点击按钮开启新对话，无需依赖历史面板。

### 3.3 Agent切换时的会话切换

**问题分析**：当前切换 Agent 后，仍停留在旧 Agent 的会话中，导致用户困惑。需要自动切换到新 Agent 的最新会话。

**解决方案**：

1. **扩展 ChatThreadRecord 查询逻辑**
   - 文件：`web/src/chat/chat-thread-service.ts`
   - 新增函数：`getLatestThreadByAgentId(userId, agentId)`
   - 按 `lastMessageAt` 或 `updatedAt` 降序排序，返回第一条

2. **修改 Agent 切换处理**
   - 文件：`web/src/chat/authenticated-chat-page.tsx`
   - 在 `setSelectedAgentId` 后添加副作用
   - 调用新增的查询函数获取最新会话
   - 使用 `threadListRuntime.switchToThread(threadId)` 切换

3. **技术实现**
   ```tsx
   // chat-thread-service.ts
   export function getLatestThreadByAgentId(
     userId: string,
     agentId: string,
     repository = getDefaultMetadataRepository()
   ): ChatThreadRecord | null {
     const threads = repository.listChatThreadsByUserId(userId)
       .filter(t => t.agentId === agentId && t.status === "regular")
       .sort((a, b) => {
         const aTime = a.lastMessageAt ?? a.updatedAt;
         const bTime = b.lastMessageAt ?? b.updatedAt;
         return bTime.localeCompare(aTime);
       });
     return threads[0] ?? null;
   }
   
   // authenticated-chat-page.tsx
   useEffect(() => {
     if (!selectedAgentId) return;
     
     const latestThread = await fetch(
       `/api/chat/threads/latest?agentId=${selectedAgentId}`
     ).then(r => r.json());
     
     if (latestThread?.id) {
       runtime.switchToThread(latestThread.id);
     } else {
       runtime.switchToNewThread();
     }
   }, [selectedAgentId]);
   ```

**预期效果**：切换 Agent 后，自动跳转到该 Agent 的最新对话；如果没有历史对话，则创建新对话。

## 4. 实施步骤

### 步骤1：创建 ThinkingIndicator 组件（优先级：高）

**修改文件**：
- 新建 `web/components/assistant-ui/thinking-indicator.tsx`

**改动内容**：
```tsx
export function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 px-2 py-3 text-muted-foreground">
      <div className="flex gap-1">
        <span className="animate-bounce [animation-delay:-0.3s]">·</span>
        <span className="animate-bounce [animation-delay:-0.15s]">·</span>
        <span className="animate-bounce">·</span>
      </div>
      <span className="text-sm">思考中</span>
    </div>
  );
}
```

**预期效果**：可复用的思考状态指示器组件。

### 步骤2：集成 ThinkingIndicator 到 AssistantMessage（优先级：高）

**修改文件**：
- `web/components/assistant-ui/thread.tsx`

**改动内容**：
- 在 `AssistantMessage` 组件开头添加状态检测
- 导入 `ThinkingIndicator` 组件
- 在消息内容区域前条件渲染

**预期效果**：AI 开始处理时显示思考动画。

### 步骤3：添加新对话按钮（优先级：中）

**修改文件**：
- `web/components/assistant-ui/thread.tsx`

**改动内容**：
- 在 `Composer` 组件的 `ComposerAction` 区域添加按钮
- 使用 `useThreadListRuntime` hook
- 绑定 `switchToNewThread` 方法

**预期效果**：用户可以快速开启新对话。

### 步骤4：实现 Agent 切换时的会话跳转（优先级：中）

**修改文件**：
- `web/src/chat/chat-thread-service.ts`
- `web/app/api/chat/threads/latest/route.ts`（新建）
- `web/src/chat/authenticated-chat-page.tsx`

**改动内容**：
1. 在 service 层添加 `getLatestThreadByAgentId` 函数
2. 创建 API 路由 `/api/chat/threads/latest`
3. 在 `authenticated-chat-page.tsx` 中监听 `selectedAgentId` 变化
4. 调用 API 获取最新会话并切换

**预期效果**：切换 Agent 后自动跳转到对应的最新会话。

### 步骤5：优化加载状态样式（优先级：低）

**修改文件**：
- `web/app/globals.css` 或相关样式文件

**改动内容**：
- 调整 ThinkingIndicator 的动画时长和颜色
- 确保在深色模式下也清晰可见

**预期效果**：视觉效果更加精致。

## 5. 风险评估

### 5.1 技术风险

**风险1：@assistant-ui/react 版本兼容性**
- 描述：`switchToNewThread` 和 `switchToThread` 方法可能在旧版本中不存在
- 应对：检查当前版本，必要时升级到最新版本
- 降级方案：使用 URL 参数 + router.push 实现切换

**风险2：状态同步问题**
- 描述：Agent 切换和会话切换可能产生竞态条件
- 应对：使用 `useEffect` 的依赖数组严格控制执行时机
- 降级方案：添加防抖逻辑，延迟 300ms 执行切换

**风险3：历史会话查询性能**
- 描述：用户会话数量多时，查询最新会话可能较慢
- 应对：在数据库层添加索引（agentId + updatedAt）
- 降级方案：限制查询范围为最近 100 条会话

### 5.2 用户体验风险

**风险1：自动切换会话可能打断用户操作**
- 描述：用户正在查看旧会话时切换 Agent，会被强制跳转
- 应对：添加确认提示："切换到 [Agent名称] 的最新对话？"
- 降级方案：仅在当前会话为空时自动切换

**风险2：新对话按钮位置可能不够显眼**
- 描述：用户可能找不到新对话按钮
- 应对：添加首次使用引导提示
- 降级方案：同时保留历史面板的新建按钮

### 5.3 兼容性风险

**风险1：现有会话数据可能缺少 agentId**
- 描述：旧数据可能没有 agentId 字段
- 应对：数据迁移脚本，为旧会话设置默认 agentId
- 降级方案：查询时过滤掉 agentId 为 null 的记录

---

**文档版本**：v1.0  
**创建日期**：2026-05-26  
**预计工作量**：2-3 个工作日  
**依赖项**：@assistant-ui/react >= 0.5.0

