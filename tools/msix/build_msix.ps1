<#
  build_msix.ps1 — 一键把 GitPush.exe 封成上架用 GitPush.msix / .appxupload
  =====================================================================
  前置条件：
    1. 已用 PyInstaller 构建出 GitPush.exe（见 GitPush.spec，产物在 dist\）
    2. 已安装 Windows 10/11 SDK（提供 makeappx.exe / signtool.exe）
       或已下载 NuGet 包 Microsoft.Windows.SDK.BuildTools 并解压

  用法（推荐在仓库根目录执行）：
    .\tools\msix\build_msix.ps1
    —— 脚本会交互式询问 Package name 与 Publisher（从 Partner Center 应用标识复制）

  非交互用法（CI / 一行搞定）：
    .\tools\msix\build_msix.ps1 -IdentityName "12345NekoAiDev.GitPush" -Publisher "CN=..."

  说明：
    * 脚本会自动在仓库里找 GitPush.exe，并把 STORE_BUILD.flag 放进包
      （Store 版禁用内置自更新，符合 Microsoft Store 政策 10.2.2）
    * 代码签名是可选项：Microsoft Store 上传后会用自己的证书重新签名，
      所以本机即使没有代码签名证书，也能正常打包并上传；
      签名仅用于"本机双击安装测试"时才需要。
#>
param(
  [string]$IdentityName = "",
  [string]$Publisher    = "",
  [string]$Version  = "1.4.4.0",
  [string]$Arch     = "x64",
  [string]$RepoRoot = "",
  [string]$ExePath  = ""
)

$ErrorActionPreference = "Stop"

# ---------- 1. 定位仓库根目录 ----------
$root = $RepoRoot
if (-not $root) {
  if ($PSScriptRoot -match '[\\/]tools[\\/]msix$') {
    $root = (Get-Item $PSScriptRoot).Parent.Parent.FullName
  } elseif ($ExePath -and (Test-Path $ExePath)) {
    $root = (Get-Item $ExePath).DirectoryName
  } else {
    $root = $PSScriptRoot
  }
}
Write-Host "仓库根目录: $root" -ForegroundColor Cyan

# ---------- 2. 定位 GitPush.exe ----------
if (-not $ExePath) {
  $candidates = @(
    (Join-Path $root "dist\GitPush.exe"),
    (Join-Path $root "GitPush.exe"),
    (Join-Path $PSScriptRoot "GitPush.exe")
  )
  foreach ($c in $candidates) { if (Test-Path $c) { $ExePath = $c; break } }
}
if (-not (Test-Path $ExePath)) {
  $found = Get-ChildItem $root -Recurse -Filter "GitPush.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $ExePath = $found.FullName }
}
if (-not (Test-Path $ExePath)) {
  $ExePath = Read-Host "找不到 GitPush.exe，请粘贴它的完整路径（含文件名）"
}
if (-not (Test-Path $ExePath)) { throw "仍找不到 GitPush.exe，已退出" }
Write-Host "主程序: $ExePath" -ForegroundColor Cyan

# ---------- 3. 定位 makeappx / signtool ----------
function Find-Tool($name) {
  $roots = @(
    "C:\Program Files (x86)\Windows Kits\10\bin",
    "C:\Program Files\Windows Kits\10\bin",
    (Join-Path $env:USERPROFILE ".nuget\packages\microsoft.windows.sdk.buildtools")
  )
  foreach ($r in $roots) {
    if (Test-Path $r) {
      $p = Get-ChildItem $r -Recurse -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($p) { return $p.FullName }
    }
  }
  $onPath = Get-Command $name -ErrorAction SilentlyContinue
  if ($onPath) { return $onPath.Source }
  return $null
}
$makeappx = Find-Tool "makeappx.exe"
$signtool = Find-Tool "signtool.exe"
if (-not $makeappx) {
  Write-Host "❌ 找不到 makeappx.exe。" -ForegroundColor Red
  Write-Host "   请安装 Windows 10/11 SDK（安装时勾选“Windows SDK 签名工具”），" -ForegroundColor Red
  Write-Host "   或下载 NuGet 包 Microsoft.Windows.SDK.BuildTools 解压后重试。" -ForegroundColor Red
  throw "缺少 makeappx.exe"
}
Write-Host "makeappx: $makeappx" -ForegroundColor Cyan
if ($signtool) { Write-Host "signtool: $signtool" -ForegroundColor Cyan }
else { Write-Host "（未找到 signtool，将跳过签名——Store 上传后会自动重签，不影响上传）" -ForegroundColor Yellow }

