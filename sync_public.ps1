# 每次发版时运行：把最新安装包和单文件 exe 同步到 public/，供 Cloudflare Pages 直接托管
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$public = Join-Path $dir "public"

if (!(Test-Path $public)) { New-Item -ItemType Directory -Path $public | Out-Null }

$srcSetup = Join-Path $dir "GitPush_Setup.exe"
$srcExe   = Join-Path $dir "dist\GitPush.exe"
$dstSetup = Join-Path $public "GitPush_Setup.exe"
$dstExe   = Join-Path $public "gitpush.exe"

if (Test-Path $srcSetup) {
    Copy-Item $srcSetup $dstSetup -Force
    Write-Output "已同步安装包: $dstSetup ($( (Get-Item $dstSetup).Length ) 字节)"
} else {
    Write-Output "警告: 未找到 $srcSetup"
}

if (Test-Path $srcExe) {
    Copy-Item $srcExe $dstExe -Force
    Write-Output "已同步单文件版: $dstExe ($( (Get-Item $dstExe).Length ) 字节)"
} else {
    Write-Output "警告: 未找到 $srcExe"
}

Write-Output "同步完成。提交 public/ 目录后，Pages 会自动部署。"
