---
title: OPC Planet 工作区布局重新设计规范
type: spec
status: approved
tags: [web, workspace, layout, refactoring]
created: 2026-05-22
updated: 2026-05-22
author: Technical Writer Agent
related_prd: docs/prd/网站布局规划.md
related_guide: docs/guide/website_core_code_guide.md
---

# OPC Planet 工作区布局重新设计规范

## 1. Executive Summary

本规范定义了 OPC Planet Web 从单一聊天页面向完整工作区的重新设计方案。核心目标是将产品从"技术演示聊天框"升级为"一人企业 Agent 工作台",通过左侧导航、模块化页面和统一布局系统,让用户清晰了解当前位置和可用功能。

**核心变化:**
- 从单页聊天 → 8 个功能模块的完整工作区
- 从 `/chat` 单一路由 → `/workspace/*` 模块化路由体系
- 从三栏布局 (agent sidebar | chat | history) → 统一工作区布局 (workspace sidebar | header + content)
- 保留现有聊天功能,作为"一人企业诊断"模块集成

**实施方式:** 统一重构 (方案 B) - 完全重构布局系统,而非在现有三栏布局上打补丁。

## 2. Current State Analysis

### 2.1 现有实现

**路由结构:**
- `/` 和 `/chat` 都指向同一个 authenticated chat workspace
- 无模块化路由,所有功能集中在单一聊天页面

**布局系统:**
- 使用 `MultiAgentChatLayout` 三栏布局:
  - 左栏: `AgentSidebar` (agent 列表,可折叠)
  - 中栏: `AgentInfoCard` + `Thread` (聊天主区)
  - 右栏: `HistoryPanel` (历史记录,可折叠)
- 布局状态由 `chat-store.ts` (Zustand) 管理
- CSS 类名: `.multi-agent-chat-layout`, `.multi-agent-sidebar-left`, `.multi-agent-main`, `.multi-agent-sidebar-right`

**核心组件:**
```
AuthenticatedChatPage
  -> AssistantRuntimeProvider
  -> MultiAgentChatLayout
     -> AgentSidebar (左)
     -> AgentInfoCard + Thread (中)
     -> HistoryPanel (右)
```

**状态管理:**
- `chat-store.ts`: 管理 agent 选择、sidebar 折叠状态、history 过滤
- `assistant-ui` runtime: 管理线程、消息、流式响应

**样式系统:**
- `globals.css` (1222 行): 包含所有全局样式
- Tailwind CSS v4
- CSS 变量定义在 `:root`

### 2.2 为什么需要重新设计

**产品定位问题:**
- 当前页面定位不清晰,看起来像"技术演示"而非"产品工作台"
- 用户登录后不知道可以做什么、下一步该做什么
- 缺少明确的功能入口和导航结构

**架构限制:**
- 三栏布局专为聊天设计,难以扩展到其他模块类型
- 左侧 agent sidebar 只适合 agent 列表,不适合作为全局导航
- 右侧 history panel 只适合聊天历史,其他模块无法复用

**扩展性问题:**
- 新增功能模块需要完全重新设计布局
- 无法形成统一的工作区体验
- 难以建立清晰的信息架构

## 3. Design Goals

### 3.1 产品目标

1. **清晰的产品定位**: 从"聊天演示"升级为"一人企业工作台"
2. **明确的功能入口**: 用户登录后立刻知道可以做什么
3. **模块化架构**: 每个功能模块有独立页面和清晰边界
4. **统一的用户体验**: 所有模块共享一致的布局和导航模式
5. **可扩展性**: 后续新增模块不需要重构核心布局

### 3.2 技术目标

1. **统一布局系统**: 所有模块共享 `WorkspaceLayout` 组件
2. **清晰的路由结构**: `/workspace/*` 模块化路由,每个模块独立路由
3. **状态隔离**: 工作区状态 (`workspace-store.ts`) 与模块状态分离
4. **样式可维护性**: 移除旧的三栏布局样式,建立新的工作区样式系统
5. **向后兼容**: 保留现有聊天功能,作为诊断模块无缝集成

### 3.3 用户体验目标

1. **导航效率**: 左侧固定导航,模块切换成本低
2. **空间利用**: 主工作区占据最大空间,辅助信息按需展示
3. **视觉一致性**: 统一的颜色、间距、字体系统
4. **响应式设计**: 适配不同屏幕尺寸 (首版优先桌面端)

## 4. Architecture Design

### 4.1 路由结构

