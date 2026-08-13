$dir = "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24"
$iss = Join-Path $dir "GitPush_Setup.iss"
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$out = Join-Path $dir "iscc_out.txt"
$err = Join-Path $dir "iscc_err.txt"
$log = Join-Path $dir "iscc_log.txt"
"" | Set-Content -Path $log

$proc = Start-Process -FilePath $iscc -ArgumentList $iss -Wait -PassThru `
    -RedirectStandardOutput $out -RedirectStandardError $err -NoNewWindow
"ISCC exit code: $($proc.ExitCode)" | Out-File -FilePath $log -Encoding utf8 -Append
"--- STDOUT ---" | Out-File -FilePath $log -Encoding utf8 -Append
Get-Content $out | Out-File -FilePath $log -Encoding utf8 -Append
"--- STDERR ---" | Out-File -FilePath $log -Encoding utf8 -Append
Get-Content $err | Out-File -FilePath $log -Encoding utf8 -Append

if ($proc.ExitCode -eq 0) {
    $setup = Join-Path $dir "GitPush_Setup.exe"
    if (Test-Path $setup) {
        $cert = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" } | Select-Object -First 1
        $signed = Set-AuthenticodeSignature -FilePath $setup -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
        "setup sign status: $($signed.Status)  ($( (Get-Item $setup).Length ) bytes)" | Out-File -FilePath $log -Encoding utf8 -Append
    } else {
        "GitPush_Setup.exe not generated" | Out-File -FilePath $log -Encoding utf8 -Append
    }
}
