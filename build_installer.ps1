$dir = "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24"
$iss = Join-Path $dir "GitPush_Setup.iss"
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$out = Join-Path $dir "iscc_out.txt"
$err = Join-Path $dir "iscc_err.txt"
$log = Join-Path $dir "iscc_log.txt"
"" | Set-Content -Path $log

$proc = Start-Process -FilePath $iscc -ArgumentList $iss -Wait -PassThru `
    -RedirectStandardOutput $out -RedirectStandardError $err -NoNewWindow
"ISCC 退出码: $($proc.ExitCode)" | Out-File -FilePath $log -Encoding utf8 -Append
"--- STDOUT ---" | Out-File -FilePath $log -Encoding utf8 -Append
Get-Content $out | Out-File -FilePath $log -Encoding utf8 -Append
"--- STDERR ---" | Out-File -FilePath $log -Encoding utf8 -Append
Get-Content $err | Out-File -FilePath $log -Encoding utf8 -Append

if ($proc.ExitCode -eq 0) {
    $setup = Join-Path $dir "GitPush_Setup.exe"
    if (Test-Path $setup) {
        # 取证书并给安装包签名
        $cert = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" } | Select-Object -First 1
        $signed = Set-AuthenticodeSignature -FilePath $setup -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
        "安装包签名状态: $($signed.Status)  ($( (Get-Item $setup).Length ) 字节)" | Out-File -FilePath $log -Encoding utf8 -Append
    } else {
        "未生成 GitPush_Setup.exe" | Out-File -FilePath $log -Encoding utf8 -Append
    }
}
