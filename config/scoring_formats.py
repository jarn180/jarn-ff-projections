"""
Fantasy Football Scoring Format Definitions
"""

SCORING_FORMATS = {
    "PPR": {
        "name": "Points Per Reception",
        "passing": {
            "yards": 0.04,  # 1 point per 25 yards
            "touchdowns": 4,
            "interceptions": -2,
            "two_point_conversions": 2,
        },
        "rushing": {
            "yards": 0.1,  # 1 point per 10 yards
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "receiving": {
            "receptions": 1,  # Full PPR
            "yards": 0.1,  # 1 point per 10 yards
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "fumbles": {
            "lost": -2,
        },
    },
    "HALF_PPR": {
        "name": "Half Point Per Reception",
        "passing": {
            "yards": 0.04,
            "touchdowns": 4,
            "interceptions": -2,
            "two_point_conversions": 2,
        },
        "rushing": {
            "yards": 0.1,
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "receiving": {
            "receptions": 0.5,  # Half PPR
            "yards": 0.1,
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "fumbles": {
            "lost": -2,
        },
    },
    "STANDARD": {
        "name": "Standard (No PPR)",
        "passing": {
            "yards": 0.04,
            "touchdowns": 4,
            "interceptions": -2,
            "two_point_conversions": 2,
        },
        "rushing": {
            "yards": 0.1,
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "receiving": {
            "receptions": 0,  # No PPR
            "yards": 0.1,
            "touchdowns": 6,
            "two_point_conversions": 2,
        },
        "fumbles": {
            "lost": -2,
        },
    },
}


def get_scoring_format(format_name):
    """Get scoring format by name."""
    return SCORING_FORMATS.get(format_name.upper())


def get_available_formats():
    """Get list of available scoring formats."""
    return list(SCORING_FORMATS.keys())
