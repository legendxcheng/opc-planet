# B站 UP 主视频文案下载指南

## Summary

本指南记录如何使用仓库已有工具 `automation.extractors.bilibili_subtitle` 批量下载某个 B 站 UP 主公开视频中的字幕文案。核心流程是：准备登录 Cookie → 用 `--creator` 批量提取 → 检查 summary → 把 raw 字幕整理进 `sources/videos/bilibili/`。

## 适用场景

- 学习、研究公开视频文案结构。
- 批量下载某个 UP 主公开视频已有的 B 站字幕。
- 把字幕作为知识库来源，后续再筛选、提炼、整理。

## 不适用场景

- 下载视频本体。
- 绕过付费、私密、未公开内容。
- 获取没有字幕的视频文案；本工具只下载 B 站已有字幕轨道。
- 把 Cookie、账号凭证或私密数据写进仓库。

## 准备 Cookie

批量下载 UP 主视频列表通常需要登录态。浏览器已登录不等于 Python 命令行已登录，因此需要把 Cookie 放到本地文件里。

推荐路径：

```powershell
C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt
```

要求：

- 文件只放在本机，不要提交到 Git。
- 不要把 Cookie 内容发到聊天里。
- Cookie 至少应包含类似 `SESSDATA`、`bili_jct`、`DedeUserID` 的字段。

## 批量下载某个 UP 主文案

命令格式：

```powershell
python -m automation.extractors.bilibili_subtitle <UP主空间URL或mid> `
  --creator `
  --cookie-file <本地Cookie文件> `
  --output-dir data/raw/bilibili/subtitles/<mid> `
  --summary-path data/raw/bilibili/subtitles/<mid>/creator-<mid>-summary.json `
  --page-size 30
```

示例：

```powershell
python -m automation.extractors.bilibili_subtitle https://space.bilibili.com/1900638792/upload/video `
  --creator `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt `
  --output-dir data/raw/bilibili/subtitles/1900638792 `
  --summary-path data/raw/bilibili/subtitles/1900638792/creator-1900638792-summary.json `
  --page-size 30
```

## 下载单个视频文案

如果只需要某个 BV 视频：

```powershell
python -m automation.extractors.bilibili_subtitle BV1xxxxxxxxx `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt `
  --output-dir data/raw/bilibili/subtitles/<mid>
```

也可以先只检查字幕是否可用：

```powershell
python -m automation.extractors.bilibili_subtitle BV1xxxxxxxxx `
  --check-only `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt
```

## 输出文件说明

默认输出在：

```powershell
data/raw/bilibili/subtitles/<mid>/
```

每个成功下载的视频会生成三类文件：

- `<BV>-<lang>.raw.json`：B 站原始字幕 JSON。
- `<BV>-<lang>.txt`：纯文本字幕，一行一个字幕片段。
- `<BV>-<lang>.metadata.json`：视频与字幕元数据。

批量下载会额外生成：

- `creator-<mid>-summary.json`：UP 主视频列表、每个视频下载状态、成功/失败统计。

## 检查下载结果

用下面命令查看统计：

```powershell
$summary = Get-Content -Raw data/raw/bilibili/subtitles/<mid>/creator-<mid>-summary.json | ConvertFrom-Json
"total=$($summary.total) downloaded=$($summary.downloaded) unavailable=$($summary.unavailable) error=$($summary.error)"
```

查看每条视频状态：

```powershell
$summary.results | Select-Object bvid,title,status,reason,text_path | Format-Table -AutoSize
```

常见状态：

- `downloaded`：字幕已成功下载。
- `no_subtitle_tracks`：视频没有字幕轨道。
- `login_required_or_unavailable`：需要登录、字幕不可用或权限不足。
- `subtitle_url_missing`：接口返回了字幕元数据，但没有可下载 URL。

## 整理进知识库来源

下载到 `data/raw/` 后，不要直接把 raw 数据当成知识结论。建议再整理到：

```powershell
sources/videos/bilibili/<creator-slug>/
```

推荐结构：

- `README.md`：来源索引、适合沉淀的主题、不适合沉淀的主题、处理记录。
- `all-transcripts.md`：已下载字幕合集。
- `001-<BV>-<title>.md`：单个视频字幕整理版。

后续再从 `sources/` 提炼到：

```powershell
knowledge/<domain>/
```

整理原则：

- `sources/` 保存来源与文案。
- `knowledge/` 只保存经过筛选的可复用结论。
- 不要把夸张标题、情绪化表达、未经验证的赚钱承诺直接写成知识库原则。

## 常见问题

### `Bilibili nav API failed: -101 账号未登录`

Python 工具没有拿到登录态。解决方法：加 `--cookie-file`，并确认 Cookie 文件内容有效。

### 浏览器已经登录，为什么 Python 还是未登录？

浏览器登录态存在浏览器 profile 里，Python 命令行不会自动读取。必须显式传入 `--cookie-file` 或设置 `BILIBILI_COOKIE` 环境变量。

### `412 Precondition Failed`

B 站接口风控或请求头/登录态不足。优先使用本工具的 `--creator` 模式和有效 Cookie，不要手写接口请求。

### 有些视频为什么下载不到字幕？

公开视频不一定有字幕。直播回放、较新视频、权限受限视频或接口只返回空字幕 URL 时，工具会记录为 `unavailable`。

### 可以把 Cookie 放进仓库吗？

不可以。Cookie 属于账号凭证，只能放在本机私有路径，例如 `C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt`。

## 本次经验记录

对 `https://space.bilibili.com/1900638792/upload/video` 使用有效 Cookie 后，工具成功读取 UP 主 `边大娘FM` 的公开视频列表：

- 总视频数：59
- 成功下载字幕：45
- 不可用：14
- 输出目录：`data/raw/bilibili/subtitles/1900638792/`
- 汇总文件：`data/raw/bilibili/subtitles/1900638792/creator-1900638792-summary.json`

