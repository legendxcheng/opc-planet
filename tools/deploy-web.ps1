[CmdletBinding()]
param(
    [string] $HostName = "43.139.125.47",
    [string] $User = "ubuntu",
    [string] $KeyPath = "",
    [string] $RepoUrl = "https://git.weixin.qq.com/legendxcheng/opc-website.git",
    [string] $Ref = "master",
    [string] $KnowledgeRepoUrl = "",
    [string] $KnowledgeRef = "master",
    [string] $KnowledgeArchivePath = "",
    [string] $GitSshCommand = "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i ~/.ssh/opc_website_deploy",
    [string] $AppRoot = "/srv/opc-website",
    [int] $Port = 3000,
    [string] $Domain = "_",
    [int] $ReleasesToKeep = 5,
    [switch] $SetupServer,
    [switch] $SkipTests,
    [switch] $SkipBuild
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($KeyPath)) {
    $KeyPath = Join-Path (Split-Path $PSScriptRoot -Parent) "keys\opc.pem"
}

function ConvertTo-BashSingleQuoted {
    param([AllowNull()][string] $Value)

    if ($null -eq $Value) {
        return "''"
    }

    return "'" + ($Value -replace "'", "'`"`"'" ) + "'"
}

function ConvertTo-RemoteFlag {
    param([bool] $Value)

    if ($Value) {
        return "1"
    }

    return "0"
}

$resolvedKeyPath = Resolve-Path -LiteralPath $KeyPath
$target = "$User@$HostName"

$sshArgs = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-i", $resolvedKeyPath.Path,
    $target
)

$scpArgs = @(
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=NUL",
    "-i", $resolvedKeyPath.Path
)

$remoteEnv = @(
    "APP_ROOT=$(ConvertTo-BashSingleQuoted $AppRoot)",
    "REPO_URL=$(ConvertTo-BashSingleQuoted $RepoUrl)",
    "DEPLOY_REF=$(ConvertTo-BashSingleQuoted $Ref)",
    "KNOWLEDGE_REPO_URL=$(ConvertTo-BashSingleQuoted $KnowledgeRepoUrl)",
    "KNOWLEDGE_REF=$(ConvertTo-BashSingleQuoted $KnowledgeRef)",
    "DEPLOY_GIT_SSH_COMMAND=$(ConvertTo-BashSingleQuoted $GitSshCommand)",
    "APP_PORT=$Port",
    "SERVER_NAME=$(ConvertTo-BashSingleQuoted $Domain)",
    "RELEASES_TO_KEEP=$ReleasesToKeep",
    "SETUP_SERVER=$(ConvertTo-RemoteFlag $SetupServer.IsPresent)",
    "SKIP_TESTS=$(ConvertTo-RemoteFlag $SkipTests.IsPresent)",
    "SKIP_BUILD=$(ConvertTo-RemoteFlag $SkipBuild.IsPresent)"
) -join " "

$remoteCommand = "$remoteEnv bash -s"
$remoteKnowledgeArchivePath = ""

$remoteScript = @'
set -Eeuo pipefail

app_root="${APP_ROOT:-/srv/opc-website}"
repo_url="${REPO_URL:?REPO_URL is required}"
deploy_ref="${DEPLOY_REF:-master}"
knowledge_repo_url="${KNOWLEDGE_REPO_URL:-}"
knowledge_ref="${KNOWLEDGE_REF:-master}"
deploy_git_ssh_command="${DEPLOY_GIT_SSH_COMMAND:-}"
app_port="${APP_PORT:-3000}"
server_name="${SERVER_NAME:-_}"
setup_server="${SETUP_SERVER:-0}"
skip_tests="${SKIP_TESTS:-0}"
skip_build="${SKIP_BUILD:-0}"
releases_to_keep="${RELEASES_TO_KEEP:-5}"

shared_dir="${app_root}/shared"
releases_dir="${app_root}/releases"
repo_cache="${app_root}/repo-cache"
knowledge_repo_cache="${app_root}/knowledge-repo-cache"
current_link="${app_root}/current"
env_file="${shared_dir}/web.env"
data_dir="${shared_dir}/data"
codex_home="${shared_dir}/codex-home"
service_name="opc-website"
service_file="/etc/systemd/system/${service_name}.service"
nginx_site="/etc/nginx/sites-available/opc-website"
nginx_enabled="/etc/nginx/sites-enabled/opc-website"

run_root() {
  if [ "$(id -u)" -eq 0 ]; then
    "$@"
  else
    sudo "$@"
  fi
}

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command is missing on server: $1" >&2
    exit 1
  fi
}

configure_git_ssh() {
  case "${repo_url}" in
    git@*|ssh://*)
      if [ -n "${deploy_git_ssh_command}" ]; then
        export GIT_SSH_COMMAND="${deploy_git_ssh_command}"
      fi
      ;;
  esac
}

write_default_env() {
  if [ ! -f "${env_file}" ]; then
    cat > "${env_file}" <<EOF
# Runtime secrets for opc-website. Fill these on the server; do not commit them.
OPENAI_AGENTS_API_KEY=
OPENAI_AGENTS_BASE_URL=https://api.openai.com/v1
OPENAI_AGENTS_MODEL=
OPENAI_AGENTS_MODEL_REASONING_EFFORT=medium
OPENAI_AGENTS_PROXY_URL=

# Backward-compatible aliases. Prefer OPENAI_AGENTS_* for new deployments.
CODEX_API_KEY=
CODEX_BASE_URL=
CODEX_MODEL=

OPENAI_VECTOR_STORE_API_KEY=
OPENAI_VECTOR_STORE_BASE_URL=https://api.openai.com/v1

PUBLIC_CHAT_FORCE_MOCK=0
OPC_METADATA_DB_PATH=${data_dir}/opc-metadata.sqlite
EOF
    chmod 600 "${env_file}"
  fi
}

write_systemd_unit() {
  local node_path
  node_path="$(command -v node)"

  run_root tee "${service_file}" >/dev/null <<EOF
[Unit]
Description=OPC Website Next.js app
After=network.target

[Service]
Type=simple
User=$(id -un)
Group=$(id -gn)
WorkingDirectory=${current_link}
Environment=NODE_ENV=production
Environment=PORT=${app_port}
Environment=OPC_METADATA_DB_PATH=${data_dir}/opc-metadata.sqlite
EnvironmentFile=-${env_file}
ExecStart=/usr/bin/env sh -c 'exec ./node_modules/.bin/next start -H 127.0.0.1 -p "\$PORT"'
Restart=always
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

  if [ ! -x "${node_path}" ]; then
    echo "Node path is not executable: ${node_path}" >&2
    exit 1
  fi

  run_root systemctl daemon-reload
  run_root systemctl enable "${service_name}" >/dev/null
}

write_nginx_site() {
  run_root tee "${nginx_site}" >/dev/null <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name ${server_name};

    client_max_body_size 20m;

    access_log /var/log/nginx/opc-website.access.log;
    error_log /var/log/nginx/opc-website.error.log;

    location /healthz {
        add_header Content-Type text/plain;
        return 200 'ok';
    }

    location / {
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300;
        proxy_pass http://127.0.0.1:${app_port};
    }
}
EOF

  run_root ln -sfn "${nginx_site}" "${nginx_enabled}"

  if [ -L /etc/nginx/sites-enabled/default ]; then
    run_root rm -f /etc/nginx/sites-enabled/default
  fi

  if [ -L /etc/nginx/sites-enabled/opc-planet ]; then
    run_root rm -f /etc/nginx/sites-enabled/opc-planet
  fi

  run_root nginx -t
  run_root systemctl reload nginx
}

prepare_directories() {
  run_root mkdir -p "${app_root}" "${shared_dir}" "${releases_dir}" "${data_dir}" "${codex_home}"
  run_root chown -R "$(id -un):$(id -gn)" "${app_root}"
  chmod 700 "${shared_dir}" "${codex_home}"
  write_default_env
}

checkout_release() {
  if [ ! -d "${repo_cache}/.git" ]; then
    git clone "${repo_url}" "${repo_cache}"
  fi

  git -C "${repo_cache}" fetch --prune --tags origin

  local target_ref
  if git -C "${repo_cache}" rev-parse --verify --quiet "origin/${deploy_ref}" >/dev/null; then
    target_ref="origin/${deploy_ref}"
  else
    target_ref="${deploy_ref}"
  fi

  local commit
  commit="$(git -C "${repo_cache}" rev-parse "${target_ref}")"
  local short_commit
  short_commit="$(git -C "${repo_cache}" rev-parse --short=12 "${commit}")"

  local release_name
  release_name="$(date -u +%Y%m%d%H%M%S)-${short_commit}"

  local release_dir
  release_dir="${releases_dir}/${release_name}"

  git clone --local "${repo_cache}" "${release_dir}" >&2
  git -C "${release_dir}" checkout --force "${commit}" >&2
  git -C "${release_dir}" reset --hard "${commit}" >&2

  echo "${release_dir}"
}

sync_knowledge_dirs() {
  local release_dir="$1"

  if [ -n "${KNOWLEDGE_ARCHIVE_PATH:-}" ]; then
    tar -xzf "${KNOWLEDGE_ARCHIVE_PATH}" -C "${release_dir}"
    return
  fi

  if [ -z "${knowledge_repo_url}" ]; then
    return
  fi

  if [ ! -d "${knowledge_repo_cache}/.git" ]; then
    git clone "${knowledge_repo_url}" "${knowledge_repo_cache}" >&2
  fi

  git -C "${knowledge_repo_cache}" fetch --prune --tags origin >&2

  local target_ref
  if git -C "${knowledge_repo_cache}" rev-parse --verify --quiet "origin/${knowledge_ref}" >/dev/null; then
    target_ref="origin/${knowledge_ref}"
  else
    target_ref="${knowledge_ref}"
  fi

  git -C "${knowledge_repo_cache}" checkout --force "${target_ref}" >&2
  git -C "${knowledge_repo_cache}" reset --hard "${target_ref}" >&2

  local path
  for path in knowledge sources outputs agent; do
    rm -rf "${release_dir}/${path}"
    if [ -e "${knowledge_repo_cache}/${path}" ]; then
      cp -a "${knowledge_repo_cache}/${path}" "${release_dir}/${path}"
    fi
  done
}

build_release() {
  local release_dir="$1"

  ln -sfn "${env_file}" "${release_dir}/.env"

  (
    cd "${release_dir}"
    npm ci || return $?
    npm run typecheck || return $?

    if [ "${skip_tests}" != "1" ]; then
      npm test || return $?
    fi

    if [ "${skip_build}" != "1" ]; then
      npm run build || return $?
    fi
  )
}

switch_release() {
  local release_dir="$1"
  local next_link="${app_root}/current.next"

  ln -sfn "${release_dir}" "${next_link}"
  mv -Tf "${next_link}" "${current_link}"
}

restart_service() {
  if ! systemctl list-unit-files "${service_name}.service" >/dev/null 2>&1; then
    echo "Missing ${service_name}.service. Re-run with -SetupServer first." >&2
    exit 1
  fi

  run_root systemctl daemon-reload
  run_root systemctl restart "${service_name}"
  sleep 2

  if ! systemctl is-active --quiet "${service_name}"; then
    run_root journalctl -u "${service_name}" -n 80 --no-pager >&2 || true
    exit 1
  fi

  curl -fsS --max-time 15 "http://127.0.0.1:${app_port}/" >/dev/null
}

stop_service_if_no_current_release() {
  if [ -e "${current_link}" ]; then
    return
  fi

  if systemctl list-unit-files "${service_name}.service" >/dev/null 2>&1; then
    run_root systemctl stop "${service_name}" >/dev/null 2>&1 || true
  fi
}

prune_releases() {
  if [ "${releases_to_keep}" -lt 1 ]; then
    return
  fi

  local active_release
  active_release="$(readlink -f "${current_link}" 2>/dev/null || true)"

  find "${releases_dir}" -mindepth 1 -maxdepth 1 -type d -printf "%T@ %p\n" |
    sort -rn |
    tail -n +"$((releases_to_keep + 1))" |
    cut -d' ' -f2- |
    while IFS= read -r old_release; do
      if [ -n "${old_release}" ] && [ "${old_release}" != "${active_release}" ]; then
        rm -rf "${old_release}"
      fi
    done
}

need_cmd git
need_cmd npm
need_cmd node
need_cmd curl
need_cmd systemctl

if [ "${setup_server}" = "1" ]; then
  need_cmd nginx
fi

configure_git_ssh
prepare_directories

if [ "${setup_server}" = "1" ]; then
  write_systemd_unit
elif ! systemctl list-unit-files "${service_name}.service" >/dev/null 2>&1; then
  echo "Missing ${service_name}.service. Re-run with -SetupServer first." >&2
  exit 1
fi

release_dir="$(checkout_release)"
sync_knowledge_dirs "${release_dir}"
echo "Building release: ${release_dir}"
if ! build_release "${release_dir}"; then
  stop_service_if_no_current_release
  exit 1
fi
switch_release "${release_dir}"
restart_service

if [ "${setup_server}" = "1" ]; then
  write_nginx_site
fi

prune_releases

echo "Deployed ${service_name} from ${repo_url}@${deploy_ref}"
echo "Current release: $(readlink -f "${current_link}")"
'@

Write-Host "Deploying $RepoUrl@$Ref to ${target}:$AppRoot"
$remoteScript = $remoteScript.TrimStart([char]0xFEFF)
$tempScriptPath = [System.IO.Path]::GetTempFileName()
$remoteScriptPath = "/tmp/opc-website-deploy-$([guid]::NewGuid().ToString('N')).sh"

try {
    if (-not [string]::IsNullOrWhiteSpace($KnowledgeArchivePath)) {
        $resolvedKnowledgeArchivePath = Resolve-Path -LiteralPath $KnowledgeArchivePath
        $remoteKnowledgeArchivePath = "/tmp/opc-website-knowledge-$([guid]::NewGuid().ToString('N')).tar.gz"
        & scp @scpArgs $resolvedKnowledgeArchivePath.Path "${target}:$remoteKnowledgeArchivePath"
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }

        $remoteEnv = "$remoteEnv KNOWLEDGE_ARCHIVE_PATH=$(ConvertTo-BashSingleQuoted $remoteKnowledgeArchivePath)"
    }

    [System.IO.File]::WriteAllText(
        $tempScriptPath,
        $remoteScript,
        [System.Text.UTF8Encoding]::new($false)
    )

    & scp @scpArgs $tempScriptPath "${target}:$remoteScriptPath"
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    & ssh @sshArgs "$remoteEnv bash '$remoteScriptPath'; remote_status=`$?; rm -f '$remoteScriptPath' '$remoteKnowledgeArchivePath'; exit `$remote_status"
}
finally {
    Remove-Item -LiteralPath $tempScriptPath -Force -ErrorAction SilentlyContinue
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
