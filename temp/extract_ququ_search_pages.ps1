param(
  [int]$StartPage = 2,
  [int]$EndPage = 5
)

$ErrorActionPreference = 'Continue'
$outDir = 'data/raw/bilibili/subtitles/ququ-business-search-2026-04-26'
$cookiePath = 'C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt'
$keywordEncoded = '%E6%9B%B2%E6%9B%B2%20%E5%95%86%E4%B8%9A'
$strongRelevancePattern = '商业|赚钱|销售|创业|生意|产品|流量|客户|市场|行业|商业模式|商业逻辑|商业闭环|社会运行|游戏规则|变现|成交|定价|公司|消费|品牌|营销|经营|项目|赛道|盈利|利润|成本|需求|有钱人|老板'
$negativePattern = '情感|挽回|男友|女友|男人|女人|关系|闺蜜|老婆|老公|白富美|凤凰|结婚|恋爱|分手|婚姻'

New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$cookie = (Get-Content -Raw $cookiePath).Trim()
$headers = @{
  'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  'Referer' = 'https://search.bilibili.com/'
  'Cookie' = $cookie
}

$seen = @{}
Get-ChildItem $outDir -Filter '*.metadata.json' -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.BaseName -match '^(BV[0-9A-Za-z]{10})-') {
    $seen[$matches[1]] = $true
  }
}
Get-ChildItem $outDir -Filter '*summary.json' -ErrorAction SilentlyContinue | ForEach-Object {
  try {
    $items = Get-Content -Raw $_.FullName | ConvertFrom-Json
    foreach ($item in @($items)) {
      if ($item.bvid) {
        $seen[[string]$item.bvid] = $true
      }
    }
  } catch {
  }
}

$catalog = @()
$results = @()

for ($page = $StartPage; $page -le $EndPage; $page++) {
  Write-Host "### search page $page"
  Start-Sleep -Milliseconds 1200
  $uri = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=$keywordEncoded&page=$page&page_size=20"
  try {
    $resp = Invoke-WebRequest -Uri $uri -Headers $headers -UseBasicParsing
    $json = $resp.Content | ConvertFrom-Json
  } catch {
    $results += [pscustomobject]@{
      page = $page
      bvid = $null
      title = $null
      author = $null
      relevant = $false
      decision_reason = 'search_fetch_error'
      status = 'error'
      reason = $_.Exception.Message
      text_path = $null
      metadata_path = $null
    }
    continue
  }

  $index = 0
  foreach ($video in @($json.data.result)) {
    $index++
    $title = [System.Net.WebUtility]::HtmlDecode(([string]$video.title -replace '<[^>]+>', ''))
    $bvid = [string]$video.bvid
    $author = [string]$video.author
    $hasStrongBusinessSignal = $title -match $strongRelevancePattern
    $hasNegativeSignal = $title -match $negativePattern
    $isRelevant = $hasStrongBusinessSignal -and -not ($hasNegativeSignal -and -not ($title -match '商业|赚钱|销售|创业|生意|经营|产品|市场|客户|行业|品牌|变现'))
    $decisionReason = if ($isRelevant) { 'title_matches_business_literacy_keywords' } elseif ($hasNegativeSignal) { 'excluded_relationship_or_emotion_title' } else { 'title_not_business_literacy_by_title' }
    $catalogItem = [pscustomobject]@{
      page = $page
      index = $index
      bvid = $bvid
      author = $author
      title = $title
      duration = [string]$video.duration
      play = $video.play
      relevant = $isRelevant
      decision_reason = $decisionReason
    }
    $catalog += $catalogItem

    if (-not $isRelevant) {
      $results += [pscustomobject]@{
        page = $page
        bvid = $bvid
        title = $title
        author = $author
        relevant = $false
        decision_reason = $decisionReason
        status = 'skipped'
        reason = 'not_relevant_by_title'
        text_path = $null
        metadata_path = $null
      }
      continue
    }

    if ($seen.ContainsKey($bvid)) {
      $results += [pscustomobject]@{
        page = $page
        bvid = $bvid
        title = $title
        author = $author
        relevant = $true
        decision_reason = $decisionReason
        status = 'skipped'
        reason = 'duplicate_already_processed'
        text_path = $null
        metadata_path = $null
      }
      continue
    }

    Write-Host "download $bvid page=$page title=$title"
    $output = & python -m automation.extractors.bilibili_subtitle $bvid --cookie-file $cookiePath --output-dir $outDir 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | Out-String).Trim()
    Write-Host $text
    try {
      $obj = $text | ConvertFrom-Json
    } catch {
      $obj = [pscustomobject]@{
        bvid = $bvid
        status = 'error'
        reason = $text
        title = $title
        owner_name = $author
        text_path = $null
        metadata_path = $null
      }
    }

    $results += [pscustomobject]@{
      page = $page
      bvid = $bvid
      title = if ($obj.title) { $obj.title } else { $title }
      author = if ($obj.owner_name) { $obj.owner_name } else { $author }
      relevant = $true
      decision_reason = $decisionReason
      exit_code = $exitCode
      status = $obj.status
      reason = $obj.reason
      text_path = $obj.text_path
      metadata_path = $obj.metadata_path
    }
    $seen[$bvid] = $true
    Start-Sleep -Milliseconds 700
  }
}

$catalogPath = Join-Path $outDir ("search-pages-{0}-{1}-catalog.json" -f $StartPage, $EndPage)
$summaryPath = Join-Path $outDir ("search-pages-{0}-{1}-summary.json" -f $StartPage, $EndPage)
$catalog | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $catalogPath
$results | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $summaryPath

Write-Host "catalog=$catalogPath"
Write-Host "summary=$summaryPath"
$results | Group-Object status,reason | Select-Object Count,Name | Format-Table -AutoSize