```text
/                                    公共入口 (保持现状)
/workspace                           工作区入口,重定向到 /workspace/dashboard
/workspace/dashboard                 总控台 (默认首页)
/workspace/diagnosis                 一人企业诊断 (保留现有聊天功能)
/workspace/opportunities             机会雷达
/workspace/workshop                  方法论工作坊
/workspace/workshop/:workflowId      单个方法论流程详情
/workspace/knowledge                 知识库
/workspace/assets                    资产库
/workspace/assets/:assetId           资产详情
/workspace/mentors                   商业智库
/workspace/mentors/:agentId          专家 Agent 对话
/workspace/account                   账户与用量
```

**路由迁移策略:**
- `/chat` 重定向到 `/workspace/diagnosis` (保持向后兼容)
- `/chat?threadId=xxx` 重定向到 `/workspace/diagnosis?threadId=xxx`

### 4.2 组件层级结构

```
WorkspaceLayout (新)
  ├─ WorkspaceSidebar (新)
  │   ├─ Brand
  │   ├─ Navigation (8 个模块)
  │   └─ UserCard
  ├─ WorkspaceMain (新)
  │   ├─ WorkspaceHeader (新)
  │   │   ├─ ModuleTitle
  │   │   └─ HeaderActions
  │   └─ WorkspaceContent (新)
  │       └─ {children} (各模块页面)
  └─ WorkspaceDrawer (可选,按需显示)
```

**与现有组件的关系:**
- `MultiAgentChatLayout` → 仅在 diagnosis 模块内部使用,或逐步废弃
- `AgentSidebar` → 移除或改造为 diagnosis 模块内部组件
- `HistoryPanel` → 保留在 diagnosis 模块内部
- `Thread` (assistant-ui) → 继续在 diagnosis 模块中使用

### 4.3 文件结构

**新增文件:**
```
web/src/workspace/
  workspace-layout.tsx              统一工作区布局
  workspace-sidebar.tsx             左侧导航栏
  workspace-header.tsx              顶部标题栏
  workspace-store.ts                工作区状态管理
  workspace-navigation.ts           导航配置

web/app/workspace/
  layout.tsx                        工作区路由布局
  page.tsx                          重定向到 dashboard
  dashboard/
    page.tsx                        总控台页面
  diagnosis/
    page.tsx                        诊断模块 (复用现有聊天)
  opportunities/
    page.tsx                        机会雷达 (占位)
  workshop/
    page.tsx                        方法论工作坊首页 (占位)
    [workflowId]/
      page.tsx                      单个流程页面 (占位)
  knowledge/
    page.tsx                        知识库 (占位)
  assets/
    page.tsx                        资产库列表 (占位)
    [assetId]/
      page.tsx                      资产详情 (占位)
  mentors/
    page.tsx                        商业智库首页 (占位)
    [agentId]/
      page.tsx                      专家对话 (占位)
  account/
    page.tsx                        账户与用量 (占位)
```

**重构文件:**
```
web/src/chat/
  authenticated-chat-page.tsx       改为 diagnosis 模块专用
  multi-agent-chat-layout.tsx       保留或废弃 (待定)
  chat-store.ts                     保留,仅用于 diagnosis 模块

web/app/
  page.tsx                          保持现状或重定向到 workspace
  chat/
    page.tsx                        重定向到 /workspace/diagnosis
```

**移除文件:**
- 暂无 (保守策略,先保留旧代码以便回滚)

## 5. Component Specifications

### 5.1 WorkspaceLayout

**职责:**
- 提供统一的工作区布局框架
- 管理 sidebar、header、content 的布局关系
- 响应 sidebar 折叠状态

**接口:**
```typescript
interface WorkspaceLayoutProps {
  children: ReactNode;
}
```

**布局结构:**
```tsx
<div className="workspace-layout">
  <WorkspaceSidebar />
  <div className="workspace-main">
    <WorkspaceHeader />
    <div className="workspace-content">
      {children}
    </div>
  </div>
</div>
```

**样式规格:**
- 全屏布局: `height: 100dvh`
- Flexbox 横向布局
- Sidebar 固定宽度 240px,可折叠到 60px
- Main 区域占据剩余空间

### 5.2 WorkspaceSidebar

**职责:**
- 显示品牌标识
- 提供 8 个模块的导航入口
- 显示用户信息卡片
- 支持折叠/展开

