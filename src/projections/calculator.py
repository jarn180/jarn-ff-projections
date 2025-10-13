"""
Fantasy Football Projection Calculator
Converts Vegas props to fantasy point projections
"""

from typing import Dict, List
from config.scoring_formats import get_scoring_format


class ProjectionCalculator:
    """Calculate fantasy projections from player props."""

    # Mapping from Odds API market keys to our stat categories
    PROP_MAPPINGS = {
        # Passing stats
        "player_pass_yds": ("passing", "yards"),
        "player_pass_tds": ("passing", "touchdowns"),
        "player_pass_interceptions": ("passing", "interceptions"),

        # Rushing stats
        "player_rush_yds": ("rushing", "yards"),
        "player_rush_attempts": ("rushing", "attempts"),  # Can estimate TDs from attempts

        # Receiving stats
        "player_receptions": ("receiving", "receptions"),
        "player_reception_yds": ("receiving", "yards"),

        # Touchdowns (can be any type)
        "player_anytime_td": ("general", "anytime_td"),
    }

    def __init__(self, scoring_format: str = "PPR"):
        """Initialize calculator with a scoring format.

        Args:
            scoring_format: Scoring format name (PPR, HALF_PPR, or STANDARD)
        """
        self.scoring_format = scoring_format
        self.scoring_rules = get_scoring_format(scoring_format)

        if not self.scoring_rules:
            raise ValueError(f"Unknown scoring format: {scoring_format}")

    def calculate_projection(self, player_props: Dict) -> Dict:
        """Calculate fantasy projection for a player.

        Args:
            player_props: Player props dictionary with structure:
                {
                    "name": "Player Name",
                    "props": {
                        "player_pass_yds": 275.5,
                        "player_pass_tds": 2.0,
                        ...
                    }
                }

        Returns:
            Dictionary with fantasy projection and breakdown
        """
        player_name = player_props.get("name", "Unknown")
        props = player_props.get("props", {})

        projection = {
            "player": player_name,
            "format": self.scoring_format,
            "total_points": 0.0,
            "breakdown": {
                "passing": 0.0,
                "rushing": 0.0,
                "receiving": 0.0,
                "fumbles": 0.0,
            },
            "stats": {}
        }

        # Process each prop
        for prop_key, prop_value in props.items():
            if prop_key not in self.PROP_MAPPINGS:
                continue

            category, stat = self.PROP_MAPPINGS[prop_key]

            # Handle special case for anytime TD (needs to be distributed)
            if stat == "anytime_td":
                td_points = self._calculate_anytime_td_value(prop_value, props)
                projection["breakdown"]["rushing"] += td_points.get("rushing", 0)
                projection["breakdown"]["receiving"] += td_points.get("receiving", 0)
                continue

            # Get scoring rules for this category
            if category in self.scoring_rules:
                category_rules = self.scoring_rules[category]

                if stat in category_rules:
                    points = prop_value * category_rules[stat]
                    projection["breakdown"][category] += points
                    projection["stats"][prop_key] = prop_value

        # Estimate some stats if not directly provided
        projection = self._estimate_additional_stats(projection, props)

        # Calculate total
        projection["total_points"] = sum(projection["breakdown"].values())

        return projection

    def _calculate_anytime_td_value(self, anytime_td_prob: float, all_props: Dict) -> Dict:
        """Estimate TD distribution between rushing and receiving.

        Args:
            anytime_td_prob: Probability/line for anytime TD
            all_props: All props for the player (to determine player type)

        Returns:
            Dictionary with TD points breakdown
        """
        points = {"rushing": 0, "receiving": 0}

        # Determine player type based on available props
        has_rush_yds = "player_rush_yds" in all_props
        has_rec_yds = "player_reception_yds" in all_props
        has_pass_yds = "player_pass_yds" in all_props

        # Convert anytime TD to expected TDs (simplified)
        # This is a rough estimation - you may want to refine this
        expected_tds = anytime_td_prob * 0.5  # Rough conversion

        if has_pass_yds:
            # QB - ignore anytime TD props (they're rare)
            return points

        if has_rush_yds and has_rec_yds:
            # RB or flex - split based on usage (can be refined)
            rush_yds = all_props.get("player_rush_yds", 0)
            rec_yds = all_props.get("player_reception_yds", 0)

            total_yds = rush_yds + rec_yds
            if total_yds > 0:
                rush_pct = rush_yds / total_yds
                rec_pct = rec_yds / total_yds
            else:
                rush_pct = 0.7  # Default to more rushing
                rec_pct = 0.3

            points["rushing"] = expected_tds * rush_pct * 6
            points["receiving"] = expected_tds * rec_pct * 6

        elif has_rush_yds:
            # Primarily rushing (RB)
            points["rushing"] = expected_tds * 6

        elif has_rec_yds:
            # Primarily receiving (WR/TE)
            points["receiving"] = expected_tds * 6

        return points

    def _estimate_additional_stats(self, projection: Dict, props: Dict) -> Dict:
        """Estimate additional stats that may not be directly provided.

        Args:
            projection: Current projection dictionary
            props: Raw props

        Returns:
            Updated projection
        """
        # Estimate rushing TDs from rushing yards (very rough)
        if "player_rush_yds" in props and "player_rush_tds" not in props:
            rush_yds = props["player_rush_yds"]
            # Historically, roughly 1 TD per 80-100 rushing yards
            estimated_rush_tds = rush_yds / 90.0
            rush_td_points = estimated_rush_tds * self.scoring_rules["rushing"]["touchdowns"]
            projection["breakdown"]["rushing"] += rush_td_points
            projection["stats"]["estimated_rush_tds"] = estimated_rush_tds

        # Estimate receiving TDs from receiving yards
        if "player_reception_yds" in props and "player_rec_tds" not in props:
            rec_yds = props["player_reception_yds"]
            # Historically, roughly 1 TD per 100-120 receiving yards
            estimated_rec_tds = rec_yds / 110.0
            rec_td_points = estimated_rec_tds * self.scoring_rules["receiving"]["touchdowns"]
            projection["breakdown"]["receiving"] += rec_td_points
            projection["stats"]["estimated_rec_tds"] = estimated_rec_tds

        # Estimate fumbles (very rough - typically 1 fumble per 200 touches)
        rush_att = props.get("player_rush_attempts", 0)
        receptions = props.get("player_receptions", 0)
        total_touches = rush_att + receptions

        if total_touches > 0:
            estimated_fumbles = total_touches / 200.0
            fumble_points = estimated_fumbles * self.scoring_rules["fumbles"]["lost"]
            projection["breakdown"]["fumbles"] += fumble_points
            projection["stats"]["estimated_fumbles"] = estimated_fumbles

        return projection

    def calculate_multiple_formats(self, player_props: Dict, formats: List[str] = None) -> List[Dict]:
        """Calculate projections for multiple scoring formats.

        Args:
            player_props: Player props dictionary
            formats: List of format names. If None, calculates for all formats.

        Returns:
            List of projections, one for each format
        """
        if formats is None:
            formats = ["PPR", "HALF_PPR", "STANDARD"]

        projections = []
        for format_name in formats:
            calc = ProjectionCalculator(format_name)
            projection = calc.calculate_projection(player_props)
            projections.append(projection)

        return projections
