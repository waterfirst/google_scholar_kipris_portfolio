"""backend/services/portfolio.py — Unified portfolio aggregation"""
from dataclasses import dataclass, field
from typing import Optional
from .scholar import ScholarService
from .kipris import KiprisService


@dataclass
class PortfolioResult:
    name: str = ""
    success: bool = False
    error: str = ""
    profile: dict = field(default_factory=dict)
    kr_patents: list = field(default_factory=list)
    us_patents: list = field(default_factory=list)
    papers: list = field(default_factory=list)
    charts: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


class PortfolioService:
    """Orchestrates Google Scholar + KIPRIS data into a unified portfolio."""

    @classmethod
    async def generate(cls, name: str) -> PortfolioResult:
        """Generate a complete portfolio report for a given researcher name."""
        result = PortfolioResult(name=name)

        try:
            # Fetch from both sources concurrently
            gs_data = await ScholarService.search_profile(name)
            kp_data = await KiprisService.search_patents(name)

            if not gs_data and not kp_data:
                result.error = f"No data found for '{name}'. Try 'Nak Cho Choi' or '최낙초'."
                return result

            # Build profile
            if gs_data:
                p = gs_data['profile']
                result.profile = {
                    'name': p.get('name', name),
                    'affiliation': p.get('affiliation', ''),
                    'fields': p.get('fields', []),
                    'stats': {
                        'h_index': p.get('h_index', 0),
                        'i10_index': p.get('i10_index', 0),
                        'total_cites': p.get('total_cites', 0),
                        'kr_patents': len(kp_data['patents']) if kp_data else 0,
                        'us_patents': len(gs_data['us_patents']) if gs_data else 0,
                        'papers': len(gs_data['papers']) if gs_data else 0,
                    }
                }
                result.profile['stats']['total'] = (
                    result.profile['stats']['kr_patents'] +
                    result.profile['stats']['us_patents'] +
                    result.profile['stats']['papers']
                )

                result.us_patents = gs_data['us_patents']
                result.papers = gs_data['papers']

                # Charts data
                result.charts['us_tech'] = gs_data.get('us_tech', {})
                result.charts['us_yearly'] = gs_data.get('us_yearly', {})
                result.charts['paper_yearly'] = gs_data.get('paper_yearly', {})

            if kp_data:
                result.kr_patents = kp_data['patents']
                result.charts['kr_tech'] = kp_data.get('tech_dist', {})
                result.charts['kr_yearly'] = kp_data.get('yearly', {})

            # Build summary
            kr = result.profile['stats'].get('kr_patents', 0)
            us = result.profile['stats'].get('us_patents', 0)
            pp = result.profile['stats'].get('papers', 0)
            result.summary = {
                'total_ip': kr + us + pp,
                'kr_patents': kr,
                'us_patents': us,
                'papers': pp,
                'kr_lead': sum(1 for p in result.kr_patents if p.get('lead')),
                'us_lead': sum(1 for p in result.us_patents if p.get('lead')),
            }

            result.success = True

        except Exception as e:
            result.error = f"Portfolio generation failed: {str(e)}"

        return result