**导航配置:**
```typescript
interface NavigationItem {
  id: string;
  label: string;
  icon: ReactNode;
  href: string;
  badge?: string | number;
}

const navigationItems: NavigationItem[] = [
  { id: 'dashboard', label: '总控台', icon: <LayoutDashboard />, href: '/workspace/dashboard' },
  { id: 'diagnosis', label: '一人企业诊断', icon: <MessageSquare />, href: '/workspace/diagnosis' },
  { id: 'opportunities', label: '机会雷达', icon: <Radar />, href: '/workspace/opportunities' },
  { id: 'workshop', label: '方法论工作坊', icon: <Wrench />, href: '/workspace/workshop' },
  { id: 'knowledge', label: '知识库', icon: <BookOpen />, href: '/workspace/knowledge' },
  { id: 'assets', label: '资产库', icon: <Archive />, href: '/workspace/assets' },
  { id: 'mentors', label: '商业智库', icon: <Users />, href: '/workspace/mentors' },
  { id: 'account', label: '账户与用量', icon: <Settings />, href: '/workspace/account' },
];
```

**样式规格:**
- 背景色: `#2a2a2a`
- 宽度: 240px (展开) / 60px (折叠)
- 品牌区: 高度 60px,绿色文字 `#10b981`
- 导航项: 高度 48px,hover 背景 `#3a3a3a`,active 背景 `#10b981`
- 用户卡片: 固定在底部,高度 60px

### 5.3 WorkspaceHeader

**职责:**
- 显示当前模块标题
- 提供模块级操作按钮 (如"新建"、"导入")
- 显示用户头像和设置入口

**接口:**
```typescript
interface WorkspaceHeaderProps {
  title: string;
  actions?: ReactNode;
}
```

**样式规格:**
- 高度: 60px
- 背景: 白色 `#ffffff`
- 底部边框: `1px solid #e5e5e5`
- 左右内边距: 24px
- Flexbox 横向布局,space-between

### 5.4 模块页面规格

#### 5.4.1 Dashboard (总控台)

**布局:**
- 欢迎区: 标题 + 描述
- 指标卡片网格: 3 列,展示企业健康度、活跃机会、知识资产
- 最近活动列表

**占位内容:**
```tsx
<div className="dashboard-page">
  <div className="welcome-section">
    <h2>欢迎回来</h2>
    <p>这是您的一人企业运营中心</p>
  </div>
  <div className="metrics-grid">
    <MetricCard title="企业健康度" value="85%" />
    <MetricCard title="活跃机会" value="12" />
    <MetricCard title="知识资产" value="248" />
  </div>
  <RecentActivity />
</div>
```

#### 5.4.2 Diagnosis (一人企业诊断)

**实现方式:**
- **保留现有聊天功能**,将 `AuthenticatedChatPage` 集成到此模块
- 保留 `MultiAgentChatLayout` 的三栏结构 (或简化为两栏)
- 保留 `assistant-ui` 的 Thread 组件
- 保留 history panel (可选)

**集成方案:**
```tsx
// web/app/workspace/diagnosis/page.tsx
export default async function DiagnosisPage() {
  // 复用现有逻辑
  const user = await getDefaultChatUser();
  const thread = await getOrCreateInitialThread(user.id);
  
  return <AuthenticatedChatPage initialThreadId={thread.id} />;
}
```

**布局调整:**
- 移除左侧 agent sidebar (已有全局 workspace sidebar)
- 保留中间聊天区和右侧 history panel
- 或简化为单栏聊天 + 可选 drawer

#### 5.4.3 其他模块 (占位页面)

**统一占位模板:**
```tsx
<div className="placeholder-page">
  <div className="placeholder-icon">{/* 模块图标 */}</div>
  <h2>{moduleName}</h2>
  <p>此模块正在开发中,敬请期待</p>
  <Button variant="outline" disabled>即将推出</Button>
</div>
```

**样式:**
- 居中布局
- 灰色图标和文字
- 最小高度占满 content 区域

## 6. Data Flow & State Management

### 6.1 状态分层

**全局工作区状态 (workspace-store.ts):**
```typescript
interface WorkspaceStore {
  // 导航状态
  sidebarCollapsed: boolean;
  currentModuleId: string;
  
  // 用户状态
  userId: string;
  userDisplayName: string;
  
  // 操作
  toggleSidebar: () => void;
  setCurrentModule: (moduleId: string) => void;
}
```

**模块级状态:**
- `chat-store.ts`: 仅用于 diagnosis 模块,管理 agent 选择、history 过滤
- 其他模块根据需要创建独立 store

