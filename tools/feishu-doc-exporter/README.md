# Feishu Doc Exporter

Local CLI for exporting one Feishu document URL to a Markdown file under `sources/dbs-feishu/`.

## Usage

```bash
node tools/feishu-doc-exporter/src/export.mjs "https://..."
```

## What it does

- Opens Chrome in a persistent profile.
- Loads the cloud-document-converter extension unpacked from `temp/cloud-document-converter/`.
- Lets you log into Feishu once, then reuses that profile on later runs.
- Clicks the extension's copy action, reads Markdown from the clipboard, and saves it as `.md`.

## Environment variables

- `FEISHU_DOC_EXPORTER_CHROME`: override the Chrome executable path.
- `FEISHU_DOC_EXPORTER_CONVERTER_REPO`: override the converter repository path.
- `FEISHU_DOC_EXPORTER_OUTPUT_DIR`: override the output directory.
- `FEISHU_DOC_EXPORTER_REBUILD_EXTENSION=1`: force rebuild of the extension cache.
