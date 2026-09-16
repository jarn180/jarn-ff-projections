"""Configuration module for fantasy football projections."""

from .scoring_formats import SCORING_FORMATS, get_scoring_format, get_available_formats
from .team_abbreviations import TEAM_ABBR_TO_NAME, team_full_name

__all__ = [
    'SCORING_FORMATS', 'get_scoring_format', 'get_available_formats',
    'TEAM_ABBR_TO_NAME', 'team_full_name',
]