**状态隔离原则:**
- 工作区级状态 (sidebar 折叠、当前模块) 由 `workspace-store.ts` 管理
- 模块内部状态 (聊天历史、表单数据) 由模块自己的 store 管理
- 避免跨模块状态共享,通过 URL 参数或 API 传递数据

### 6.2 导航状态管理

**URL 驱动:**
- 当前模块由 URL 路径决定: `/workspace/dashboard` → `currentModuleId = 'dashboard'`
- 使用 Next.js `usePathname()` 获取当前路径
- Sidebar 根据当前路径高亮对应导航项

**导航切换:**
```typescript
// 使用 Next.js Link 组件
<Link href="/workspace/dashboard">总控台</Link>

// 或使用 router.push
const router = useRouter();
router.push('/workspace/diagnosis');
```

### 6.3 数据流

**模块页面加载:**
```
URL change
  -> Next.js App Router
  -> /workspace/[module]/page.tsx
  -> Server Component 获取初始数据
  -> Client Component 渲染
  -> 模块内部状态初始化
```

**Diagnosis 模块数据流 (保持现状):**
```
User message
  -> assistant-ui runtime
  -> POST /api/chat
  -> chat-thread-service
  -> public-chat-service
  -> KnowledgeGateway
  -> Stream response
  -> assistant-ui 渲染
```

## 7. Styling Strategy

### 7.1 移除的 CSS 类

**旧的三栏布局类 (保留但不再全局使用):**
```css
.multi-agent-chat-layout
.multi-agent-sidebar-left
.multi-agent-main
.multi-agent-sidebar-right
.agent-sidebar-collapsed
.history-panel-collapsed
```

**处理方式:**
- 不立即删除,因为 diagnosis 模块可能继续使用
- 如果 diagnosis 模块改用新布局,则可以删除
- 或将这些类移到 `diagnosis.module.css` 作为模块私有样式

### 7.2 新增的 CSS 类

**工作区布局类:**
```css
/* 主布局 */
.workspace-layout {
  display: flex;
  height: 100dvh;
  overflow: hidden;
}

/* 左侧导航栏 */
.workspace-sidebar {
  width: 240px;
  background: #2a2a2a;
  color: white;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #3a3a3a;
  transition: width 0.2s ease;
}

.workspace-sidebar.collapsed {
  width: 60px;
}

.workspace-sidebar-brand {
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #10b981;
  border-bottom: 1px solid #3a3a3a;
}

.workspace-sidebar-nav {
  flex: 1;
  padding: 10px 0;
  overflow-y: auto;
}

.workspace-nav-item {
  height: 48px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background 0.2s;
  color: #e5e5e5;
  text-decoration: none;
}

.workspace-nav-item:hover {
  background: #3a3a3a;
}

.workspace-nav-item.active {
  background: #10b981;
  color: white;
}

.workspace-sidebar-user {
  height: 60px;
  padding: 0 20px;
  border-top: 1px solid #3a3a3a;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 主工作区 */
.workspace-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.workspace-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.workspace-header-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.workspace-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.workspace-content {
  flex: 1;
  overflow-y: auto;
  background: #fafafa;
}

/* 占位页面 */
.placeholder-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 48px;
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  opacity: 0.3;
}

/* Dashboard 页面 */
.dashboard-page {
  padding: 24px;
}

.welcome-section {
  margin-bottom: 32px;
}

.welcome-section h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-section p {
  color: #666;
  font-size: 16px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

### 7.3 CSS 变量复用

**保持现有 CSS 变量:**
- `--accent: #10b981` (品牌绿色)
- `--background: #fafafa`
- `--foreground: #000000`
- `--border: #e5e5e5`
- 其他 shadcn 变量保持不变

**新增工作区专用变量 (可选):**
```css
:root {
  --workspace-sidebar-width: 240px;
  --workspace-sidebar-collapsed-width: 60px;
  --workspace-header-height: 60px;
  --workspace-sidebar-bg: #2a2a2a;
  --workspace-sidebar-border: #3a3a3a;
}
```

### 7.4 样式组织

**推荐方式:**
1. 全局工作区样式添加到 `globals.css`
2. 模块特定样式使用 CSS Modules (如 `dashboard.module.css`)
3. 组件内联样式使用 Tailwind 类名
4. 复杂交互样式使用 `cn()` 工具函数

## 8. Migration Path

### 8.1 兼容性处理

