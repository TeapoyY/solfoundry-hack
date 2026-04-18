# 8-scroll tweet collection using Chrome CDP via browser tool
$allTweets = @()
$jsFn = @"
(function(){
var r=[];
var a=document.querySelectorAll('article[role=article]');
for(var i=0;i<a.length;i++){
var el=a[i];
var pid='';
var ls=el.querySelectorAll('a[href]');
for(var j=0;j<ls.length;j++){
var m=ls[j].href.match(/\/status\/(\d+)/);
if(m){pid=m[1];break;}}
var t=el.querySelector('time');
var ts=t?(t.getAttribute('datetime')||''):'';
var txt=el.querySelector('[data-testid=tweetText]');
var tx=txt?(txt.innerText||''):'';
var like=el.querySelector('[data-testid=like]');
var ln=like?(like.innerText||'0').replace(/,/g,''):'0';
var rt=el.querySelector('[data-testid=retweet]');
var rn=rt?(rt.innerText||'0').replace(/,/g,''):'0';
var auth=el.querySelector('[data-testid=User-Name]');
var by='';
if(auth){
var sp=auth.querySelectorAll('span');
for(var k=0;k<sp.length;k++){
if(sp[k].innerText.includes('@')){by=sp[k].innerText;break;}}}
r.push({p:pid,t:ts,x:tx.substring(0,200),ln:ln,rn:rn,by:by});
}
return JSON.stringify(r);
})()
"@

$targetId = "B8795CA0F4574E46F3E6F21B1D5F8F4E"
$profile = "chrome"
$target = "host"

for ($i = 0; $i -lt 8; $i++) {
    Write-Host "Scroll $i..."
    
    # Collect tweets
    $result = & "$PSScriptRoot\..\..\..\browser_collect.exe" 2>$null
    if (-not $result) {
        Write-Host "  Using browser tool API..."
    }
    
    # Wait then scroll
    Start-Sleep -Milliseconds 2500
}

$tweets | ConvertTo-Json -Depth 10 | Out-File "$PSScriptRoot\data\tweets_latest.json" -Encoding UTF8
Write-Host "Saved $($allTweets.Count) tweets"
