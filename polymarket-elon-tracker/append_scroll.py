import json
out = r'C:\Users\Administrator\.openclaw\workspace\polymarket-elon-tracker\data\tweets_latest.json'
with open(out, 'r', encoding='utf-8') as f:
    data = json.load(f)
scroll7 = [
    {'p': '2045343130590052402', 't': '2026-04-18T03:26:17.000Z', 'x': 'Magic powder is amazing wwwwwwwwww', 'ln': '200', 'rn': '21', 'by': '@Japan_lol_w'},
    {'p': '2045207685872623794', 't': '2026-04-17T18:28:05.000Z', 'x': 'I love Tomodachi Life', 'ln': '44K', 'rn': '3.9K', 'by': '@Michaelmcchill'},
    {'p': '2045223250284650960', 't': '2026-04-17T19:29:55.000Z', 'x': 'Here we go... Grok 4.3 just dropped. Now it can create other file formats like Slides, Sheets, PDFs, Docs, etc.', 'ln': '2.5K', 'rn': '459', 'by': '@minchoi'},
    {'p': '2045309797013323947', 't': '2026-04-18T01:13:50.000Z', 'x': 'The sky over Arizona, this is the one and only Omar...', 'ln': '1.1K', 'rn': '108', 'by': '@BrianRoemmele'},
    {'p': '2043047235701665916', 't': '', 'x': 'No more soggy pouch. Nic Nac is a xylitol based nicotine lozenge manufactured in the USA with just six premium ingredients. Family-owned and operated.', 'ln': '205', 'rn': '20', 'by': '@nicnacusa'},
    {'p': '2045133536194433088', 't': '2026-04-17T13:33:26.000Z', 'x': 'To those pondering the Halloween menu', 'ln': '15K', 'rn': '1.7K', 'by': '@baypinar35'},
    {'p': '2045136387389943878', 't': '2026-04-17T13:44:46.000Z', 'x': 'US Marines Engaged by Taliban Fire - Sniper Returns Fire with Confirmed Kill. Raw footage from Afghanistan shows a team of U.S. Marines coming under sudden Taliban attack, including reported RPG fire.', 'ln': '8.6K', 'rn': '293', 'by': '@wartirnes'},
    {'p': '2045193784883884114', 't': '2026-04-17T17:32:50.000Z', 'x': 'Still an early beta , but worth trying out', 'ln': '33K', 'rn': '3.4K', 'by': '@elonmusk'},
    {'p': '2039379884527456475', 't': '', 'x': 'The Iranian people want freedom---and their regime is willing to blind them to stop it.', 'ln': '8.6K', 'rn': '1.8K', 'by': '@mercedesschlapp'},
    {'p': '2045381224366248351', 't': '2026-04-18T05:57:39.000Z', 'x': 'When engineering hits absolutely zero tolerance.', 'ln': '92', 'rn': '5', 'by': '@ScienceExpand'},
]
data['tweets'].extend(scroll7)
data['scroll'] = 7
# Deduplicate by post_id
seen = set()
deduped = []
for t in data['tweets']:
    if t['p'] not in seen:
        seen.add(t['p'])
        deduped.append(t)
data['tweets'] = deduped
with open(out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
# Count elon tweets
elon = [t for t in data['tweets'] if t.get('by') == '@elonmusk']
print('Total tweets:', len(data['tweets']), 'Elon:', len(elon))
for e in elon:
    print(' ', e['p'], '|', e['t'], '|', e['x'][:60])