**路由重定向:**
```typescript
// web/app/chat/page.tsx
import { redirect } from 'next/navigation';

export default function ChatPage({ searchParams }: { searchParams: { threadId?: string } }) {
  const threadId = searchParams.threadId;
  const targetUrl = threadId 
    ? `/workspace/diagnosis?threadId=${threadId}`
    : '/workspace/diagnosis';
  redirect(targetUrl);
}
```

**保留旧组件:**
- `MultiAgentChatLayout` 保留,供 diagnosis 模块使用
- `chat-store.ts` 保留,重命名为 `diagnosis-store.ts` (可选)
- `AgentSidebar` 和 `HistoryPanel` 保留或改造

### 8.2 Diagnosis 模块集成

**方案 A: 完全复用现有布局**
```tsx
// web/app/workspace/diagnosis/page.tsx
export default async function DiagnosisPage() {
  const user = await getDefaultChatUser();
  const thread = await getOrCreateInitialThread(user.id);
  
  return (
    <div className="diagnosis-module">
      <AuthenticatedChatPage initialThreadId={thread.id} />
    </div>
  );
}
```

**方案 B: 简化为两栏布局**
- 移除左侧 agent sidebar (已有全局 sidebar)
- 保留中间聊天区
- 右侧 history panel 改为可选 drawer

**推荐:** 方案 A (首版),方案 B (后续优化)

### 8.3 渐进式迁移步骤

**Step 1: 创建工作区框架 (不影响现有功能)**
- 创建 `WorkspaceLayout`、`WorkspaceSidebar`、`WorkspaceHeader`
- 创建 `/workspace` 路由和 layout
- 创建 dashboard 占位页面
- 此时 `/chat` 仍然正常工作

**Step 2: 集成 diagnosis 模块**
- 创建 `/workspace/diagnosis` 页面
- 复用 `AuthenticatedChatPage`
- 添加 `/chat` 到 `/workspace/diagnosis` 的重定向
- 测试聊天功能是否正常

**Step 3: 创建其他占位模块**
- 创建 7 个占位页面
- 测试导航切换
- 测试 URL 路由

**Step 4: 样式调整**
- 添加工作区样式到 `globals.css`
- 调整 diagnosis 模块样式以适配新布局
- 移除或隔离旧的三栏布局样式

**Step 5: 测试和优化**
- 测试所有路由
- 测试 sidebar 折叠
- 测试响应式布局
- 性能优化

## 9. Testing Strategy

### 9.1 单元测试

**组件测试:**
```typescript
// tests/workspace/workspace-sidebar.test.tsx
describe('WorkspaceSidebar', () => {
  it('renders all 8 navigation items', () => {
    render(<WorkspaceSidebar />);
    expect(screen.getByText('总控台')).toBeInTheDocument();
    expect(screen.getByText('一人企业诊断')).toBeInTheDocument();
    // ... 其他 6 个
  });

  it('highlights active navigation item', () => {
    render(<WorkspaceSidebar />);
    const activeItem = screen.getByText('总控台').closest('a');
    expect(activeItem).toHaveClass('active');
  });

  it('toggles sidebar collapse', () => {
    render(<WorkspaceSidebar />);
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).not.toHaveClass('collapsed');
    
    fireEvent.click(screen.getByLabelText('折叠侧边栏'));
    expect(sidebar).toHaveClass('collapsed');
  });
});
```

**状态管理测试:**
```typescript
// tests/workspace/workspace-store.test.ts
describe('workspace-store', () => {
  it('toggles sidebar collapsed state', () => {
    const { result } = renderHook(() => useWorkspaceStore());
    expect(result.current.sidebarCollapsed).toBe(false);
    
    act(() => result.current.toggleSidebar());
    expect(result.current.sidebarCollapsed).toBe(true);
  });
});
```

### 9.2 集成测试

**路由测试:**
```typescript
// tests/app/workspace-routes.test.ts
describe('Workspace Routes', () => {
  it('redirects /workspace to /workspace/dashboard', async () => {
    const response = await fetch('/workspace');
    expect(response.redirected).toBe(true);
    expect(response.url).toContain('/workspace/dashboard');
  });

  it('redirects /chat to /workspace/diagnosis', async () => {
    const response = await fetch('/chat');
    expect(response.redirected).toBe(true);
    expect(response.url).toContain('/workspace/diagnosis');
  });

  it('preserves threadId in redirect', async () => {
    const response = await fetch('/chat?threadId=abc123');
    expect(response.url).toContain('threadId=abc123');
  });
});
```

