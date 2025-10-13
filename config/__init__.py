"""Configuration module for fantasy football projections."""

from .scoring_formats import SCORING_FORMATS, get_scoring_format, get_available_formats

__all__ = ['SCORING_FORMATS', 'get_scoring_format', 'get_available_formats']
