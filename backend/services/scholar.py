"""backend/services/scholar.py — Google Scholar data service"""
import json
import re
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent  # backend/services → backend → root

# Name matching patterns for Nak Cho Choi
NAME_RE = re.compile(
    r'\bNC\s*CHOI\b|\bNC\s*Choi\b|\bN\s*CHOI\b|\bN\s*Choi\b|'
    r'\bC\s*Nakcho\b|\bNakcho\s*Choi\b|\bChoi\s*Nak\s*Cho\b|'
    r'\bKL\s*Nakcho\s*Choi\b|\bNak\s*Cho\s*Choi\b', re.IGNORECASE)


class ScholarService:
    """Google Scholar data retrieval and analysis."""

    @staticmethod
    def is_lead_inventor(authors: str) -> bool:
        if not authors:
            return False
        first = authors.split(',')[0].strip()
        return bool(NAME_RE.search(first))

    @classmethod
    async def search_profile(cls, name: str) -> Optional[dict]:
        """Search for a researcher profile. Currently supports pre-cached data."""
        # Try loading cached data
        cache_path = DATA_DIR / 'scholar_analysis.json'
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pubs = data.get('publications', [])
            profile = data.get('profile', {})

            # Process publications
            us_patents = []
            papers = []
            for p in pubs:
                venue = p.get('venue', '').lower()
                is_pat = any(k in venue for k in ['patent', 'app.', 'application'])
                classification = p.get('classification', {})
                item = {
                    'title': p.get('title', ''),
                    'year': p.get('year_int', 0) or int(p.get('year', '0') or '0'),
                    'cites': p.get('citations_int', 0) or int(p.get('citations', '0') or '0'),
                    'authors': p.get('authors', ''),
                    'venue': p.get('venue', ''),
                    'tech': classification.get('primary_tech', 'Other') if isinstance(classification, dict) else str(classification),
                    'lead': cls.is_lead_inventor(p.get('authors', '')),
                }
                if is_pat:
                    us_patents.append(item)
                else:
                    papers.append(item)

            # Stats
            try:
                h_idx = int(profile.get('stats', {}).get('h-index', 14))
            except:
                h_idx = 14
            try:
                i10_idx = int(profile.get('stats', {}).get('i10-index', 22))
            except:
                i10_idx = 22
            try:
                total_cites = int(profile.get('stats', {}).get('서지정보', 813))
            except:
                total_cites = 813

            # Tech distribution
            us_tech = {}
            us_yearly = {}
            for p in us_patents:
                us_tech[p['tech']] = us_tech.get(p['tech'], 0) + 1
                if p['year'] > 0:
                    us_yearly[p['year']] = us_yearly.get(p['year'], 0) + 1

            paper_yearly = {}
            for p in papers:
                if p['year'] > 0:
                    paper_yearly[p['year']] = paper_yearly.get(p['year'], 0) + 1

            return {
                'profile': {
                    'name': profile.get('name', 'Nak Cho Choi'),
                    'affiliation': 'Samsung Display, Principal Engineer',
                    'fields': profile.get('fields', []),
                    'h_index': h_idx,
                    'i10_index': i10_idx,
                    'total_cites': total_cites,
                },
                'us_patents': sorted(us_patents, key=lambda x: x['year'], reverse=True),
                'papers': sorted(papers, key=lambda x: x['year'], reverse=True),
                'us_tech': us_tech,
                'us_yearly': us_yearly,
                'paper_yearly': paper_yearly,
            }

        # No cached data — attempt live scholarly search
        try:
            from scholarly import scholarly
            search_query = scholarly.search_author(name)
            author = next(search_query, None)
            if author:
                author = scholarly.fill(author, sections=['basics', 'publications'])
                pubs_list = []
                for pub in author.get('publications', [])[:100]:
                    bib = pub.get('bib', {})
                    venue_str = bib.get('venue', '') or bib.get('journal', '') or ''
                    is_pat = 'patent' in venue_str.lower()
                    pubs_list.append({
                        'title': bib.get('title', ''),
                        'year': int(bib.get('pub_year', 0) or 0),
                        'cites': int(pub.get('num_citations', 0) or 0),
                        'authors': bib.get('author', ''),
                        'venue': venue_str,
                        'tech': 'Other',
                        'lead': False,
                    })
                h = author.get('hindex', 0)
                i10 = author.get('i10index', 0)
                cites = author.get('citedby', 0)
                # Basic processing
                us_patents = [p for p in pubs_list if p['venue'] and 'patent' in p['venue'].lower()]
                papers = [p for p in pubs_list if p not in us_patents]
                return {
                    'profile': {'name': author.get('name', name), 'affiliation': author.get('affiliation', ''),
                                'fields': author.get('interests', []), 'h_index': h, 'i10_index': i10, 'total_cites': cites},
                    'us_patents': us_patents, 'papers': papers,
                    'us_tech': {}, 'us_yearly': {}, 'paper_yearly': {},
                }
        except Exception as e:
            pass
        return None