**Diagnosis 模块测试:**
```typescript
// tests/workspace/diagnosis-integration.test.tsx
describe('Diagnosis Module', () => {
  it('loads existing chat functionality', async () => {
    render(<DiagnosisPage />);
    await waitFor(() => {
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });
  });

  it('preserves thread history', async () => {
    const threadId = 'test-thread-123';
    render(<DiagnosisPage searchParams={{ threadId }} />);
    
    await waitFor(() => {
      expect(screen.getByText(/历史消息/)).toBeInTheDocument();
    });
  });
});
```

### 9.3 用户流程测试

**关键用户流程:**

1. **首次登录流程:**
   - 访问 `/` → 看到公共入口
   - 登录 → 重定向到 `/workspace/dashboard`
   - 看到欢迎页面和指标卡片

2. **模块导航流程:**
   - 点击左侧"一人企业诊断" → 进入 `/workspace/diagnosis`
   - 看到聊天界面
   - 发送消息 → 收到回复
   - 点击"总控台" → 返回 dashboard

3. **向后兼容流程:**
   - 访问旧的 `/chat` URL → 自动重定向到 `/workspace/diagnosis`
   - 访问 `/chat?threadId=xxx` → 重定向并保留 threadId
   - 聊天功能正常工作

4. **Sidebar 折叠流程:**
   - 点击折叠按钮 → sidebar 宽度变为 60px
   - 导航项只显示图标
   - 再次点击 → 恢复 240px 宽度

### 9.4 性能测试

**关键指标:**
- 首屏加载时间 (FCP) < 1.5s
- 模块切换响应时间 < 200ms
- Sidebar 折叠动画流畅 (60fps)
- Diagnosis 模块聊天响应时间与现有相同

**测试方法:**
- 使用 Lighthouse 测试性能
- 使用 Chrome DevTools Performance 分析
- 测试不同网络条件下的加载时间

## 10. Implementation Phases

### Phase 1: 核心工作区结构 (2-3 天)

**目标:** 建立工作区框架,不影响现有聊天功能

**任务清单:**
- [ ] 创建 `workspace-store.ts` 状态管理
- [ ] 创建 `WorkspaceLayout` 组件
- [ ] 创建 `WorkspaceSidebar` 组件 (8 个导航项)
- [ ] 创建 `WorkspaceHeader` 组件
- [ ] 创建 `/workspace` 路由结构
- [ ] 创建 dashboard 占位页面
- [ ] 添加工作区样式到 `globals.css`
- [ ] 编写 `WorkspaceLayout` 单元测试

**验收标准:**
- 访问 `/workspace/dashboard` 能看到占位页面
- Sidebar 显示 8 个导航项
- Sidebar 折叠功能正常
- 导航项高亮当前模块
- `/chat` 仍然正常工作 (未受影响)

### Phase 2: Diagnosis 模块集成 (1-2 天)

**目标:** 将现有聊天功能集成到 diagnosis 模块

**任务清单:**
- [ ] 创建 `/workspace/diagnosis/page.tsx`
- [ ] 集成 `AuthenticatedChatPage` 到 diagnosis 模块
- [ ] 添加 `/chat` 到 `/workspace/diagnosis` 的重定向
- [ ] 测试 threadId 参数传递
- [ ] 测试聊天功能 (发送消息、接收回复、历史记录)
- [ ] 调整 diagnosis 模块样式以适配新布局
- [ ] 编写 diagnosis 集成测试

**验收标准:**
- `/workspace/diagnosis` 显示聊天界面
- 聊天功能与现有完全一致
- `/chat` 自动重定向到 `/workspace/diagnosis`
- `/chat?threadId=xxx` 正确传递 threadId
- 历史记录面板正常工作

### Phase 3: 占位模块页面 (1 天)

**目标:** 创建其他 7 个模块的占位页面

**任务清单:**
- [ ] 创建 `/workspace/opportunities/page.tsx` (占位)
- [ ] 创建 `/workspace/workshop/page.tsx` (占位)
- [ ] 创建 `/workspace/knowledge/page.tsx` (占位)
- [ ] 创建 `/workspace/assets/page.tsx` (占位)
- [ ] 创建 `/workspace/mentors/page.tsx` (占位)
- [ ] 创建 `/workspace/account/page.tsx` (占位)
- [ ] 创建统一占位组件 `PlaceholderPage`
- [ ] 测试所有路由可访问

**验收标准:**
- 所有 8 个模块都可以通过导航访问
- 占位页面显示模块名称和"开发中"提示
- URL 路由正确
- 浏览器前进/后退按钮正常工作

### Phase 4: 样式优化和测试 (1-2 天)

