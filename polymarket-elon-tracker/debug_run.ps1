$ErrorActionPreference = 'Continue'
$OC = "C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
$JS = "(function(){return JSON.stringify({title: document.title, count: document.querySelectorAll('article').length});})()"
$TIMEOUT = 30000

$jsonArgs = @(
    "browser", "evaluate",
    "--fn", $JS,
    "--target-id", "B8795CA0F4574E46F3E6F21B1D5F8F4E",
    "--browser-profile", "chrome",
    "--timeout", [string]$TIMEOUT,
    "--json"
)

# Call openclaw via & invocation
$result = & $OC @jsonArgs 2>&1
$jsonStr = ($result | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | Select-Object -First 1)
Write-Host "JSON OUTPUT: $($jsonStr | Out-String)"
