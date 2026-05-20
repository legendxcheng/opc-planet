---
title: Web Git 发布部署指南
type: guide
status: active
tags: [web, deploy, nextjs, systemd, nginx]
created: 2026-05-19
updated: 2026-05-19
source: internal-ops
confidence: high
---

# Web Git 发布部署指南

## Summary

`web/` 是独立的 Next.js 项目，首版生产部署采用 Git 发布、服务器本地构建、`systemd` 常驻进程和 Nginx 反向代理。Docker 暂不作为第一步，因为当前云服务器已经安装 Node.js、npm 和 Nginx，而 Docker 尚未安装；单服务 Next.js 应用先用 systemd 更轻、更直接，也方便排查。

SSH 登录信息见 `docs/guide/ssh-cloud-server-login-guide.md`。

## 部署模型

```text
本机 web/ 提交并推送
  -> tools/deploy-web.ps1
  -> SSH ubuntu@43.139.125.47
  -> /srv/opc-website/repo-cache 拉取 Git
  -> 可选从根仓库同步 knowledge/sources/outputs/agent
  -> /srv/opc-website/releases/<timestamp>-<commit> 构建
  -> /srv/opc-website/current 原子切换
  -> systemctl restart opc-website
  -> Nginx 80 -> 127.0.0.1:3000
```

持久化目录：

- `/srv/opc-website/shared/web.env`：服务器运行时环境变量，不进 Git。
- `/srv/opc-website/shared/data/opc-metadata.sqlite`：SQLite metadata。

## 首次部署

先确保本地 `web/` 的代码已经提交并推送到远端仓库：

```powershell
git -C web status --short
git -C web push origin master
```

首次发布时带 `-SetupServer`，脚本会创建目录、生成默认 `web.env`、写入 systemd unit、写入 Nginx 站点并执行一次完整发布：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 -SetupServer
```

如果服务器上还没有 `opc-website.service`，不带 `-SetupServer` 的发布会提前失败。

如果部署的是独立 `opc-website` 子仓库，还需要把根仓库中的公共知识目录同步到 release 中，否则本地知识检索会没有语料：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 `
  -SetupServer `
  -RepoUrl "git@git.weixin.qq.com:legendxcheng/opc-website.git" `
  -KnowledgeRepoUrl "https://github.com/legendxcheng/opc-planet.git"
```

首次脚本完成后，登录服务器编辑运行时密钥：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "nano /srv/opc-website/shared/web.env"
```

至少检查这些值：

```bash
CODEX_API_KEY=
OPENAI_AGENTS_API_KEY=
OPENAI_AGENTS_BASE_URL=https://api.openai.com/v1
OPENAI_AGENTS_MODEL=
OPENAI_AGENTS_MODEL_REASONING_EFFORT=medium
OPENAI_AGENTS_PROXY_URL=

CODEX_BASE_URL=
CODEX_MODEL=

OPENAI_VECTOR_STORE_API_KEY=
OPENAI_VECTOR_STORE_BASE_URL=https://api.openai.com/v1

PUBLIC_CHAT_FORCE_MOCK=0
OPC_METADATA_DB_PATH=/srv/opc-website/shared/data/opc-metadata.sqlite
```

保存后重启：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "sudo systemctl restart opc-website"
```

## 日常发布

本地完成开发后：

```powershell
cd web
npm run typecheck
npm test
npm run build
git status --short
git add .
git commit -m "feat: your change"
git push origin master
cd ..
```

发布到服务器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1
```

当前推荐的实际发布命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 `
  -RepoUrl "git@git.weixin.qq.com:legendxcheng/opc-website.git" `
  -KnowledgeRepoUrl "https://github.com/legendxcheng/opc-planet.git"
```

发布脚本默认会在服务器上重新执行：

- `npm ci`
- `npm run typecheck`
- `npm test`
- `npm run build`
- `systemctl restart opc-website`

构建或测试失败时，脚本不会切换 `/srv/opc-website/current`。

## 指定分支或版本

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 -Ref master
```

`-Ref` 可以是分支名、tag 或 commit。

## 查看状态和日志

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "systemctl status opc-website --no-pager"
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "journalctl -u opc-website -n 120 --no-pager"
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "tail -n 120 /var/log/nginx/opc-website.error.log"
```

健康检查：

```powershell
Invoke-WebRequest -Uri "http://43.139.125.47/healthz"
Invoke-WebRequest -Uri "http://43.139.125.47/"
```

## 回滚

查看历史 release：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "ls -1dt /srv/opc-website/releases/* | head"
```

切回某个旧版本：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "ln -sfn /srv/opc-website/releases/<release-name> /srv/opc-website/current && sudo systemctl restart opc-website"
```

默认只保留最近 5 个 release。需要更多时：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 -ReleasesToKeep 10
```

## 常见问题

### 服务器拉不到 Git 仓库

如果 Git 远端需要认证，需要先在服务器配置仓库访问凭据，或改用服务器可读的部署仓库 URL：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\deploy-web.ps1 -RepoUrl "https://example.com/opc-website.git"
```

### 已推送但发布不是最新代码

检查本地子模块和远端状态：

```powershell
git -C web status --short --branch
git -C web log -1 --oneline
```

发布脚本只部署远端 Git 中已有的提交，不会同步本地未提交改动。

### 网站仍然返回本地 fallback

先确认服务器已经部署到包含 OpenAI Agents SDK 的提交：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "cd /srv/opc-website/current && git rev-parse --short HEAD && grep -R 'knowledgeSearchPerformed' -n src/chat/public-agent.ts"
```

再确认服务器运行时环境变量已设置：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "grep -E '^(OPENAI_AGENTS_API_KEY|OPENAI_AGENTS_BASE_URL|OPENAI_AGENTS_MODEL|OPENAI_AGENTS_PROXY_URL)=' /srv/opc-website/shared/web.env"
```

如果日志出现 `OpenAI Agents SDK 调用失败：Connection error.`，说明服务器连不上 `OPENAI_AGENTS_BASE_URL`。在服务器上验证：

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "curl -sS -o /tmp/openai-models.out -w 'http_code=%{http_code} time=%{time_total}\n' --connect-timeout 10 --max-time 20 https://api.openai.com/v1/models"
```

如果超时或 DNS 异常，使用服务器能访问的 OpenAI-compatible `/v1` relay 配到 `OPENAI_AGENTS_BASE_URL`，或者在服务器上配置 `OPENAI_AGENTS_PROXY_URL` / `HTTPS_PROXY` / `HTTP_PROXY` 后重启 `opc-website`。

### 是否要用 Docker

第一版先不用 Docker。当前项目是单个 Next.js 服务，服务器已有 Node.js 和 Nginx，systemd 部署能更快获得可运行、可回滚、容易排障的发布链路。

后续出现以下情况再切 Docker Compose：

- 需要同时部署 Web、worker、Postgres、Redis 等多服务。
- 需要固定 Node/npm/系统依赖版本，减少服务器漂移。
- 需要从 CI 构建镜像并跨机器发布。
- 需要蓝绿发布或更严格的容器隔离。
