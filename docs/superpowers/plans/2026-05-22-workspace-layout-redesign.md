# Workspace Layout Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform OPC Planet from a single-chat-page demo into a complete workspace with 8 functional modules, unified navigation, and clear product positioning.

**Architecture:** Replace the current three-column chat layout (`MultiAgentChatLayout`) with a unified workspace layout (`WorkspaceLayout`) featuring a persistent left sidebar for navigation, a top header bar, and a main content area. Preserve existing chat functionality as the "Diagnosis" module.

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript strict mode, Tailwind CSS v4, Zustand for state management, assistant-ui for chat, Vitest + React Testing Library for testing.

---

## File Structure Overview

**New Files to Create:**
```
web/src/workspace/
  workspace-layout.tsx              # Main workspace container
  workspace-sidebar.tsx             # Left navigation sidebar
  workspace-header.tsx              # Top header bar
  workspace-store.ts                # Workspace state (Zustand)
  workspace-navigation.ts           # Navigation configuration
  placeholder-page.tsx              # Reusable placeholder component

web/app/workspace/
  layout.tsx                        # Workspace route layout
  page.tsx                          # Redirect to dashboard
  dashboard/page.tsx                # Dashboard module
  diagnosis/page.tsx                # Diagnosis module (chat)
  opportunities/page.tsx            # Opportunities module (placeholder)
  workshop/page.tsx                 # Workshop module (placeholder)
  knowledge/page.tsx                # Knowledge module (placeholder)
  assets/page.tsx                   # Assets module (placeholder)
  mentors/page.tsx                  # Mentors module (placeholder)
  account/page.tsx                  # Account module (placeholder)
```

**Files to Modify:**
```
web/app/chat/page.tsx               # Add redirect to /workspace/diagnosis
web/app/globals.css                 # Add workspace styles
```

**Files to Preserve (No Changes):**
```
web/src/chat/authenticated-chat-page.tsx
web/src/chat/multi-agent-chat-layout.tsx
web/src/chat/chat-store.ts
web/src/chat/agent-sidebar.tsx
web/src/chat/history-panel.tsx
```

---

## Phase 1: Core Workspace Structure

### Task 1.1: Create Workspace State Management

**Goal:** Set up Zustand store for workspace-level state (sidebar collapse, current module).

