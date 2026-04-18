$ErrorActionPreference = 'Continue'
$OC = "C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
$TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

# Test 1: Simple title
$js1 = "() => document.title"
$args1 = @('browser','evaluate','--fn',$js1,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','10000','--json')
$r1 = & $OC @args1 2>&1 | Out-String
Write-Host "TITLE RESULT: $r1"

# Test 2: Tweet extraction
$js2 = @'
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

$args2 = @('browser','evaluate','--fn',$js2,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','25000','--json')
$r2 = & $OC @args2 2>&1 | Out-String
# Try to extract JSON
if ($r2 -match '\{[\s\S]*"p"[\s\S]*\}') {
    $matched = $Matches[0]
    Write-Host "TWEETS FOUND: $($matched.Length) chars"
} else {
    Write-Host "NO MATCH, raw: $($r2.Substring(0, [Math]::Min(300, $r2.Length)))"
}
