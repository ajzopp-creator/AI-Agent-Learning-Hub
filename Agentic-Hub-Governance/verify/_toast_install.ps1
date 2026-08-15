Write-Output "PSModulePath:"
$env:PSModulePath -split ';' | ForEach-Object { Write-Output ("  " + $_) }
Write-Output "---"
Write-Output "Searching for BurntToast folders..."
$paths = $env:PSModulePath -split ';'
foreach ($p in $paths) {
  if (Test-Path $p) {
    Get-ChildItem $p -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*Burnt*' } | ForEach-Object { Write-Output $_.FullName }
  }
}
Write-Output "---"
Write-Output "Attempting Install-Module BurntToast -Scope CurrentUser..."
try {
  # Ensure NuGet provider for Install-Module
  if (-not (Get-PackageProvider -Name NuGet -ErrorAction SilentlyContinue)) {
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope CurrentUser | Out-Null
  }
  Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue
  Install-Module -Name BurntToast -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop
  Write-Output "Install-Module: OK"
  Get-Module -ListAvailable BurntToast | Format-List Name,Version,ModuleBase
} catch {
  Write-Output ("Install FAIL: " + $_.Exception.Message)
}