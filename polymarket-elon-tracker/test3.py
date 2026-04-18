#!/usr/bin/env python3
"""Test: run openclaw via PowerShell subprocess and parse result in Python."""
import json
import os
import re
import subprocess
import sys

OC = r"C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1"
TARGET = "B8795CA0F4574E46F3E6F21B1D5F8F4E"

JS = """(function(){
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
})()"""

# Build PowerShell script
PS = r"""
$OC = "{OC}"
$TARGET = "{TARGET}"
$JS = @'
{JS}
'@
$args = @('browser','evaluate','--fn',$JS,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','25000','--json')
$raw = & $OC @args 2>&1 | Out-String
Write-Output $raw
""".format(OC=OC, TARGET=TARGET, JS=JS)

fd, fp = tempfile.mkstemp(suffix=".ps1")
with os.fdopen(fd, "w") as f:
    f.write(PS)

try:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive",
         "-ExecutionPolicy", "Bypass", "-File", fp],
        capture_output=True, text=True, timeout=40,
        encoding="utf-8", errors="replace"
    )
    raw = r.stdout
    print("RAW OUTPUT (first 500):")
    print(raw[:500])
    print()

    # Try to extract JSON from raw output
    # Find the JSON object (starts with { or [)
    stripped = raw.strip()
    try:
        data = json.loads(stripped)
        print("FULL JSON parsed OK")
        print("result:", str(data.get("result", ""))[:200])
    except json.JSONDecodeError:
        # Try finding { ... } in the output
        m = re.search(r'\{[\s\S]*\}', stripped)
        if m:
            try:
                data = json.loads(m.group(0))
                print("EXTRACTED JSON parsed OK")
                print("result:", str(data.get("result", ""))[:200])
            except json.JSONDecodeError as e:
                print("JSON extract error:", e)
                print("Text around error:", m.group(0)[max(0,e.pos-20):e.pos+20])
        else:
            print("No JSON found in output")
finally:
    os.unlink(fp)