- [ ] Create `web/src/workspace/workspace-store.ts`
- [ ] Write test: `workspace-store.test.ts` - should initialize with default state
- [ ] Run test: `npm test workspace-store.test.ts` → Expected: FAIL (file doesn't exist)
- [ ] Implement workspace store with interface:
```typescript
interface WorkspaceStore {
  sidebarCollapsed: boolean;
  currentModuleId: string;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCurrentModule: (moduleId: string) => void;
}
```
- [ ] Run test: `npm test workspace-store.test.ts` → Expected: PASS
- [ ] Commit: "feat(workspace): add workspace state management"

**Estimated Time:** 5 minutes

---

### Task 1.2: Create Navigation Configuration

**Goal:** Define the 8 module navigation items in a centralized config file.

- [ ] Create `web/src/workspace/workspace-navigation.ts`
- [ ] Define navigation items array:
```typescript
import { 
  LayoutDashboard, MessageSquare, Radar, Wrench, 
  BookOpen, Archive, Users, Settings 
} from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  badge?: string | number;
}

export const NAVIGATION_ITEMS: NavigationItem[] = [
  { id: 'dashboard', label: '总控台', icon: LayoutDashboard, href: '/workspace/dashboard' },
  { id: 'diagnosis', label: '一人企业诊断', icon: MessageSquare, href: '/workspace/diagnosis' },
  { id: 'opportunities', label: '机会雷达', icon: Radar, href: '/workspace/opportunities' },
  { id: 'workshop', label: '方法论工作坊', icon: Wrench, href: '/workspace/workshop' },
  { id: 'knowledge', label: '知识库', icon: BookOpen, href: '/workspace/knowledge' },
  { id: 'assets', label: '资产库', icon: Archive, href: '/workspace/assets' },
  { id: 'mentors', label: '商业智库', icon: Users, href: '/workspace/mentors' },
  { id: 'account', label: '账户与用量', icon: Settings, href: '/workspace/account' },
];
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Commit: "feat(workspace): add navigation configuration"

**Estimated Time:** 3 minutes

---

### Task 1.3: Create WorkspaceSidebar Component

**Goal:** Build the left navigation sidebar with 8 module links.

- [ ] Create `web/src/workspace/workspace-sidebar.tsx`
- [ ] Write test: `workspace-sidebar.test.tsx` - should render all 8 navigation items
- [ ] Run test: `npm test workspace-sidebar.test.tsx` → Expected: FAIL
- [ ] Implement WorkspaceSidebar component:
```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { NAVIGATION_ITEMS } from './workspace-navigation';
import { useWorkspaceStore } from './workspace-store';
import { cn } from '@/lib/utils';

export function WorkspaceSidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useWorkspaceStore();

  return (
    <aside className={cn('workspace-sidebar', sidebarCollapsed && 'collapsed')}>
      <div className="workspace-sidebar-brand">
        {!sidebarCollapsed && <span>OPC Planet</span>}
        <button
          onClick={toggleSidebar}
          className="workspace-sidebar-toggle"
          aria-label={sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'}
        >
          {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav className="workspace-sidebar-nav">
        {NAVIGATION_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link
              key={item.id}
              href={item.href}
              className={cn('workspace-nav-item', isActive && 'active')}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <Icon className="workspace-nav-icon" size={20} />
              {!sidebarCollapsed && <span>{item.label}</span>}
              {!sidebarCollapsed && item.badge && (
                <span className="workspace-nav-badge">{item.badge}</span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="workspace-sidebar-user">
        <div className="workspace-user-avatar">U</div>
        {!sidebarCollapsed && <span className="workspace-user-name">default-user</span>}
      </div>
    </aside>
  );
}
```
- [ ] Run test: `npm test workspace-sidebar.test.tsx` → Expected: PASS
- [ ] Commit: "feat(workspace): add workspace sidebar component"

**Estimated Time:** 5 minutes

---

### Task 1.4: Create WorkspaceHeader Component

**Goal:** Build the top header bar with module title and actions.

- [ ] Create `web/src/workspace/workspace-header.tsx`
- [ ] Implement WorkspaceHeader component:
```typescript
'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface WorkspaceHeaderProps {
  title: string;
  actions?: ReactNode;
  className?: string;
}

export function WorkspaceHeader({ title, actions, className }: WorkspaceHeaderProps) {
  return (
    <header className={cn('workspace-header', className)}>
      <h1 className="workspace-header-title">{title}</h1>
      {actions && <div className="workspace-header-actions">{actions}</div>}
    </header>
  );
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Commit: "feat(workspace): add workspace header component"

**Estimated Time:** 3 minutes

---

### Task 1.5: Create WorkspaceLayout Component

**Goal:** Build the main layout container that combines sidebar and content.

- [ ] Create `web/src/workspace/workspace-layout.tsx`
- [ ] Implement WorkspaceLayout component:
```typescript
'use client';

import { ReactNode } from 'react';
import { WorkspaceSidebar } from './workspace-sidebar';
import { useWorkspaceStore } from './workspace-store';
import { cn } from '@/lib/utils';

export interface WorkspaceLayoutProps {
  children: ReactNode;
}

export function WorkspaceLayout({ children }: WorkspaceLayoutProps) {
  const sidebarCollapsed = useWorkspaceStore((state) => state.sidebarCollapsed);

  return (
    <div className={cn('workspace-layout', sidebarCollapsed && 'sidebar-collapsed')}>
      <WorkspaceSidebar />
      <div className="workspace-main">{children}</div>
    </div>
  );
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Commit: "feat(workspace): add workspace layout component"

**Estimated Time:** 3 minutes

---

### Task 1.6: Add Workspace Styles to globals.css

**Goal:** Add CSS for workspace layout components.

- [ ] Open `web/app/globals.css`
- [ ] Scroll to line 1113 (before `@theme inline`)
- [ ] Insert the following workspace styles at that location:

```css
/* Workspace Layout Styles */
.workspace-layout {
  display: flex;
  height: 100dvh;
  overflow: hidden;
}

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

.activity-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test in browser: Visit workspace route → Should see styled layout
- [ ] Commit: "style(workspace): add workspace layout styles"

**Estimated Time:** 5 minutes

---

### Task 1.7: Create Workspace Route Layout

**Goal:** Set up Next.js App Router layout for /workspace routes.

- [ ] Create directory: `web/app/workspace/`
- [ ] Create `web/app/workspace/layout.tsx`
- [ ] Implement workspace layout wrapper:
```typescript
import { WorkspaceLayout } from '@/workspace/workspace-layout';
import { ReactNode } from 'react';

export default function WorkspaceRootLayout({ children }: { children: ReactNode }) {
  return <WorkspaceLayout>{children}</WorkspaceLayout>;
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Commit: "feat(workspace): add workspace route layout"

**Estimated Time:** 2 minutes

---

### Task 1.8: Create Workspace Root Page (Redirect)

**Goal:** Create /workspace page that redirects to /workspace/dashboard.

- [ ] Create `web/app/workspace/page.tsx`
- [ ] Implement redirect:
```typescript
import { redirect } from 'next/navigation';

export default function WorkspacePage() {
  redirect('/workspace/dashboard');
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace` → Should redirect to `/workspace/dashboard`
- [ ] Commit: "feat(workspace): add workspace root redirect"

**Estimated Time:** 2 minutes

---

## Phase 2: Dashboard Module

### Task 2.1: Create Dashboard Page

**Goal:** Build the dashboard module with welcome section and metric cards.

- [ ] Create directory: `web/app/workspace/dashboard/`
- [ ] Create `web/app/workspace/dashboard/page.tsx`
- [ ] Implement dashboard page with inline MetricCard and RecentActivity components:

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';

export default function DashboardPage() {
  return (
    <>
      <WorkspaceHeader title="总控台" />
      <div className="workspace-content">
        <div className="dashboard-page">
          <div className="welcome-section">
            <h2>欢迎回来</h2>
            <p>这是您的一人企业运营中心</p>
          </div>

          <div className="metrics-grid">
            <div className="metric-card">
              <h3>企业健康度</h3>
              <p className="metric-value">85%</p>
            </div>
            <div className="metric-card">
              <h3>活跃机会</h3>
              <p className="metric-value">12</p>
            </div>
            <div className="metric-card">
              <h3>知识资产</h3>
              <p className="metric-value">248</p>
            </div>
          </div>

          <div className="activity-card">
            <h3>最近活动</h3>
            <p>暂无活动记录</p>
          </div>
        </div>
      </div>
    </>
  );
}
```

**Note:** MetricCard and RecentActivity are implemented as inline JSX for Phase 1 simplicity. Extract to separate components in future phases if needed.

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test in browser: Visit `/workspace/dashboard` → Should see dashboard with 3 metric cards
- [ ] Commit: "feat(dashboard): add dashboard page with metrics"

**Estimated Time:** 4 minutes

---

## Phase 3: Diagnosis Module Integration

### Task 3.1: Create Diagnosis Module Page

**Goal:** Integrate existing chat functionality into diagnosis module.

- [ ] Create directory: `web/app/workspace/diagnosis/`
- [ ] Create `web/app/workspace/diagnosis/page.tsx`
- [ ] Implement diagnosis page:
```typescript
import { getDefaultChatUser } from '@/auth/session';
import {
  getOrCreateInitialThreadForUser,
  listUserThreads,
} from '@/chat/chat-thread-service';
import { AuthenticatedChatPage } from '@/chat/authenticated-chat-page';

interface DiagnosisPageProps {
  searchParams?: Promise<{ threadId?: string | string[] }>;
}

function toOptionalThreadId(
  value: string | string[] | undefined,
): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function DiagnosisPage({ searchParams }: DiagnosisPageProps) {
  const user = getDefaultChatUser();
  const threads = listUserThreads(user.id);
  const fallbackThread = threads[0] ?? getOrCreateInitialThreadForUser(user.id);
  const resolvedSearchParams: Awaited<NonNullable<DiagnosisPageProps["searchParams"]>> =
    await (
      searchParams ??
      Promise.resolve<{ threadId?: string | string[] }>({})
    );
  const requestedThreadId = toOptionalThreadId(resolvedSearchParams.threadId);
  const initialThreadId = threads.some((thread) => thread.id === requestedThreadId)
    ? requestedThreadId
    : fallbackThread.id;

  return (
    <div className="workspace-content">
      <AuthenticatedChatPage
        initialThreadId={initialThreadId}
        userDisplayName={user.displayName}
      />
    </div>
  );
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/diagnosis` → Should see chat interface
- [ ] Test: Send a message → Should receive response
- [ ] Test: Check history panel → Should show thread history
- [ ] Commit: "feat(diagnosis): integrate chat into diagnosis module"

**Estimated Time:** 5 minutes

---

### Task 3.2: Add Chat Route Redirect

**Goal:** Redirect old /chat route to /workspace/diagnosis for backward compatibility.

- [ ] Open `web/app/chat/page.tsx`
- [ ] Replace entire content with redirect:
```typescript
import { redirect } from 'next/navigation';

interface ChatPageProps {
  searchParams?: Promise<{ threadId?: string | string[] }>;
}

export default async function ChatPage({ searchParams }: ChatPageProps) {
  const resolvedSearchParams = await (searchParams ?? Promise.resolve({}));
  const threadId = Array.isArray(resolvedSearchParams.threadId)
    ? resolvedSearchParams.threadId[0]
    : resolvedSearchParams.threadId;

  const targetUrl = threadId
    ? `/workspace/diagnosis?threadId=${threadId}`
    : '/workspace/diagnosis';

  redirect(targetUrl);
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/chat` → Should redirect to `/workspace/diagnosis`
- [ ] Test: Visit `/chat?threadId=abc123` → Should redirect with threadId preserved
- [ ] Commit: "feat(workspace): add chat route redirect for backward compatibility"

**Estimated Time:** 3 minutes

---

## Phase 4: Placeholder Module Pages

### Task 4.1: Create Placeholder Component

**Goal:** Build reusable placeholder component for modules under development.

- [ ] Create `web/src/workspace/placeholder-page.tsx`
- [ ] Implement PlaceholderPage component:
```typescript
import { ReactNode } from 'react';

export interface PlaceholderPageProps {
  icon: ReactNode;
  title: string;
  description: string;
}

export function PlaceholderPage({ icon, title, description }: PlaceholderPageProps) {
  return (
    <div className="placeholder-page">
      <div className="placeholder-icon">{icon}</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Commit: "feat(workspace): add placeholder page component"

**Estimated Time:** 2 minutes

---

### Task 4.2: Create Opportunities Module Page

**Goal:** Create placeholder page for opportunities module.

- [ ] Create directory: `web/app/workspace/opportunities/`
- [ ] Create `web/app/workspace/opportunities/page.tsx`
- [ ] Implement using PlaceholderPage:
```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { Radar } from 'lucide-react';

export default function OpportunitiesPage() {
  return (
    <>
      <WorkspaceHeader title="机会雷达" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<Radar size={80} />}
          title="机会雷达"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```
- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/opportunities` → Should see placeholder
- [ ] Commit: "feat(opportunities): add opportunities placeholder page"

**Estimated Time:** 2 minutes

---

### Task 4.3: Create Workshop Module Page

**Goal:** Create placeholder page for workshop module.

- [ ] Create directory: `web/app/workspace/workshop/`
- [ ] Create `web/app/workspace/workshop/page.tsx`
- [ ] Implement using PlaceholderPage with Wrench icon (follow exact pattern from Task 4.2):

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { Wrench } from 'lucide-react';

export default function WorkshopPage() {
  return (
    <>
      <WorkspaceHeader title="方法论工作坊" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<Wrench size={80} />}
          title="方法论工作坊"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/workshop` → Should see placeholder
- [ ] Commit: "feat(workshop): add workshop placeholder page"

**Estimated Time:** 2 minutes

---

### Task 4.4: Create Knowledge Module Page

**Goal:** Create placeholder page for knowledge module.

- [ ] Create directory: `web/app/workspace/knowledge/`
- [ ] Create `web/app/workspace/knowledge/page.tsx`
- [ ] Implement using PlaceholderPage with BookOpen icon (follow exact pattern from Task 4.2):

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { BookOpen } from 'lucide-react';

export default function KnowledgePage() {
  return (
    <>
      <WorkspaceHeader title="知识库" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<BookOpen size={80} />}
          title="知识库"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/knowledge` → Should see placeholder
- [ ] Commit: "feat(knowledge): add knowledge placeholder page"

**Estimated Time:** 2 minutes

---

### Task 4.5: Create Assets Module Page

**Goal:** Create placeholder page for assets module.

- [ ] Create directory: `web/app/workspace/assets/`
- [ ] Create `web/app/workspace/assets/page.tsx`
- [ ] Implement using PlaceholderPage with Archive icon (follow exact pattern from Task 4.2):

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { Archive } from 'lucide-react';

export default function AssetsPage() {
  return (
    <>
      <WorkspaceHeader title="资产库" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<Archive size={80} />}
          title="资产库"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/assets` → Should see placeholder
- [ ] Commit: "feat(assets): add assets placeholder page"

**Estimated Time:** 2 minutes

---

### Task 4.6: Create Mentors Module Page

**Goal:** Create placeholder page for mentors module.

- [ ] Create directory: `web/app/workspace/mentors/`
- [ ] Create `web/app/workspace/mentors/page.tsx`
- [ ] Implement using PlaceholderPage with Users icon (follow exact pattern from Task 4.2):

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { Users } from 'lucide-react';

export default function MentorsPage() {
  return (
    <>
      <WorkspaceHeader title="商业智库" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<Users size={80} />}
          title="商业智库"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/mentors` → Should see placeholder
- [ ] Commit: "feat(mentors): add mentors placeholder page"

**Estimated Time:** 2 minutes

---

### Task 4.7: Create Account Module Page

**Goal:** Create placeholder page for account module.

- [ ] Create directory: `web/app/workspace/account/`
- [ ] Create `web/app/workspace/account/page.tsx`
- [ ] Implement using PlaceholderPage with Settings icon (follow exact pattern from Task 4.2):

```typescript
import { WorkspaceHeader } from '@/workspace/workspace-header';
import { PlaceholderPage } from '@/workspace/placeholder-page';
import { Settings } from 'lucide-react';

export default function AccountPage() {
  return (
    <>
      <WorkspaceHeader title="账户与用量" />
      <div className="workspace-content">
        <PlaceholderPage
          icon={<Settings size={80} />}
          title="账户与用量"
          description="此模块正在开发中，敬请期待"
        />
      </div>
    </>
  );
}
```

- [ ] Run typecheck: `npm run typecheck` → Expected: No errors
- [ ] Test: Visit `/workspace/account` → Should see placeholder
- [ ] Commit: "feat(account): add account placeholder page"

**Estimated Time:** 2 minutes

---

## Phase 5: Testing & Verification

### Task 5.1: End-to-End Navigation Testing

**Goal:** Verify all navigation flows work correctly.

- [ ] Test: Click each navigation item in sidebar → Should navigate to correct module
- [ ] Test: Verify URL changes correctly for each module
- [ ] Test: Verify active state highlights correct navigation item
- [ ] Test: Browser back/forward buttons → Should work correctly
- [ ] Test: Direct URL access to each module → Should load correctly
- [ ] Test: Sidebar collapse/expand → Should work smoothly
- [ ] Document any issues found

**Estimated Time:** 5 minutes

---

### Task 5.2: Diagnosis Module Functionality Testing

**Goal:** Verify chat functionality is preserved in diagnosis module.

- [ ] Test: Send message in diagnosis module → Should receive response
- [ ] Test: Create new thread → Should work correctly
- [ ] Test: Switch between threads → Should load correct history
- [ ] Test: Agent selection → Should work correctly
- [ ] Test: History panel → Should show all threads
- [ ] Test: Thread filtering → Should filter correctly
- [ ] Compare with old `/chat` behavior → Should be identical
- [ ] Document any regressions

**Estimated Time:** 5 minutes

---

### Task 5.3: Backward Compatibility Testing

**Goal:** Verify old routes redirect correctly.

- [ ] Test: Visit `/chat` → Should redirect to `/workspace/diagnosis`
- [ ] Test: Visit `/chat?threadId=xxx` → Should preserve threadId in redirect
- [ ] Test: Bookmarked `/chat` URLs → Should still work
- [ ] Test: External links to `/chat` → Should redirect correctly
- [ ] Document any broken links

**Estimated Time:** 3 minutes

---

### Task 5.4: Visual Consistency Check

**Goal:** Verify visual design matches the approved preview.

- [ ] Compare sidebar styling with `workspace-layout-preview.html`
- [ ] Verify colors match: sidebar bg #2a2a2a, accent #10b981
- [ ] Verify spacing and dimensions match preview
- [ ] Verify hover states work correctly
- [ ] Verify active states are visually clear
- [ ] Test in different browser widths
- [ ] Document any visual discrepancies

**Estimated Time:** 4 minutes

---

### Task 5.5: Performance Check

**Goal:** Ensure no performance regressions.

- [ ] Run Lighthouse on `/workspace/dashboard` → Score should be > 90
- [ ] Measure module switching time → Should be < 200ms
- [ ] Measure sidebar collapse animation → Should be smooth (60fps)
- [ ] Compare diagnosis module performance with old `/chat` → Should be similar
- [ ] Check for console errors or warnings
- [ ] Document any performance issues

**Estimated Time:** 4 minutes

---

### Task 5.6: TypeScript & Linting

**Goal:** Ensure code quality standards are met.

- [ ] Run: `npm run typecheck` → Expected: No errors
- [ ] Run: `npm run lint` → Expected: No errors
- [ ] Fix any type errors found
- [ ] Fix any linting errors found
- [ ] Commit: "fix: resolve type and lint errors"

**Estimated Time:** 3 minutes

---

## Phase 6: Documentation & Cleanup

### Task 6.1: Update Code Guide Documentation

**Goal:** Update website_core_code_guide.md with new workspace architecture.

- [ ] Open `docs/guide/website_core_code_guide.md`
- [ ] Locate section 14 (the last numbered section before any appendices)
- [ ] Add a new section "## 15. Workspace Layout Architecture" after section 14
- [ ] Document the following in the new section:
  - **15.1 Overview**: Brief description of workspace layout system and its purpose
  - **15.2 Core Components**: 
    - `WorkspaceLayout` - Main container component
    - `WorkspaceSidebar` - Left navigation with 8 modules
    - `WorkspaceHeader` - Top header bar with module title
  - **15.3 Navigation Configuration**: 
    - Location: `workspace-navigation.ts`
    - Structure of `NavigationItem` interface
    - List of 8 modules with their IDs, labels, icons, and routes
  - **15.4 State Management**:
    - `workspace-store.ts` - Global workspace state (sidebar collapse, current module)
    - Separation from module-specific state (e.g., `chat-store.ts` for diagnosis)
  - **15.5 Module Page Structure**:
    - Standard pattern: `WorkspaceHeader` + `workspace-content` wrapper
    - Dashboard implementation (inline components)
    - Diagnosis integration (preserves existing chat)
    - Placeholder pages (reusable `PlaceholderPage` component)
  - **15.6 Routing Structure**:
    - `/workspace` → redirects to `/workspace/dashboard`
    - `/workspace/[module]` → individual module pages
    - `/chat` → redirects to `/workspace/diagnosis` (backward compatibility)
  - **15.7 Styling**:
    - CSS classes: `.workspace-layout`, `.workspace-sidebar`, `.workspace-nav-item`, etc.
    - Location: `globals.css` (added before `@theme inline`)
    - Key design tokens: sidebar bg `#2a2a2a`, accent `#10b981`
- [ ] Commit: "docs: update code guide with workspace architecture"

**Estimated Time:** 5 minutes

---

### Task 6.2: Final Integration Test

**Goal:** Complete end-to-end user flow test.

- [ ] Test complete user journey:
  1. Visit `/` (public page)
  2. Login (if auth is implemented)
  3. Should land on `/workspace/dashboard`
  4. Click through all 8 modules
  5. Test diagnosis module chat
  6. Test sidebar collapse
  7. Test browser refresh on each module
  8. Test direct URL access
- [ ] Document any issues
- [ ] Fix critical issues before completion

**Estimated Time:** 5 minutes

---

### Task 6.3: Create Summary Report

**Goal:** Document what was implemented and what's next.

- [ ] List all completed tasks
- [ ] List all files created (count: ~20 files)
- [ ] List all files modified (count: ~2 files)
- [ ] Document any deviations from the plan
- [ ] Document any known issues or limitations
- [ ] Suggest next steps for future development
- [ ] Commit: "docs: add workspace redesign implementation summary"

**Estimated Time:** 3 minutes

---

## Success Criteria Checklist

**Functional Completeness:**
- [ ] All 8 modules accessible via sidebar navigation
- [ ] Dashboard shows welcome section and metric cards
- [ ] Diagnosis module preserves all existing chat functionality
- [ ] 6 placeholder modules show "under development" message
- [ ] Sidebar collapse/expand works correctly
- [ ] Active navigation item is highlighted

**Backward Compatibility:**
- [ ] `/chat` redirects to `/workspace/diagnosis`
- [ ] `/chat?threadId=xxx` preserves threadId parameter
- [ ] Existing chat functionality has no regressions
- [ ] Historical thread access works correctly

**User Experience:**
- [ ] Clear module navigation visible on login
- [ ] Module switching is fast (< 200ms)
- [ ] Sidebar animation is smooth
- [ ] Visual design matches approved preview
- [ ] No layout issues or visual bugs

**Code Quality:**
- [ ] TypeScript typecheck passes with no errors
- [ ] All tests pass (if tests were written)
- [ ] No console errors or warnings
- [ ] Code follows project conventions
- [ ] Components are properly typed

**Performance:**
- [ ] Lighthouse score > 90 on dashboard
- [ ] No noticeable performance degradation
- [ ] Module switching is responsive
- [ ] Diagnosis module chat performance unchanged

**Documentation:**
- [ ] Code guide updated with workspace architecture
- [ ] Implementation summary created
- [ ] Code comments are clear and complete

---

## Estimated Total Time

**Phase 1 (Core Structure):** 30 minutes
**Phase 2 (Dashboard):** 4 minutes
**Phase 3 (Diagnosis Integration):** 8 minutes
**Phase 4 (Placeholder Pages):** 14 minutes
**Phase 5 (Testing):** 24 minutes
**Phase 6 (Documentation):** 13 minutes

**Total:** ~93 minutes (~1.5 hours)

---

## Notes for Implementation

**TDD Approach:**
- Write tests first for components with complex logic (store, sidebar)
- For simple presentational components, tests are optional
- Focus on integration tests for user flows

**Commit Strategy:**
- Commit after each completed task
- Use conventional commit messages (feat, fix, style, docs, test)
- Keep commits small and focused

**Testing Strategy:**
- Unit tests for workspace-store
- Component tests for WorkspaceSidebar (navigation rendering)
- Integration tests for diagnosis module (chat functionality)
- Manual testing for visual consistency and user flows

**Rollback Plan:**
- All old code is preserved (no deletions)
- `/chat` route can be restored by removing redirect
- Workspace routes are additive, don't break existing functionality

**Common Pitfalls to Avoid:**
- Don't delete MultiAgentChatLayout - diagnosis module still uses it
- Don't modify chat-store.ts - it's still used by diagnosis module
- Ensure CSS doesn't conflict with existing .multi-agent-* classes
- Test threadId parameter passing carefully in redirects
- Verify sidebar collapse state persists in Zustand store

---

## File Paths Reference

**Created Files:**
```
web/src/workspace/workspace-store.ts
web/src/workspace/workspace-navigation.ts
web/src/workspace/workspace-sidebar.tsx
web/src/workspace/workspace-header.tsx
web/src/workspace/workspace-layout.tsx
web/src/workspace/placeholder-page.tsx
web/app/workspace/layout.tsx
web/app/workspace/page.tsx
web/app/workspace/dashboard/page.tsx
web/app/workspace/diagnosis/page.tsx
web/app/workspace/opportunities/page.tsx
web/app/workspace/workshop/page.tsx
web/app/workspace/knowledge/page.tsx
web/app/workspace/assets/page.tsx
web/app/workspace/mentors/page.tsx
web/app/workspace/account/page.tsx
```

**Modified Files:**
```
web/app/chat/page.tsx
web/app/globals.css
docs/guide/website_core_code_guide.md
```

**Preserved Files (No Changes):**
```
web/src/chat/authenticated-chat-page.tsx
web/src/chat/multi-agent-chat-layout.tsx
web/src/chat/chat-store.ts
web/src/chat/agent-sidebar.tsx
web/src/chat/history-panel.tsx
web/src/chat/agent-info-card.tsx
```

---

**Plan Version:** 1.0  
**Created:** 2026-05-22  
**Status:** Ready for Implementation

---

### Task 1.4: Create WorkspaceHeader Component
