<#
  build_msix.ps1 — 将 dist\GitPush.exe 封装为上架用 GitPush.msix
  ============================================================
  前置条件：
    1. 已用 PyInstaller 构建出 dist\GitPush.exe（见 GitPush.spec）
    2. 安装 Windows 10/11 SDK（提供 makeappx.exe 与 signtool.exe）
    3. 已在 Partner Center 拿到「应用标识」里的 Package name 与 Publisher
    4. 已运行 make_cert.ps1 生成 NekoAiDev GitPush 代码签名证书
    5. assets\ 下备好 4 张 png：Square44x44Logo / Square150x150Logo /
       Wide310x150Logo / StoreLogo（用 appicon.ico 转换即可）

  用法（在仓库根目录执行）：
    .\tools\msix\build_msix.ps1 -IdentityName "12345NekoAiDev.GitPush" -Publisher "CN=..."
#>
param(
  [Parameter(Mandatory=$true)]  [string]$IdentityName,
  [Parameter(Mandatory=$true)]  [string]$Publisher,
  [string]$Version  = "1.4.4.0",
  [string]$Arch     = "x64",
  [string]$Root     = $PSScriptRoot   # 脚本所在目录（tools\msix）
)

$ErrorActionPreference = "Stop"
# 仓库根目录 = tools\msix 的上一级
$RepoRoot = (Get-Item $Root).Parent.Parent.FullName

function Find-Tool($name) {
  $p = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin" -Recurse -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { $p = Get-ChildItem "C:\Program Files\Windows Kits\10\bin" -Recurse -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1 }
  if (-not $p) { throw "找不到 $name，请安装 Windows 10/11 SDK" }
  return $p.FullName
}
$makeappx = Find-Tool "makeappx.exe"
$signtool = Find-Tool "signtool.exe"

# 1. 准备打包目录
$pkg = Join-Path $RepoRoot "msix_pkg"
if (Test-Path $pkg) { Remove-Item $pkg -Recurse -Force }
New-Item $pkg -ItemType Directory | Out-Null

# 2. 复制主程序、图标，并写入 Store 版开关标记（空文件即可）
Copy-Item (Join-Path $RepoRoot "dist\GitPush.exe") $pkg
Copy-Item (Join-Path $RepoRoot "appicon.ico") $pkg
New-Item (Join-Path $pkg "STORE_BUILD.flag") -ItemType File | Out-Null
Write-Host "已放入 STORE_BUILD.flag（Store 版禁用自更新开关）"

# 3. 复制徽标 png
$assets = Join-Path $pkg "assets"
New-Item $assets -ItemType Directory | Out-Null
foreach ($f in @("Square44x44Logo.png","Square150x150Logo.png","Wide310x150Logo.png","StoreLogo.png")) {
  $src = Join-Path $RepoRoot "assets\$f"
  if (Test-Path $src) { Copy-Item $src (Join-Path $assets $f) }
  else { throw "缺少 $src，请用 appicon.ico 生成这 4 张 png 后重试" }
}

# 4. 生成 AppxManifest.xml（Identity 来自参数）
$manifest = @"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities">
  <Identity Name="$IdentityName" Publisher="$Publisher" Version="$Version" ProcessorArchitecture="$Arch" />
  <Properties>
    <DisplayName>GitPush</DisplayName>
    <PublisherDisplayName>NekoAiDev</PublisherDisplayName>
    <Logo>assets\StoreLogo.png</Logo>
  </Properties>
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22631.0" />
  </Dependencies>
  <Resources><Resource Language="en-US" /><Resource Language="zh-CN" /></Resources>
  <Applications>
    <Application Id="GitPush" Executable="GitPush.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="GitPush" Description="Git Push 工具 / Git Push Tool"
        BackgroundColor="transparent" Square150x150Logo="assets\Square150x150Logo.png"
        Square44x44Logo="assets\Square44x44Logo.png">
        <uap:DefaultTile Wide310x150Logo="assets\Wide310x150Logo.png" />
      </uap:VisualElements>
    </Application>
  </Applications>
  <Capabilities><rescap:Capability Name="runFullTrust" /></Capabilities>
</Package>
"@
Set-Content -Path (Join-Path $pkg "AppxManifest.xml") -Value $manifest -Encoding UTF8

# 5. 打包
$msix = Join-Path $RepoRoot "GitPush.msix"
if (Test-Path $msix) { Remove-Item $msix -Force }
& $makeappx pack /d $pkg /p $msix /o
if ($LASTEXITCODE -ne 0) { throw "makeappx 打包失败" }

# 6. 用现有 NekoAiDev 代码签名证书签名（商店发布时会重签）
$cert = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" } | Select-Object -First 1
if (-not $cert) { throw "找不到 NekoAiDev 代码签名证书，请先运行 make_cert.ps1" }
& $signtool sign /fd SHA256 /sha1 $cert.Thumbprint /tr http://timestamp.digicert.com /td SHA256 $msix
if ($LASTEXITCODE -ne 0) { throw "签名失败" }

Write-Host "✅ 已生成 $msix ($( (Get-Item $msix).Length ) bytes)"
Write-Host "下一步：Partner Center -> 提交 -> Packages 上传此 .msix（设备系列仅勾 Desktop）"
