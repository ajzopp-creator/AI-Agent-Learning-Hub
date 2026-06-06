# =============================================================================
# Claude_Session_Guardian.ps1
# Monitors Claude Desktop log for server errors -- shows Windows toast alerts
# Save to: C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\tools\claude_guardian\
# Run at start of every trading session. Close when done.
# =============================================================================

$LOG_PATH    = "$env:APPDATA\Claude\logs\claude.ai-web.log"
$POLL_MS     = 2000       # Check every 2 seconds
$COOLDOWN_S  = 60         # Don't repeat same alert within 60 seconds
$APP_NAME    = "Claude Guardian"

# Track last alert time per pattern to avoid spam
$lastAlert = @{}

# --- Toast notification using System.Windows.Forms balloon ---
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$trayIcon = New-Object System.Windows.Forms.NotifyIcon
$trayIcon.Icon = [System.Drawing.SystemIcons]::Warning
$trayIcon.Text = $APP_NAME
$trayIcon.Visible = $true

function Show-Alert {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Key,
        [System.Windows.Forms.ToolTipIcon]$Icon = [System.Windows.Forms.ToolTipIcon]::Warning
    )
    $now = Get-Date
    if ($lastAlert.ContainsKey($Key)) {
        $elapsed = ($now - $lastAlert[$Key]).TotalSeconds
        if ($elapsed -lt $COOLDOWN_S) { return }
    }
    $lastAlert[$Key] = $now
    $trayIcon.ShowBalloonTip(8000, $Title, $Message, $Icon)
    Write-Host "[$($now.ToString('HH:mm:ss'))] ALERT: $Title -- $Message" -ForegroundColor Yellow
}

# --- Error pattern definitions ---
$patterns = @(
    @{
        Key     = "data_loss"
        Match   = "message_store_sync_loss_accepted"
        Title   = "DATA LOSS WARNING"
        Message = "Claude dropped a message -- data was NOT saved. Stop pasting new work."
        Icon    = [System.Windows.Forms.ToolTipIcon]::Error
    },
    @{
        Key     = "sync_blocked"
        Match   = "message_store_sync_blocked"
        Title   = "Claude Sync Blocked"
        Message = "Messages are not saving to server. Hold off on new signals."
        Icon    = [System.Windows.Forms.ToolTipIcon]::Warning
    },
    @{
        Key     = "server_error"
        Match   = "Internal server error"
        Title   = "Anthropic Server Error"
        Message = "Claude API returning errors. Responses may fail or not save."
        Icon    = [System.Windows.Forms.ToolTipIcon]::Warning
    },
    @{
        Key     = "not_retryable"
        Match   = "Not retryable error"
        Title   = "Claude Request Failed"
        Message = "A request failed and will NOT be retried. Check your last message."
        Icon    = [System.Windows.Forms.ToolTipIcon]::Error
    }
)

# --- Startup notice ---
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Claude Session Guardian -- ACTIVE" -ForegroundColor Cyan
Write-Host " Watching: $LOG_PATH" -ForegroundColor Cyan
Write-Host " Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$trayIcon.ShowBalloonTip(4000, $APP_NAME, "Guardian active -- watching Claude for errors.", [System.Windows.Forms.ToolTipIcon]::Info)

# --- Main watch loop ---
$lastSize = 0

try {
    while ($true) {
        Start-Sleep -Milliseconds $POLL_MS

        if (-not (Test-Path $LOG_PATH)) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Log file not found -- is Claude Desktop running?" -ForegroundColor Red
            continue
        }

        $currentSize = (Get-Item $LOG_PATH).Length

        if ($currentSize -gt $lastSize) {
            # Read only new content since last check
            $newLines = Get-Content $LOG_PATH | Select-Object -Last 50

            foreach ($pattern in $patterns) {
                $hit = $newLines | Where-Object { $_ -match [regex]::Escape($pattern.Match) }
                if ($hit) {
                    Show-Alert -Key $pattern.Key -Title $pattern.Title -Message $pattern.Message -Icon $pattern.Icon
                }
            }
            $lastSize = $currentSize
        }
    }
}
finally {
    $trayIcon.Visible = $false
    $trayIcon.Dispose()
    Write-Host "Guardian stopped." -ForegroundColor Gray
}
