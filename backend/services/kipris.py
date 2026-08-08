"""backend/services/kipris.py — KIPRIS Korean patent data service"""
import json, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent

NAME_RE = re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b', re.IGNORECASE)

IPC_TECH = {
    'G02F': 'LCD', 'H10K': 'OLED', 'H10H': 'Micro LED',
    'H10D': 'TFT', 'H01L': 'TFT', 'G09G': 'Driving',
    'G09F': 'Panel', 'G06F': 'Touch', 'H05B': 'Display',
}


class KiprisService:

    @staticmethod
    def parse_year(d):
        if not d: return 0
        parts = str(d).replace('-','.').split('.')
        return int(parts[0]) if parts and parts[0].isdigit() else 0

    @staticmethod
    def ipc_tech(ipc_str):
        if not ipc_str: return 'Other'
        for part in str(ipc_str).split('|'):
            part = part.strip()
            parts = part.split()
            if parts and len(parts[0]) >= 3:
                return IPC_TECH.get(parts[0][:4], parts[0][:4])
        return 'Other'

    @staticmethod
    def is_lead(inventors):
        if not inventors: return False
        first = inventors.split('|')[0].strip() if '|' in inventors else inventors[:10]
        return '최낙초' in first or NAME_RE.search(first)

    @classmethod
    async def search_patents(cls, name):
        # 1. Try cached Excel data
        cache_path = DATA_DIR / 'patent_data.json'
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            headers = raw['headers']
            col_map = {h: i for i, h in enumerate(headers)}
            patents = []
            for row in raw['data']:
                p = {}
                for h, i in col_map.items():
                    p[h] = row[i] if i < len(row) else ''
                patents.append({
                    'title': p.get('발명의명칭', ''), 'title_en': p.get('발명의명칭(영문)', ''),
                    'year': cls.parse_year(p.get('출원일자', '')),
                    'app_number': p.get('출원번호', ''), 'app_date': p.get('출원일자', ''),
                    'reg_number': p.get('등록번호', ''), 'reg_date': p.get('등록일자', ''),
                    'status': '등록' if '등록' in str(p.get('법적상태', '')) else ('공개' if '공개' in str(p.get('법적상태', '')) else '기타'),
                    'ipc': p.get('IPC분류', ''), 'applicant': p.get('출원인', ''),
                    'tech': cls.ipc_tech(p.get('IPC분류', '')),
                    'lead': cls.is_lead(p.get('발명자', '')), 'inventors': p.get('발명자', ''),
                })
            kr_tech = {}
            kr_yearly = {}
            for p in patents:
                kr_tech[p['tech']] = kr_tech.get(p['tech'], 0) + 1
                if p['year'] > 0:
                    kr_yearly[p['year']] = kr_yearly.get(p['year'], 0) + 1
            return {'patents': sorted(patents, key=lambda x: x['year'], reverse=True),
                    'tech_dist': kr_tech, 'yearly': kr_yearly}

        # 2. Try KIPRIS API
        try:
            key = "q7jusMtGXniJ9nMVvbM6oNa8I3pMDbXAAsDLkpRng=I="
            url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/freeSearchInfo"
            ps = {'inventor': name, 'patent': 'true', 'utility': 'true', 'numOfRows': '50', 'pageNo': '1', 'accessKey': key}
            qs = '&'.join(f"{k}={urllib.parse.quote(str(v))}" for k, v in ps.items())
            req = urllib.request.Request(f"{url}?{qs}", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read().decode('utf-8')
            root = ET.fromstring(data)
            items = root.findall('.//item')
            if items:
                patents = []
                for item in items:
                    d = {}
                    for child in item:
                        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        d[tag] = child.text or ''
                    patents.append({
                        'title': d.get('InventionName', ''), 'title_en': '',
                        'year': cls.parse_year(d.get('ApplicationDate', '')),
                        'app_number': d.get('ApplicationNumber', ''), 'app_date': d.get('ApplicationDate', ''),
                        'reg_number': d.get('RegistrationNumber', ''), 'reg_date': d.get('RegistrationDate', ''),
                        'status': '등록' if '등록' in d.get('RegistrationStatus', '') else ('공개' if '공개' in d.get('RegistrationStatus', '') else '기타'),
                        'ipc': d.get('InternationalpatentclassificationNumber', ''),
                        'applicant': '', 'tech': cls.ipc_tech(d.get('InternationalpatentclassificationNumber', '')),
                        'lead': cls.is_lead(d.get('Inventor', '')), 'inventors': d.get('Inventor', ''),
                    })
                kr_tech = {}
                kr_yearly = {}
                for p in patents:
                    kr_tech[p['tech']] = kr_tech.get(p['tech'], 0) + 1
                    if p['year'] > 0:
                        kr_yearly[p['year']] = kr_yearly.get(p['year'], 0) + 1
                return {'patents': sorted(patents, key=lambda x: x['year'], reverse=True),
                        'tech_dist': kr_tech, 'yearly': kr_yearly}
        except Exception:
            pass

        return None
