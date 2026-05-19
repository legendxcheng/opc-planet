$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$deployScript = Join-Path $repoRoot "tools\deploy-web.ps1"

function Assert-Contains {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Content,

        [Parameter(Mandatory = $true)]
        [string] $Needle,

        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    if (-not $Content.Contains($Needle)) {
        throw "Missing required deployment marker: $Label ($Needle)"
    }
}

if (-not (Test-Path -LiteralPath $deployScript)) {
    throw "Deployment script does not exist: $deployScript"
}

$content = Get-Content -Raw -LiteralPath $deployScript

Assert-Contains -Content $content -Needle "ssh" -Label "SSH execution"
Assert-Contains -Content $content -Needle "checkout --force" -Label "Git release checkout"
Assert-Contains -Content $content -Needle "npm ci" -Label "dependency install"
Assert-Contains -Content $content -Needle "npm run typecheck" -Label "typecheck gate"
Assert-Contains -Content $content -Needle "npm test" -Label "test gate"
Assert-Contains -Content $content -Needle "npm run build" -Label "build gate"
Assert-Contains -Content $content -Needle "service_name=`"opc-website`"" -Label "systemd service name"
Assert-Contains -Content $content -Needle "systemctl restart" -Label "systemd restart"
Assert-Contains -Content $content -Needle "/etc/nginx/sites-available/opc-website" -Label "Nginx site config"
Assert-Contains -Content $content -Needle "/srv/opc-website" -Label "default app root"
Assert-Contains -Content $content -Needle "web.env" -Label "shared env file"
Assert-Contains -Content $content -Needle "OPC_METADATA_DB_PATH" -Label "persistent metadata path"
Assert-Contains -Content $content -Needle "releases_to_keep" -Label "release retention"

Write-Host "deploy-web.ps1 static checks passed"
