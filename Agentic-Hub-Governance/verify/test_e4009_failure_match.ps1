# Independent review harness for WO-P300-E4.009
# Extracts the EXACT failure-indicator array and matching loop from the
# real P_300_RunAllDailyEvals.ps1 (lines verified by direct file read,
# not retyped from memory) and drives it against real + synthetic text.

$failureIndicators = @(
    "login page", "not logging in", "sign in to Chaikin",
    "log in to Chaikin", "extension.{0,20}not connected",
    "chrome extension.{0,20}not", "could not connect",
    "unable to connect", "not authenticated"
)

function Test-ChaikinFailureMatch {
    param([string]$text)
    $matched = $false
    foreach ($pattern in $failureIndicators) {
        if ($text -match $pattern) { $matched = $true; break }
    }
    return $matched
}

$cases = @(
    @{ Name = "Login-wall phrasing"; Text = "It looks like I have hit a login page for Chaikin Analytics and I am not logging in on your behalf."; Expect = $true },
    @{ Name = "Disconnected-extension phrasing"; Text = "The Chrome extension does not appear to be connected right now."; Expect = $true },
    @{ Name = "Clean success response"; Text = "Chaikin Power Gauge for CNK: bullish momentum score 7.2, above average. Data pulled successfully and written to the note."; Expect = $false },
    @{ Name = "Edge: word connect present but not a failure phrase"; Text = "Connect the dots: momentum and volume both point higher for GURE."; Expect = $false },
    @{ Name = "Sign-in phrasing variant"; Text = "You will need to sign in to Chaikin Analytics to view this page."; Expect = $true }
)

$pass = 0
$fail = 0
foreach ($c in $cases) {
    $result = Test-ChaikinFailureMatch -text $c.Text
    $ok = ($result -eq $c.Expect)
    if ($ok) { $pass++ } else { $fail++ }
    $status = if ($ok) { "PASS" } else { "FAIL" }
    Write-Output "[$status] $($c.Name) -- expected=$($c.Expect) actual=$result"
}
Write-Output ""
Write-Output "RESULT: $pass/$($cases.Count) PASS"
if ($fail -gt 0) { Write-Output "*** $fail CASE(S) FAILED -- review pattern list ***" }