# ---------- 4. 获取身份标识（交互） ----------
if (-not $IdentityName) {
  Write-Host "请从 Partner Center → 你的应用 → 应用标识 复制以下两项：" -ForegroundColor Yellow
  $IdentityName = Read-Host "  Package name（形如 12345NekoAiDev.GitPush）"
}
if (-not $Publisher) {
  $Publisher = Read-Host "  Publisher（形如 CN=... 的一长串）"
}
if (-not $IdentityName -or -not $Publisher) { throw "Package name 与 Publisher 必填" }

# ---------- 5. 准备打包目录 ----------
$pkg = Join-Path $root "msix_pkg"
if (Test-Path $pkg) { Remove-Item $pkg -Recurse -Force }
New-Item $pkg -ItemType Directory | Out-Null

Copy-Item $ExePath (Join-Path $pkg "GitPush.exe")

$ico = Join-Path $root "appicon.ico"
if (Test-Path $ico) { Copy-Item $ico $pkg } else { Write-Host "（未找到 appicon.ico，使用默认图标）" -ForegroundColor Yellow }

# Store 版开关：包内放空文件 STORE_BUILD.flag → 禁用内置自更新
New-Item (Join-Path $pkg "STORE_BUILD.flag") -ItemType File | Out-Null
Write-Host "✅ 已放入 STORE_BUILD.flag（Store 版禁用自更新，符合政策 10.2.2）" -ForegroundColor Green

# 徽标 png
$assets = Join-Path $pkg "assets"
New-Item $assets -ItemType Directory | Out-Null
foreach ($f in @("Square44x44Logo.png","Square150x150Logo.png","Wide310x150Logo.png","StoreLogo.png")) {
  $src = Join-Path $root "assets\$f"
  if (-not (Test-Path $src)) { $src = Join-Path $PSScriptRoot "assets\$f" }
  if (Test-Path $src) { Copy-Item $src (Join-Path $assets $f) }
  else { Write-Host "⚠️ 缺少 $f（可用 appicon.ico 转换生成）" -ForegroundColor Yellow }
}

# ---------- 6. 生成 AppxManifest.xml ----------
$manifest = @"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="$IdentityName" Publisher="$Publisher" Version="$Version" ProcessorArchitecture="$Arch" />
  <Properties>
    <DisplayName>GitPush</DisplayName>
    <PublisherDisplayName>NekoAiDev</PublisherDisplayName>
    <Logo>assets/StoreLogo.png</Logo>
  </Properties>
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22631.0" />
  </Dependencies>
  <Resources><Resource Language="en-US" /><Resource Language="zh-CN" /></Resources>
  <Applications>
    <Application Id="GitPush" Executable="GitPush.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="GitPush" Description="Git Push 工具 / Git Push Tool"
        BackgroundColor="transparent" Square150x150Logo="assets/Square150x150Logo.png"
        Square44x44Logo="assets/Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="assets/Wide310x150Logo.png" />
      </uap:VisualElements>
    </Application>
  </Applications>
  <Capabilities><rescap:Capability Name="runFullTrust" /></Capabilities>
</Package>
"@
Set-Content -Path (Join-Path $pkg "AppxManifest.xml") -Value $manifest -Encoding UTF8

# ---------- 7. 打包 ----------
$msix = Join-Path $root "GitPush.msix"
if (Test-Path $msix) { Remove-Item $msix -Force }
& $makeappx pack /d $pkg /p $msix /o
if ($LASTEXITCODE -ne 0) { throw "makeappx 打包失败" }
Write-Host "✅ 已生成 $msix ($( (Get-Item $msix).Length ) bytes)" -ForegroundColor Green

# ---------- 8. 签名（可选） ----------
if ($signtool) {
  $cert = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" } | Select-Object -First 1
  if ($cert) {
    & $signtool sign /fd SHA256 /sha1 $cert.Thumbprint /tr http://timestamp.digicert.com /td SHA256 $msix
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ 已用 NekoAiDev 证书签名（用于本机测试安装）" -ForegroundColor Green }
    else { Write-Host "⚠️ 签名失败，忽略——Store 上传后会用自己的证书重签" -ForegroundColor Yellow }
  } else {
    Write-Host "⚠️ 未找到 NekoAiDev 证书，跳过签名——Store 上传后会用自己的证书重签，不影响上传" -ForegroundColor Yellow
  }
}

# ---------- 9. 生成 appxupload（Store 推荐格式） ----------
$appxupload = Join-Path $root "GitPush.appxupload"
if (Test-Path $appxupload) { Remove-Item $appxupload -Force }
Compress-Archive -Path $msix -DestinationPath $appxupload -Force
Write-Host "✅ 已生成 $appxupload（可直接上传 Partner Center）" -ForegroundColor Green

Write-Host ""
Write-Host "下一步：Partner Center → 提交 → Packages 上传 GitPush.appxupload 或 GitPush.msix（设备系列仅勾 Desktop）" -ForegroundColor Cyan
