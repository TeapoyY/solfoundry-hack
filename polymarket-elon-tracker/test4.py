#!/usr/bin/env python3
"""Run openclaw browser evaluate and parse result in Python."""
import json
import os
import re
import subprocess
import tempfile

OC = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

JS = r"""(function(){
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
return JSON.stringify(r);})()"""

# Write PowerShell script using @'...'@ heredoc
PS_CONTENT = r"""
$ErrorActionPreference = 'Continue'
$OC = '""" + OC + r"""'
$TARGET = '""" + TARGET + r"""'

$js = @'
""" + JS + r"""'@

$proc = Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command","& '$OC' browser evaluate --fn `"$js`" --target-id '$TARGET' --browser-profile chrome --timeout 25000 --json" -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\oc_stdout.txt" -RedirectStandardError "$env:TEMP\oc_stderr.txt"

Start-Sleep -Seconds 1
$raw = Get-Content "$env:TEMP\oc_stdout.txt" -Raw -ErrorAction SilentlyContinue
if (-not $raw) {
    $raw = "$env:TEMP\oc_stdout.txt was empty"
}
Write-Output $raw
"""

fd, fp = tempfile.mkstemp(suffix=".ps1")
with os.fdopen(fd, "w") as f:
    f.write(PS_CONTENT)

print("PS file:", fp)
r = subprocess.run(
    ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", fp],
    capture_output=True, text=True, timeout=50
)
os.unlink(fp)
print("RC:", r.returncode)
raw = r.stdout.strip()
print("OUT:", raw[:600])
print()
# Parse
try:
    data = json.loads(raw)
    print("JSON OK, result:", str(data.get("result",""))[:200])
except Exception as e:
    print("JSON parse error:", e)
    # Try regex
    m = re.search(r'"result":\s*(\[[\s\S]*?\]|\"[\s\S]*?\")', raw)
    if m:
        print("Found result field")
        print(m.group(0)[:200])