**目标:** 完善样式,确保质量

**任务清单:**
- [ ] 优化 sidebar 折叠动画
- [ ] 优化 dashboard 页面样式
- [ ] 调整响应式布局 (可选)
- [ ] 编写路由重定向测试
- [ ] 编写用户流程测试
- [ ] 运行 Lighthouse 性能测试
- [ ] 修复发现的问题
- [ ] 更新文档

**验收标准:**
- 所有单元测试通过
- 所有集成测试通过
- Lighthouse 性能评分 > 90
- 无明显样式问题
- 文档更新完成

**总计时间:** 5-8 天

## 11. Success Criteria

### 11.1 功能完整性

- [ ] 8 个模块都可以通过左侧导航访问
- [ ] Dashboard 显示欢迎页面和占位内容
- [ ] Diagnosis 模块完全保留现有聊天功能
- [ ] 其他 6 个模块显示占位页面
- [ ] Sidebar 折叠/展开功能正常
- [ ] 导航项正确高亮当前模块

### 11.2 向后兼容性

- [ ] `/chat` 自动重定向到 `/workspace/diagnosis`
- [ ] `/chat?threadId=xxx` 正确传递 threadId
- [ ] 现有聊天功能无任何退化
- [ ] 历史线程可以正常访问
- [ ] API 端点无需修改

### 11.3 用户体验

- [ ] 用户登录后看到清晰的模块导航
- [ ] 模块切换响应迅速 (< 200ms)
- [ ] Sidebar 折叠动画流畅
- [ ] 视觉风格统一,符合设计预览
- [ ] 无明显布局错位或样式问题

### 11.4 代码质量

- [ ] TypeScript 类型检查通过 (`npm run typecheck`)
- [ ] 所有单元测试通过 (`npm test`)
- [ ] 所有集成测试通过
- [ ] 无 console 错误或警告
- [ ] 代码符合项目规范

### 11.5 性能指标

- [ ] 首屏加载时间 (FCP) < 1.5s
- [ ] Lighthouse 性能评分 > 90
- [ ] 模块切换无明显延迟
- [ ] Diagnosis 模块聊天性能与现有相同

### 11.6 文档完整性

- [ ] 更新 `website_core_code_guide.md` 包含工作区架构
- [ ] 创建工作区开发指南 (如需要)
- [ ] 更新 README 包含新的路由结构
- [ ] 代码注释清晰完整


## 12. Open Questions

### 12.1 Diagnosis 模块布局

**问题:** Diagnosis 模块是否需要简化布局?

**选项:**
- **A.** 完全保留现有三栏布局 (agent sidebar | chat | history panel)
- **B.** 移除左侧 agent sidebar,只保留 chat + history panel
- **C.** 简化为单栏 chat,history 改为可选 drawer

**建议:** 首版选择 A (最小改动),后续根据用户反馈选择 B 或 C

**影响:**
- 选项 A: 实现最快,但可能与全局 sidebar 重复
- 选项 B: 需要调整布局,但更统一
- 选项 C: 需要重构 history panel,工作量最大

### 12.2 Dashboard 内容

**问题:** Dashboard 首版应该显示什么内容?

**选项:**
- **A.** 静态占位内容 (如预览 HTML 所示)
- **B.** 真实数据 (线程数、消息数、用量统计)
- **C.** 空状态 + 快捷入口

**建议:** 首版选择 A (静态占位),Phase 2 实现 B (真实数据)

**影响:**
- 选项 A: 实现最快,但无实际价值
- 选项 B: 需要开发数据聚合逻辑
- 选项 C: 需要设计空状态和快捷入口

### 12.3 Sidebar 图标

**问题:** 导航项使用什么图标库?

**选项:**
- **A.** Lucide React (项目已使用)
- **B.** 自定义 SVG 图标
- **C.** 混合使用

**建议:** 选择 A (Lucide React),保持一致性

**影响:**
- 选项 A: 图标风格统一,但可能不够个性化
- 选项 B: 可以定制,但增加维护成本
- 选项 C: 风格可能不统一

### 12.4 响应式设计

**问题:** 首版是否需要支持移动端?

**选项:**
- **A.** 仅支持桌面端 (≥ 1024px)
- **B.** 支持平板端 (≥ 768px)
- **C.** 完全响应式 (包括手机)

**建议:** 首版选择 A (桌面优先),后续扩展到 B 和 C

**影响:**
- 选项 A: 实现最快,但移动端体验差
- 选项 B: 需要设计平板布局
- 选项 C: 需要完整的响应式设计,工作量大

