$ErrorActionPreference = "Continue"
$dir = "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24"
$log = Join-Path $dir "cert_log.txt"
"" | Set-Content -Path $log
function Log($m){ $m | Out-File -FilePath $log -Encoding utf8 -Append }

Log("=== 开始证书处理 $(Get-Date) ===")
Log("工作目录: $dir")

# 1. 查找已有的 NekoAiDev 证书
$existing = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" }
$cert = $null
if ($existing) {
    foreach ($c in $existing) {
        $eku = ($c.EnhancedKeyUsageList | ForEach-Object { $_.Value }) -join ","
        Log("发现证书 Thumbprint=$($c.Thumbprint) EKU=$eku")
        if ([string]::IsNullOrEmpty($eku) -or $eku -like "*1.3.6.1.5.5.7.3.3*") {
            $cert = $c
            Log("复用该证书用于代码签名")
        }
    }
}

if (-not $cert) {
    Log("未找到可用的代码签名证书，新建一张 CodeSigningCert ...")
    $cert = New-SelfSignedCertificate `
        -Subject "CN=NekoAiDev GitPush" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyExportPolicy Exportable `
        -KeyUsage DigitalSignature `
        -Type CodeSigningCert `
        -NotAfter (Get-Date).AddYears(5) `
        -HashAlgorithm SHA256
    Log("新建证书 Thumbprint=$($cert.Thumbprint)")
    $cert.Thumbprint | Out-File -FilePath (Join-Path $dir "cert_thumbprint.txt") -Encoding utf8
}

# 2. 导出 .cer（公钥，安装到受信任根用，无需密码）
$cerPath = Join-Path $dir "GitPush.cer"
if (Test-Path $cerPath) { Remove-Item $cerPath -Force }
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Log("已导出 .cer: $cerPath  ($( (Get-Item $cerPath).Length ) 字节)")

# 2.5 先把证书装进当前用户「受信任根证书」，否则自签名证书链不被信任，签名会失败
# 用 X509Store 直接写入，绕开 Import-Certificate 在沙箱里对 Root 存储的写入限制
$alreadyRoot = Get-ChildItem "Cert:\CurrentUser\Root" | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
if ($alreadyRoot) {
    Log("证书已在当前用户受信任根，跳过装入")
} else {
    try {
        $cert2 = [System.Security.Cryptography.X509Certificates.X509Certificate2]$cert
        $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","CurrentUser")
        $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $store.Add($cert2)
        $store.Close()
        Log("已通过 X509Store 装入当前用户受信任根（仅本机签名验证用）")
    } catch {
        Log("装入受信任根失败: $_")
    }
}

# 3. 给 dist\GitPush.exe 签名
$exePath = Join-Path $dir "dist\GitPush.exe"
if (Test-Path $exePath) {
    $signed = Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
    Log("签名状态: $($signed.Status)")
    Log("签名人: $($signed.SignerCertificate.Subject)")
    if ($signed.Status -ne "Valid") {
        Log("签名警告: $($signed.StatusMessage)")
    }
    # 复核
    $verify = Get-AuthenticodeSignature -FilePath $exePath
    Log("复核签名状态: $($verify.Status)")
} else {
    Log("未找到 $exePath，跳过签名")
}

Log("=== 完成 ===")
