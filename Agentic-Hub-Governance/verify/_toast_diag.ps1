Get-Module -ListAvailable BurntToast | Format-List Name,Version,ModuleBase
try {
  Import-Module BurntToast -ErrorAction Stop
  Write-Output "Import-Module: OK"
  Get-Command New-BurntToastNotification | Format-List Name,Source,CommandType
  New-BurntToastNotification -Text "Direct PS Test", "If you see this, BurntToast works from plain PowerShell"
  Write-Output "New-BurntToastNotification: called, no exception"
} catch {
  Write-Output ("FAIL: " + $_.Exception.Message)
  Write-Output $_.ScriptStackTrace
}
