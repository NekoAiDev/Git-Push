$ErrorActionPreference = "Continue"
$dir = "D:\AppData\WorkBuddyData\.workbuddy\2026-08-02-10-27-24"
$log = Join-Path $dir "cert_log.txt"
"" | Set-Content -Path $log
function Log($m){ $m | Out-File -FilePath $log -Encoding utf8 -Append }

Log("=== cert process start $(Get-Date) ===")

$existing = Get-ChildItem "Cert:\CurrentUser\My" | Where-Object { $_.Subject -like "*NekoAiDev*" }
$cert = $null
if ($existing) {
    foreach ($c in $existing) {
        $eku = ($c.EnhancedKeyUsageList | ForEach-Object { $_.Value }) -join ","
        Log("found cert Thumbprint=$($c.Thumbprint) EKU=$eku")
        if ([string]::IsNullOrEmpty($eku) -or $eku -like "*1.3.6.1.5.5.7.3.3*") {
            $cert = $c
            Log("reuse this cert for code signing")
        }
    }
}

if (-not $cert) {
    Log("no valid code signing cert found, create new CodeSigningCert ...")
    $cert = New-SelfSignedCertificate `
        -Subject "CN=NekoAiDev GitPush" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -KeyExportPolicy Exportable `
        -KeyUsage DigitalSignature `
        -Type CodeSigningCert `
        -NotAfter (Get-Date).AddYears(5) `
        -HashAlgorithm SHA256
    Log("new cert Thumbprint=$($cert.Thumbprint)")
    $cert.Thumbprint | Out-File -FilePath (Join-Path $dir "cert_thumbprint.txt") -Encoding utf8
}

$cerPath = Join-Path $dir "GitPush.cer"
if (Test-Path $cerPath) { Remove-Item $cerPath -Force }
Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
Log("exported .cer: $cerPath  ($( (Get-Item $cerPath).Length ) bytes)")

$alreadyRoot = Get-ChildItem "Cert:\CurrentUser\Root" | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
if ($alreadyRoot) {
    Log("cert already in current user trusted root, skip")
} else {
    try {
        $cert2 = [System.Security.Cryptography.X509Certificates.X509Certificate2]$cert
        $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root","CurrentUser")
        $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
        $store.Add($cert2)
        $store.Close()
        Log("added to current user trusted root")
    } catch {
        Log("add to trusted root failed: $_")
    }
}

$exePath = Join-Path $dir "dist\GitPush.exe"
if (Test-Path $exePath) {
    $signed = Set-AuthenticodeSignature -FilePath $exePath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
    Log("sign status: $($signed.Status)")
    Log("signer: $($signed.SignerCertificate.Subject)")
    if ($signed.Status -ne "Valid") {
        Log("sign warning: $($signed.StatusMessage)")
    }
    $verify = Get-AuthenticodeSignature -FilePath $exePath
    Log("verify status: $($verify.Status)")
} else {
    Log("not found $exePath, skip sign")
}

Log("=== done ===")
