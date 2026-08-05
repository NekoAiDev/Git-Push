$dir = "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24"
$exe = Join-Path $dir "dist\GitPush.exe"
$zip = Join-Path $dir "dist\update.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $exe -DestinationPath $zip -Force
"update.zip 重建完成: $((Get-Item $zip).Length) 字节  (来自已签名 $((Get-Item $exe).Length) 字节的 exe)" | Out-File -FilePath (Join-Path $dir "updatezip_log.txt") -Encoding utf8
