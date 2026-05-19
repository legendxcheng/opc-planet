# Feishu Doc Exporter Guide

## 作用

把单个飞书文档 URL 导出成本地 `.md` 文件，默认保存到 `sources/dbs-feishu/`。

## 首次准备

在仓库根目录执行：

```bash
cd tools/feishu-doc-exporter
npm install
npm run install:chromium
```

## 单次导出

```bash
node src/export.mjs "https://j8v8p5qtm3.feishu.cn/docx/xxxx"
```

也可以显式指定：

```bash
node src/export.mjs --url "https://..." --output-dir "E:\\opc-planet\\sources\\dbs-feishu"
```

## 第一次登录

- 脚本会打开一个持久化 Chromium 窗口。
- 如果你还没登录飞书，就在这个窗口里登录一次。
- 登录成功后，脚本会自动继续导出。
- 后续再跑同一工具时，会复用本地登录态，不需要重复登录。

## 输出规则

- 默认输出目录：`sources/dbs-feishu/`
- 默认文件名：按飞书页面标题清洗后生成
- 如果同名文件已存在，会自动追加后缀，避免覆盖

## 常用环境变量

- `FEISHU_DOC_EXPORTER_OUTPUT_DIR`：覆盖输出目录
- `FEISHU_DOC_EXPORTER_PROFILE_DIR`：覆盖持久化浏览器目录
- `FEISHU_DOC_EXPORTER_CACHE_DIR`：覆盖扩展缓存目录
- `FEISHU_DOC_EXPORTER_CONVERTER_REPO`：覆盖 `cloud-document-converter` 仓库路径
- `FEISHU_DOC_EXPORTER_REBUILD_EXTENSION=1`：强制重建扩展缓存
- `FEISHU_DOC_EXPORTER_CHROME`：指定系统 Chrome 路径
- `FEISHU_DOC_EXPORTER_PNPM`：指定包管理器命令，不设置时自动尝试 `pnpm` / `corepack`

## 常见问题

### 页面打开了，但没导出

- 先确认飞书已经登录。
- 确认页面是飞书文档正文页，不是空白页或重定向页。
- 如果扩展缓存损坏，可以删掉 `tools/feishu-doc-exporter/.cache/` 后重跑。

### 导出的内容不完整

- 先等文档完全加载。
- 重新运行一次，让脚本重新打开页面并等待正文就绪。

### 文件名太怪

- 工具会清理零宽字符和飞书标题后缀。
- 如果还是不满意，可以直接用 `--output-dir` 放到你想要的位置后手改文件名。
