import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import re
from collections import defaultdict, Counter
from pathlib import Path

# Load data
with open('scholar_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

profile = data['profile']
pubs = data['publications']

# ---- Classification ----
def classify_pub(pub):
    title = pub.get('title', '')
    venue = pub.get('venue', '')
    
    # Type: patent vs paper
    venue_lower = venue.lower()
    is_patent = any(kw in venue_lower for kw in ['patent', 'app.', 'application'])
    pub_type = 'patent' if is_patent else ('paper' if venue else 'unknown')
    
    # Technology sub-category
    combined = (title + ' ' + venue).lower()
    tech_cats = []
    
    tech_keywords = {
        'Micro LED / LED': ['micro led', 'micro-led', 'light emitting diode', 'μled', 'μ-led', 'led chip', 'led display', 'led device', 'light-emitting', 'light emitting', 'μled'],
        'OLED': ['oled', 'organic light emitting', 'organic electroluminescent', 'organic light-emitting'],
        'LCD': ['lcd', 'liquid crystal', 'liquid-crystal', 'liquid crystal display'],
        'TFT / Backplane': ['tft', 'thin film transistor', 'thin-film transistor', 'array panel', 'array substrate', 'transistor'],
        'Display Packaging / Bonding': ['bonding', 'bump', 'package', 'interconnect', 'electrode connect', 'connection', 'pad', ' anisotropic', 'acf', 'flexible circuit'],
        'Display Panel / Substrate': ['display panel', 'display substrate', 'substrate', 'tile', 'tiling', 'seamless', 'large-area'],
        'Driving / Circuit': ['driving', 'driver', 'pixel circuit', 'scan driver', 'data driver', 'emission driver', 'gate driver'],
        'Inspection / Testing': ['inspection', 'testing', 'test', 'inspect', 'repair', 'defect'],
        'Manufacturing Process': ['manufacturing', 'method of manufacturing', 'method of fabricating', 'fabrication', 'process'],
        'Optical / Color': ['color', 'wavelength', 'color filter', 'color conversion', 'quantum dot', 'light control', 'optical'],
        'Touch / Sensor': ['touch', 'sensor', 'sensing', 'fingerprint', 'pressure sensor'],
        'Flexible / Stretchable': ['flexible', 'stretchable', 'foldable', 'bendable', 'rollable'],
    }
    
    for cat, keywords in tech_keywords.items():
        for kw in keywords:
            if kw in combined:
                tech_cats.append(cat)
                break
    
    if not tech_cats:
        tech_cats.append('Other Display')
    
    # Main tech category
    primary_tech = []
    for kw_set in [['Micro LED / LED'], ['OLED'], ['LCD']]:
        for tc in tech_cats:
            if tc in kw_set:
                primary_tech.append(tc)
    if not primary_tech:
        primary_tech = tech_cats[:1] if tech_cats else ['Other']
    
    return {
        'type': pub_type,
        'tech_categories': tech_cats,
        'primary_tech': primary_tech[0]
    }

# Apply classification
for pub in pubs:
    pub['classification'] = classify_pub(pub)
    # Parse year as int
    try:
        pub['year_int'] = int(pub.get('year', '0'))
    except:
        pub['year_int'] = 0
    # Parse citations as int
    try:
        pub['citations_int'] = int(pub.get('citations', '0') or '0')
    except:
        pub['citations_int'] = 0

# ---- Analysis ----
print("=" * 60)
print("GOOGLE SCHOLAR PROFILE ANALYSIS")
print("=" * 60)
print(f"Name: {profile['name']}")
print(f"Stats: {profile['stats']}")
print(f"Fields: {profile['fields']}")
print(f"Total publications: {len(pubs)}")

# Type distribution
type_dist = Counter(p['classification']['type'] for p in pubs)
print(f"\n--- Type Distribution ---")
for t, c in type_dist.most_common():
    print(f"  {t}: {c}")

# Tech category distribution
tech_dist = Counter()
for p in pubs:
    for tc in p['classification']['tech_categories']:
        tech_dist[tc] += 1
print(f"\n--- Tech Category Distribution ---")
for tc, c in tech_dist.most_common():
    print(f"  {tc}: {c}")

# Yearly distribution
yearly = defaultdict(lambda: {'total': 0, 'patent': 0, 'paper': 0, 'citations': 0})
yearly_tech = defaultdict(lambda: Counter())
for p in pubs:
    y = p['year_int']
    if y > 0:
        yearly[y]['total'] += 1
        yearly[y][p['classification']['type']] += 1
        yearly[y]['citations'] += p['citations_int']
        yearly_tech[y][p['classification']['primary_tech']] += 1

print(f"\n--- Yearly Distribution ---")
for y in sorted(yearly.keys()):
    ydata = yearly[y]
    print(f"  {y}: {ydata['total']} pubs (patent:{ydata['patent']}, paper:{ydata['paper']}), {ydata['citations']} cites")

# Top cited
top_cited = sorted(pubs, key=lambda p: p['citations_int'], reverse=True)[:10]
print(f"\n--- Top 10 Cited ---")
for i, p in enumerate(top_cited):
    print(f"  {i+1}. [{p['citations_int']} cites] {p['title'][:80]} ({p['year']})")

# Timeline: trend years
years_with_pubs = sorted([y for y in yearly if y > 0])
if years_with_pubs:
    print(f"\n--- Timeline ---")
    print(f"  First publication: {years_with_pubs[0]}")
    print(f"  Latest publication: {years_with_pubs[-1]}")
    print(f"  Active years: {len(years_with_pubs)}")

# Save enriched data
output = {
    'profile': profile,
    'publications': pubs,
    'analysis': {
        'type_distribution': dict(type_dist),
        'tech_distribution': dict(tech_dist),
        'yearly': {str(k): dict(v) for k, v in yearly.items()},
        'yearly_tech': {str(k): dict(v) for k, v in yearly_tech.items()},
        'top_cited': [{'title': p['title'], 'year': p['year'], 'citations': p['citations_int'], 'type': p['classification']['type']} for p in top_cited]
    }
}

with open('scholar_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nAnalysis saved to scholar_analysis.json")
