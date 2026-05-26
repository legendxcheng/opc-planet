---
title: Supabase 风格深色设计系统
type: spec
status: approved
tags: [web, design-system, ui, dark-theme, supabase]
created: 2026-05-24
updated: 2026-05-24
author: brainstorming
confidence: high
---

# Supabase 风格深色设计系统

## 概述

统一 OPC 网站的设计系统，采用 Supabase 风格的深色主题，全面规范化配色、间距、圆角、阴影、字体大小等设计元素。

## 目标

1. **移除浅色主题**：简化维护，仅保留深色主题
2. **统一配色方案**：使用 Supabase 标志性的深灰背景 + 绿色品牌色
3. **规范化设计 Token**：建立系统化的间距、圆角、阴影、字体大小体系
4. **提升一致性**：消除硬编码值，统一所有组件样式
5. **改善可访问性**：确保高对比度和良好的视觉层次

## 设计决策

### 主题策略

**决策**：仅保留深色主题，移除浅色主题支持

**理由**：
- 简化维护成本，减少 CSS 变量和主题切换逻辑
- Supabase 风格以深色主题为核心
- 用户明确要求仅使用深色主题

### 配色方案

#### 背景色系统（分层设计）

```css
--background-primary: #0a0a0a;    /* 主背景 */
--background-secondary: #1a1a1a;  /* 卡片、面板 */
--background-tertiary: #2a2a2a;   /* 悬停状态 */
--background-elevated: #333333;   /* 弹出层、模态框 */
```

#### 品牌色

```css
--brand-primary: #3ECF8E;         /* Supabase 绿 */
--brand-hover: #34B77C;           /* 悬停状态 */
--brand-active: #2A9D6A;          /* 激活状态 */
```

#### 文字色系统

```css
--text-primary: #e5e5e5;          /* 主要文字 */
--text-secondary: #a3a3a3;        /* 次要文字 */
--text-tertiary: #737373;         /* 辅助文字 */
--text-disabled: #525252;         /* 禁用状态 */
```

#### 边框和分隔线

```css
--border-primary: rgba(255, 255, 255, 0.1);
--border-secondary: rgba(255, 255, 255, 0.05);
```

#### 语义色

```css
--success: #10b981;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

### 间距系统

基于 4px 基准单位：

```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
--spacing-3xl: 64px;
```

### 圆角系统

```css
--radius-sm: 4px;    /* 小元素：标签、徽章 */
--radius-md: 8px;    /* 中等元素：按钮、输入框 */
--radius-lg: 12px;   /* 大元素：卡片 */
--radius-xl: 16px;   /* 超大元素：容器 */
--radius-full: 9999px; /* 圆形：头像 */
```

### 阴影系统

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
```

### 字体大小系统

使用 Tailwind 标准尺寸：

```css
--text-xs: 12px;
--text-sm: 14px;
--text-base: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 30px;
--text-4xl: 36px;
```

## 实施架构

### 层次结构

```
Token 层（CSS 变量）
  ↓
Tailwind 配置层
  ↓
组件层（CVA + Tailwind classes）
  ↓
应用层（页面和布局）
```

### 实施步骤

1. **清理浅色主题**
   - 移除 `.dark` 类相关的 CSS 变量
   - 移除主题切换逻辑和 UI
   - 简化 `globals.css` 中的变量定义

2. **更新 CSS 变量**
   - 在 `web/app/globals.css` 中定义新的深色主题变量
   - 使用 Supabase 风格的配色方案
   - 建立规范的间距、圆角、阴影、字体大小变量

3. **创建 Tailwind 配置**
   - 创建 `web/tailwind.config.ts`
   - 将 CSS 变量映射到 Tailwind theme
   - 配置自定义颜色、间距、圆角等

4. **替换硬编码值**
   - 扫描 `globals.css` 中的硬编码颜色值
   - 替换为 CSS 变量引用
   - 统一工作区样式（`.workspace-*`）
   - 统一多代理聊天样式（`.multi-agent-*`）

5. **更新组件样式**
   - 审查 `web/components/` 下的所有组件
   - 确保使用 Tailwind classes 而非硬编码值
   - 统一按钮、卡片、输入框等组件的视觉风格

6. **验证和测试**
   - 视觉回归测试
   - 可访问性测试（对比度检查）
   - 响应式布局测试

### 关键文件

**需要修改的文件**：
- `web/app/globals.css` - 主要的 CSS 变量定义
- `web/tailwind.config.ts` - 新建，Tailwind 配置
- `web/postcss.config.mjs` - 可能需要更新
- `web/components/ui/*` - 所有 UI 组件
- `web/src/workspace/*` - 工作区相关组件
- `web/src/chat/*` - 聊天相关组件

**需要审查的模式**：
- 硬编码的颜色值（`#xxx`, `rgb()`, `rgba()`）
- 硬编码的间距值（`8px`, `16px` 等）
- 硬编码的圆角值（`border-radius: 10px` 等）
- 硬编码的阴影值（`box-shadow: ...`）

## 设计原则

1. **一致性优先**：所有组件使用统一的设计 token
2. **可维护性**：通过 CSS 变量集中管理，便于后续调整
3. **可访问性**：确保文字对比度符合 WCAG AA 标准
4. **性能**：使用 CSS 变量而非 JavaScript 主题切换
5. **渐进增强**：保持现有功能，仅改进视觉呈现

## 成功标准

- ✅ 所有页面使用统一的深色主题
- ✅ 无硬编码的颜色、间距、圆角、阴影值
- ✅ 所有组件视觉风格一致
- ✅ 文字对比度符合 WCAG AA 标准
- ✅ 响应式布局正常工作
- ✅ 无视觉回归问题

## 风险和缓解

**风险**：大规模样式修改可能导致视觉回归

**缓解**：
- 分步实施，先更新 token，再更新组件
- 每步完成后进行视觉检查
- 保留 git 历史，便于回滚

**风险**：移除浅色主题可能影响部分用户

**缓解**：
- 用户明确要求仅使用深色主题
- 如需恢复，可通过 git 历史找回相关代码

## 参考

- Supabase 设计系统：https://supabase.com
- Tailwind CSS 文档：https://tailwindcss.com
- WCAG 对比度标准：https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
