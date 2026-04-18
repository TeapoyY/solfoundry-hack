$ErrorActionPreference = 'Continue'
$OC = "C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
$TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
$JS = "(function(){var r=[];var a=document.querySelectorAll('article[role=article]');for(var i=0;i<a.length;i++){var el=a[i];var pid='';var ls=el.querySelectorAll('a[href]');for(var j=0;j<ls.length;j++){var m=ls[j].href.match(/\/status\/(\d+)/);if(m){pid=m[1];break;}}var t=el.querySelector('time');var ts=t?(t.getAttribute('datetime')||''):'';var txt=el.querySelector('[data-testid=tweetText]');var tx=txt?(txt.innerText||''):'';r.push({p:pid,t:ts,x:tx.substring(0,80)});}return JSON.stringify(r);})()"

# Run via & invocation
$jsonArgs = @("browser", "evaluate", "--fn", $JS, "--target-id", $TARGET, "--browser-profile", "chrome", "--timeout", "25000", "--json")
$result = & $OC @jsonArgs 2>&1

$text = $result | Out-String
# Try to find JSON in output
if ($text -match '\{[\s\S]*"ok"[\s\S]*\}') {
    $matched = $Matches[0]
    Write-Host "MATCHED JSON: $($matched.Substring(0, [Math]::Min(200, $matched.Length)))"
} else {
    Write-Host "NO JSON FOUND"
    Write-Host "OUTPUT: $($text.Substring(0, [Math]::Min(500, $text.Length)))"
}
