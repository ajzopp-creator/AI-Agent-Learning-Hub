<# 
    P_000_InstallerVerifyCache.ps1
    Purpose: Verify MSI Installer Cache Integrity
#>

Write-Host "=== P_000 Installer Verify Cache ===" -ForegroundColor Cyan

# Registry path for MSI products
$regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products"

Write-Host "`nScanning MSI product registry..." -ForegroundColor Yellow
$products = Get-ChildItem $regPath -ErrorAction SilentlyContinue

if (!$products) {
    Write-Host "No MSI products found. Something is wrong with the Installer database." -ForegroundColor Red
    exit
}

$missingCache = @()
$corruptedCache = @()

foreach ($p in $products) {
    $productCode = $p.PSChildName
    $msiPath = "C:\Windows\Installer\$productCode.msi"

    if (!(Test-Path $msiPath)) {
        $missingCache += $productCode
    }
}

Write-Host "`nChecking for corrupted MSI cache entries..." -ForegroundColor Yellow

$installerFiles = Get-ChildItem "C:\Windows\Installer" -Filter *.msi -ErrorAction SilentlyContinue

foreach ($file in $installerFiles) {
    try {
        $null = Get-WmiObject -Class Win32_Product -Filter "IdentifyingNumber='{$($file.BaseName)}'" -ErrorAction Stop
    } catch {
        $corruptedCache += $file.FullName
    }
}

Write-Host "`n=== RESULTS ===" -ForegroundColor Cyan

if ($missingCache.Count -eq 0 -and $corruptedCache.Count -eq 0) {
    Write-Host "Installer cache is healthy. No issues detected." -ForegroundColor Green
} else {
    if ($missingCache.Count -gt 0) {
        Write-Host "`nMissing MSI Cache Files:" -ForegroundColor Red
        $missingCache | ForEach-Object { Write-Host " - $_" }
    }

    if ($corruptedCache.Count -gt 0) {
        Write-Host "`nCorrupted MSI Cache Files:" -ForegroundColor Red
        $corruptedCache | ForEach-Object { Write-Host " - $_" }
    }
}

Write-Host "`nScan complete." -ForegroundColor Cyan
