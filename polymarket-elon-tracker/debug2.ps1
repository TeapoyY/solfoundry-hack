$ErrorActionPreference = 'Continue'
$OC = "C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
$TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

$js = @'
(function(){
var r=[];
var a=document.querySelectorAll('article[role=article]');
for(var i=0;i<a.length;i++){
var el=a[i];var pid='';
var ls=el.querySelectorAll('a[href]');
for(var j=0;j<ls.length;j++){
var m=ls[j].href.match(/\/status\/(\d+)/);
if(m){pid=m[1];break;}
}
var t=el.querySelector('time');
var ts=t?(t.getAttribute('datetime')||''):'';
var txt=el.querySelector('[data-testid=tweetText]');
var tx=txt?(txt.innerText||''):'';
r.push({p:pid,t:ts,x:tx.substring(0,80)});
}
return JSON.stringify(r);
})()
'@

$args = @('browser','evaluate','--fn',$js,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','25000','--json')
$raw = & $OC @args 2>&1 | Out-String

# Parse as PowerShell object
try {
    $obj = $raw | ConvertFrom-Json
    Write-Host "Parsed OK: $($obj.PSObject.Properties.Name -join ', ')"
    Write-Host "result type: $($obj.result.GetType().Name)"
    Write-Host "result length: $($obj.result.Length)"
    Write-Host "result preview: $($obj.result.Substring(0, [Math]::Min(200, $obj.result.Length)))"
} catch {
    Write-Host "Parse error: $_"
    Write-Host "Raw (first 300): $($raw.Substring(0, [Math]::Min(300, $raw.Length)))"
}
