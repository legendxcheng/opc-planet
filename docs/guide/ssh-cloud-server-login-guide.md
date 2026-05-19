---
title: SSH 云服务器登录最小指南
type: guide
status: active
tags: [ssh, server]
created: 2026-05-13
updated: 2026-05-13
source: internal-ops
confidence: high
---

# SSH 云服务器登录最小指南

## Summary

已验证可成功登录：

- 主机：`43.139.125.47`
- 用户：`ubuntu`
- 私钥：`E:\opc-planet\keys\opc.pem`

不可用用户：

- `root`
- `centos`
- `admin`

## 直接登录

```powershell
ssh -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47
```

## 无交互验证

```powershell
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ConnectTimeout=10 -i "E:\opc-planet\keys\opc.pem" ubuntu@43.139.125.47 "echo SSH_OK"
```

成功输出：

```text
SSH_OK
```

## 如果私钥权限报错

如果看到这类错误：

```text
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions for 'E:\opc-planet\keys\opc.pem' are too open.
Load key "E:\opc-planet\keys\opc.pem": bad permissions
```

执行：

```powershell
$path = "E:\opc-planet\keys\opc.pem"
icacls $path /inheritance:r
icacls $path /remove:g "NT AUTHORITY\Authenticated Users" "BUILTIN\Users" "XC\CodexSandboxUsers"
icacls $path /grant:r "XC\Administrator:R" "BUILTIN\Administrators:F" "NT AUTHORITY\SYSTEM:F"
icacls $path
```

然后重试登录命令。
