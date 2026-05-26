# AI聊天应用交互体验改进 - 实施总结

## 实施日期
2026-05-26

## 改进目标
解决三个核心用户体验问题：
1. AI思考时缺少清晰的状态提示
2. 缺少开启新对话的功能
3. 切换Agent后无法切换到该Agent的最新对话Session

## 参考方案
基于 Vercel AI Chatbot 的最佳实践，使用现有的 @assistant-ui/react 框架实现改进。

## 实施内容

### 1. 创建 ThinkingIndicator 组件 ✅

**新建文件**: `web/components/assistant-ui/thinking-indicator.tsx`

**功能**: 
- 显示动画点点点效果
- 显示"思考中"文本提示
- 使用 Tailwind CSS 动画实现脉动效果

**实现细节**:
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

### 2. 集成 ThinkingIndicator 到 AssistantMessage ✅

**修改文件**: `web/components/assistant-ui/thread.tsx`

**修改内容**:
1. 导入 ThinkingIndicator 组件
2. 在 AssistantMessage 组件中添加状态检测
3. 当消息状态为 "running" 且无内容时显示思考指示器

**关键代码**:
```tsx
<AuiIf condition={(s) => s.message.status?.type === "running" && s.message.content.length === 0}>
  <ThinkingIndicator />
</AuiIf>
```

**效果**: 用户发送消息后，立即看到"思考中..."动画，直到 AI 开始输出内容。

### 3. 添加新对话按钮 ✅

**修改文件**: `web/components/assistant-ui/thread.tsx`

**修改内容**:
1. 导入 `PlusIcon` 图标
2. 导入 `useAui` hook
3. 在 ComposerAction 组件中添加新对话按钮
4. 实现 handleNewChat 函数调用 `aui.threads().switchToNewThread()`

**关键代码**:
```tsx
const ComposerAction: FC = () => {
  const aui = useAui();

  const handleNewChat = () => {
    aui.threads().switchToNewThread();
  };

  return (
    <div className="aui-composer-action-wrapper relative flex items-center justify-between">
      <div className="flex items-center gap-1">
        <ComposerAddAttachment />
        <TooltipIconButton
          tooltip="新对话"
          side="bottom"
          type="button"
          variant="ghost"
          size="icon"
          className="size-8"
          onClick={handleNewChat}
          aria-label="新对话"
        >
          <PlusIcon className="size-4" />
        </TooltipIconButton>
      </div>
      {/* ... 发送和取消按钮 ... */}
    </div>
  );
};
```

**效果**: 用户可以随时点击输入框左侧的"+"按钮开启新对话，无需依赖历史面板。

### 4. 实现 Agent 切换时的会话跳转 ✅

#### 4.1 扩展 chat-thread-service.ts

**修改文件**: `web/src/chat/chat-thread-service.ts`

**新增函数**: `getLatestThreadByAgentId`

**功能**: 获取指定 Agent 的最新会话

**实现细节**:
```tsx
export function getLatestThreadByAgentId(
  userId: string,
  agentId: string,
  repository: MetadataRepository = getDefaultMetadataRepository(),
): ChatThreadRecord | null {
  const threads = repository
    .listChatThreadsByUserId(userId)
    .filter((t) => t.agentId === agentId && t.status === "regular")
    .sort((a, b) => {
      const aTime = a.lastMessageAt ?? a.updatedAt;
      const bTime = b.lastMessageAt ?? b.updatedAt;
      return bTime.localeCompare(aTime);
    });
  return threads[0] ?? null;
}
```

#### 4.2 创建 API 路由

**新建文件**: `web/app/api/chat/threads/latest/route.ts`

**功能**: 提供 GET 接口获取指定 Agent 的最新会话

**实现细节**:
```tsx
export async function GET(request: NextRequest) {
  const metadataRepository = getDefaultMetadataRepository();
  const user = getDefaultChatUser(metadataRepository);
  const userId = user.id;

  const { searchParams } = new URL(request.url);
  const agentId = searchParams.get("agentId");

  if (!agentId) {
    return NextResponse.json(
      { error: "agentId is required" },
      { status: 400 }
    );
  }

  const latestThread = getLatestThreadByAgentId(userId, agentId, metadataRepository);

  if (!latestThread) {
    return NextResponse.json({ thread: null });
  }

  return NextResponse.json({ thread: latestThread });
}
```

#### 4.3 修改 authenticated-chat-page.tsx

**修改文件**: `web/src/chat/authenticated-chat-page.tsx`

**修改内容**: 添加 useEffect 监听 selectedAgentId 变化

**实现细节**:
```tsx
useEffect(() => {
  if (!selectedAgentId) return;

  const switchToAgentThread = async () => {
    try {
      const response = await fetch(
        `/api/chat/threads/latest?agentId=${selectedAgentId}`
      );
      const data = await response.json();

      if (data.thread?.id) {
        await runtime.threads.switchToThread(data.thread.id);
      } else {
        await runtime.threads.switchToNewThread();
      }
    } catch (error) {
      console.error("Failed to switch to agent thread:", error);
    }
  };

  switchToAgentThread();
}, [selectedAgentId, runtime]);
```

**效果**: 切换 Agent 后，自动跳转到该 Agent 的最新对话；如果没有历史对话，则创建新对话。

## 技术难点与解决方案

### 难点 1: @assistant-ui/react API 使用

**问题**: 初始实现中错误使用了不存在的 `useThreadListRuntime` hook

**解决方案**: 
- 使用 `useAui()` hook 获取 aui 对象
- 通过 `aui.threads()` 访问 ThreadListRuntime
- 调用 `switchToNewThread()` 和 `switchToThread()` 方法

### 难点 2: 用户认证 API

**问题**: 初始实现中尝试导入不存在的 `getCurrentUserId` 函数

**解决方案**:
- 使用 `getDefaultChatUser()` 函数获取用户对象
- 通过 `user.id` 获取用户 ID
- 传递 `metadataRepository` 参数确保数据一致性

### 难点 3: Runtime 类型系统

**问题**: `runtime` 对象类型为 `AssistantRuntime`，不直接包含线程切换方法

**解决方案**:
- 通过 `runtime.threads` 访问 `ThreadListRuntime`
- 使用 `await` 处理异步操作
- 正确的调用方式: `await runtime.threads.switchToThread(threadId)`

## 构建验证

项目构建成功，所有类型检查通过：

```bash
✓ Compiled successfully in 4.3s
✓ Linting and checking validity of types
✓ Generating static pages (19/19)
✓ Finalizing page optimization
```

## 相关文档

- 技术方案: `docs/superpowers/specs/2026-05-26-chat-ux-improvement.md`
- 核心代码指南: `docs/guide/website_core_code_guide.md`

## 后续优化建议

1. **性能优化**: 为 `chat_threads` 表添加 `(agentId, updatedAt)` 复合索引
2. **用户体验**: 添加切换会话时的过渡动画
3. **错误处理**: 添加网络请求失败时的用户提示
4. **测试**: 编写单元测试和集成测试验证功能正确性

## 总结

本次改进成功解决了三个核心用户体验问题，提升了聊天应用的可用性：

1. ✅ AI 思考状态清晰可见
2. ✅ 快速开启新对话
3. ✅ Agent 切换自动跳转到最新会话

所有改进均基于现有技术栈实现，无需引入新依赖，保持了代码的一致性和可维护性。
