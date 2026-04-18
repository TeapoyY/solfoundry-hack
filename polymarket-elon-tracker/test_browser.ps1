$ErrorActionPreference = 'Stop'
$CHROME_PS = "C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
$TARGET_ID = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
$JS = "document.location.href"

$result = & $CHROME_PS browser act --json `
    --target host `
    --profile chrome `
    --targetId $TARGET_ID `
    --request ('{"kind": "evaluate", "fn": "' + $JS + '", "timeoutMs": 5000}')

Write-Output $result
