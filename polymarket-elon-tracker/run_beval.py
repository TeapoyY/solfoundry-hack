# Test openclaw browser evaluate via subprocess
import subprocess
import json

OC = r'C:\Users\Administrator\AppData\Roaming\npm\openclaw.ps1'
TARGET = 'B8795CA0F4574E46F3E6F21B1D5F8F4E'

def run_beval(js, timeout_ms=25000):
    # Write PowerShell script to temp file
    ps_script = '''
$ErrorActionPreference = 'Continue'
$OC = "{oc}"
$TARGET = "{target}"
$JS = @'
{js}
'@
$args = @('browser','evaluate','--fn',$JS,'--target-id',$TARGET,'--browser-profile','chrome','--timeout','{timeout}','--json')
$result = & $OC @args 2>&1 | Out-String
# Extract first JSON object
if ($result -match "{{[\s\S]*?""ok""[\s\S]*?}}") {{
    Write-Output $Matches[0]
}} else {{
    Write-Output $result.Substring(0, [Math]::Min(500, $result.Length))
}}
'''.format(oc=OC, target=TARGET, js=js, timeout=timeout_ms)

    # Write to temp .ps1 file
    import tempfile, os
    fd, fp = tempfile.mkstemp(suffix='.ps1')
    with os.fdopen(fd, 'w') as f:
        f.write(ps_script)

    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', fp],
            capture_output=True, text=True, timeout=timeout_ms // 1000 + 15
        )
        text = r.stdout.strip()
        if text:
            try:
                return json.loads(text)
            except:
                return {"result": text}
        return {}
    finally:
        os.unlink(fp)

# Test
print("Testing browser evaluate...")
result = run_beval('() => document.title')
print("Title:", result)
result2 = run_beval('(function(){var r=[];var a=document.querySelectorAll("article[role=article]");for(var i=0;i<a.length;i++){var el=a[i];var pid="";var ls=el.querySelectorAll("a[href]");for(var j=0;j<ls.length;j++){{var m=ls[j].href.match(/\\/status\\/(\\d+)/);if(m){{pid=m[1];break;}}}}var t=el.querySelector("time");var ts=t?(t.getAttribute("datetime")||""):"";var txt=el.querySelector("[data-testid=tweetText]");var tx=txt?(txt.innerText||""):"";r.push({{p:pid,t:ts,x:tx.substring(0,80)}});}}return JSON.stringify(r);})()')
print("Tweets:", result2.get('result','')[:200] if result2 else 'none')