### 12.5 旧代码清理

**问题:** 何时删除旧的三栏布局代码?

**选项:**
- **A.** 立即删除 (激进)
- **B.** 保留 1-2 个版本后删除 (保守)
- **C.** 永久保留 (如果 diagnosis 模块继续使用)

**建议:** 选择 B (保守策略),确保稳定后再删除

**影响:**
- 选项 A: 代码最干净,但回滚困难
- 选项 B: 保留回滚能力,但代码冗余
- 选项 C: 代码库持续膨胀

## 13. References

### 13.1 相关文档

- **PRD:** `docs/prd/网站布局规划.md` - 产品需求和信息架构
- **代码指南:** `docs/guide/website_core_code_guide.md` - 现有代码结构
- **布局预览:** `web/docs/workspace-layout-preview.html` - 视觉设计参考

### 13.2 关键代码文件

**现有实现:**
- `web/src/chat/authenticated-chat-page.tsx` - 现有聊天页面
- `web/src/chat/multi-agent-chat-layout.tsx` - 三栏布局
- `web/src/chat/chat-store.ts` - 聊天状态管理
- `web/app/globals.css` - 全局样式

**需要创建:**
- `web/src/workspace/workspace-layout.tsx`
- `web/src/workspace/workspace-sidebar.tsx`
- `web/src/workspace/workspace-header.tsx`
- `web/src/workspace/workspace-store.ts`
- `web/app/workspace/layout.tsx`
- `web/app/workspace/*/page.tsx` (8 个模块页面)

### 13.3 技术栈

- **框架:** Next.js 15 App Router
- **UI 库:** React 19
- **样式:** Tailwind CSS v4 + CSS Modules
- **状态管理:** Zustand
- **聊天 UI:** assistant-ui
- **图标:** Lucide React
- **类型:** TypeScript strict mode

### 13.4 设计原则

1. **渐进式迁移:** 不破坏现有功能,逐步添加新功能
2. **向后兼容:** 保留旧路由的重定向,确保用户无感知
3. **模块化设计:** 每个模块独立,互不影响
4. **统一体验:** 所有模块共享一致的布局和交互模式
5. **性能优先:** 确保快速加载和流畅交互

---

## Appendix A: 组件接口定义

### WorkspaceLayout

```typescript
interface WorkspaceLayoutProps {
  children: ReactNode;
}

export function WorkspaceLayout({ children }: WorkspaceLayoutProps): JSX.Element;
```

### WorkspaceSidebar

```typescript
interface WorkspaceSidebarProps {
  className?: string;
}

export function WorkspaceSidebar({ className }: WorkspaceSidebarProps): JSX.Element;
```

### WorkspaceHeader

```typescript
interface WorkspaceHeaderProps {
  title: string;
  actions?: ReactNode;
  className?: string;
}

export function WorkspaceHeader({ title, actions, className }: WorkspaceHeaderProps): JSX.Element;
```

### workspace-store

```typescript
interface WorkspaceStore {
  // State
  sidebarCollapsed: boolean;
  currentModuleId: string;
  userId: string;
  userDisplayName: string;
  
  // Actions
  toggleSidebar: () => void;
  setCurrentModule: (moduleId: string) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export const useWorkspaceStore: () => WorkspaceStore;
```

---

## Appendix B: 路由映射表

| 旧路由 | 新路由 | 重定向 | 说明 |
|--------|--------|--------|------|
| `/` | `/` | 否 | 公共入口,保持不变 |
| `/chat` | `/workspace/diagnosis` | 是 | 聊天页面迁移到 diagnosis 模块 |
| `/chat?threadId=xxx` | `/workspace/diagnosis?threadId=xxx` | 是 | 保留 threadId 参数 |
| - | `/workspace` | 重定向到 `/workspace/dashboard` | 工作区入口 |
| - | `/workspace/dashboard` | 否 | 总控台 (默认首页) |
| - | `/workspace/diagnosis` | 否 | 一人企业诊断 |
| - | `/workspace/opportunities` | 否 | 机会雷达 |
| - | `/workspace/workshop` | 否 | 方法论工作坊 |
| - | `/workspace/knowledge` | 否 | 知识库 |
| - | `/workspace/assets` | 否 | 资产库 |
| - | `/workspace/mentors` | 否 | 商业智库 |
| - | `/workspace/account` | 否 | 账户与用量 |

---

**文档版本:** 1.0  
**最后更新:** 2026-05-22  
**状态:** 已批准,待实施
