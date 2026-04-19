# Read file
path = r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\src\full_analyzer.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line-by-line replacements
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # apr14-21: update xtrack_confirmed from 164 to 184
    if '"xtrack_confirmed": 164,' in line and i < 60:
        new_lines.append('        "xtrack_confirmed": 184,      # UPDATED 2026-04-19 15:36 HKT\n')
        i += 1
        continue

    # apr14-21 outcome buckets: 220-239 from 0.12 to 0.05, 240-259 from 0.27 to 0.11
    if '"lo": 220,  "hi": 239, "label": "220-239",  "price": 0.12},' in line and i < 70:
        new_lines.append('            {"lo": 220,  "hi": 239, "label": "220-239",  "price": 0.05},\n')
        i += 1
        continue
    if '"lo": 240,  "hi": 259, "label": "240-259",  "price": 0.27},' in line and i < 70:
        new_lines.append('            {"lo": 240,  "hi": 259, "label": "240-259",  "price": 0.11},\n')
        i += 1
        continue
    if '"lo": 260,  "hi": 279, "label": "260-279",  "price": 0.30},' in line and i < 70:
        new_lines.append('            {"lo": 260,  "hi": 279, "label": "260-279",  "price": 0.24},\n')
        i += 1
        continue
    if '"lo": 280,  "hi": 299, "label": "280-299",  "price": 0.19},' in line and i < 70:
        new_lines.append('            {"lo": 280,  "hi": 299, "label": "280-299",  "price": 0.23},\n')
        i += 1
        continue
    if '"lo": 300,  "hi": 499, "label": "300-499",  "price": 0.05},' in line and i < 70:
        new_lines.append('            {"lo": 300,  "hi": 499, "label": "300-499",  "price": 0.20},\n')
        i += 1
        continue

    # apr17-24: update xtrack_confirmed from 55 to 68, prices 0.79/0.21 to 0.85/0.15
    if '"xtrack_confirmed": 55,' in line and 60 < i < 80:
        new_lines.append('        "xtrack_confirmed": 68,       # UPDATED 2026-04-19 15:36 HKT\n')
        i += 1
        continue
    if '"pm_yes_price": 0.79,' in line and 60 < i < 80:
        new_lines.append('        "pm_yes_price": 0.85,\n')
        i += 1
        continue
    if '"pm_no_price": 0.21,' in line and 60 < i < 80:
        new_lines.append('        "pm_no_price": 0.15,\n')
        i += 1
        continue
    if '"lo": 200,  "hi": 219, "label": "200-219",  "price": 0.10},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 200,  "hi": 219, "label": "200-219",  "price": 0.19},\n')
        i += 1
        continue
    if '"lo": 220,  "hi": 239, "label": "220-239",  "price": 0.10},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 220,  "hi": 239, "label": "220-239",  "price": 0.16},\n')
        i += 1
        continue
    if '"lo": 240,  "hi": 259, "label": "240-259",  "price": 0.13},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 240,  "hi": 259, "label": "240-259",  "price": 0.18},\n')
        i += 1
        continue
    if '"lo": 260,  "hi": 279, "label": "260-279",  "price": 0.21},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 260,  "hi": 279, "label": "260-279",  "price": 0.19},\n')
        i += 1
        continue
    if '"lo": 280,  "hi": 299, "label": "280-299",  "price": 0.20},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 280,  "hi": 299, "label": "280-299",  "price": 0.16},\n')
        i += 1
        continue
    if '"lo": 300,  "hi": 499, "label": "300-499",  "price": 0.14},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 300,  "hi": 319, "label": "300-319",  "price": 0.10},\n')
        i += 1
        continue
    if '"lo": 500,  "hi": 9999,"label": ">=500",    "price": 0.01},' in line and 60 < i < 80:
        new_lines.append('            {"lo": 320,  "hi": 9999,"label": ">=320",    "price": 0.02},\n')
        i += 1
        continue

    # may2026: update prices from 0.37/0.63 to 0.85/0.15
    if '"xtrack_confirmed": 0,' in line and 80 < i < 100:
        new_lines.append('        "xtrack_confirmed": 0,\n')
        i += 1
        continue
    if '"pm_yes_price": 0.37,' in line and 80 < i < 100:
        new_lines.append('        "pm_yes_price": 0.85,       # UPDATED 2026-04-19 15:36 HKT\n')
        i += 1
        continue
    if '"pm_no_price": 0.63,' in line and 80 < i < 100:
        new_lines.append('        "pm_no_price": 0.15,\n')
        i += 1
        continue
    if '"lo": 0,    "hi": 799, "label": "<800",     "price": 0.63},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 0,    "hi": 799, "label": "<800",     "price": 0.15},\n')
        i += 1
        continue
    if '"lo": 800,  "hi": 899, "label": "800-899",  "price": 0.08},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 800,  "hi": 899, "label": "800-899",  "price": 0.13},\n')
        i += 1
        continue
    if '"lo": 900,  "hi": 999, "label": "900-999",  "price": 0.10},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 900,  "hi": 999, "label": "900-999",  "price": 0.16},\n')
        i += 1
        continue
    if '"lo": 1000, "hi": 1099,"label": "1000-1099","price": 0.08},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 1000, "hi": 1099,"label": "1000-1099","price": 0.13},\n')
        i += 1
        continue
    if '"lo": 1100, "hi": 1199,"label": "1100-1199","price": 0.05},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 1100, "hi": 1199,"label": "1100-1199","price": 0.10},\n')
        i += 1
        continue
    if '"lo": 1200, "hi": 1299,"label": "1200-1299","price": 0.04},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 1200, "hi": 1299,"label": "1200-1299","price": 0.09},\n')
        i += 1
        continue
    if '"lo": 1300, "hi": 9999,"label": ">=1300",  "price": 0.02},' in line and 80 < i < 100:
        new_lines.append('            {"lo": 1300, "hi": 9999,"label": ">=1300",  "price": 0.07},\n')
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Done! Updated", path)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
print("apr14-21 xtrack_confirmed:", "184" if '"xtrack_confirmed": 184' in content else "STILL 164")
print("apr17-24 xtrack_confirmed:", "68" if '"xtrack_confirmed": 68' in content else "STILL 55")
print("may2026 pm_yes_price:", "0.85" if '"pm_yes_price": 0.85' in content else "STILL 0.37")
