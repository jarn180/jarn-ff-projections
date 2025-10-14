"""Start/Sit Optimizer for Fantasy Football lineup decisions."""

from typing import Dict, List, Any, Tuple, Optional
import json
import os
from datetime import datetime, timezone


class StartSitOptimizer:
    """Optimizes fantasy football lineup decisions based on projections."""

    # Standard Sleeper roster positions
    ROSTER_POSITIONS = {
        'QB': 1,
        'RB': 2,
        'WR': 2,
        'TE': 1,
        'FLEX': 1,  # RB/WR/TE
        'K': 1,
        'DEF': 1,
        'BN': 6  # Bench
    }

    FLEX_POSITIONS = ['RB', 'WR', 'TE']

    def __init__(self):
        """Initialize optimizer."""
        self.projections_cache = self._load_projections()
        self.current_week = self._get_current_week()
        self.next_week = self._get_next_week()
        self.sleeper_players = {}

    def _load_projections(self) -> Dict[str, Any]:
        """Load projections from cache file.

        Returns:
            Dict of cached projections
        """
        cache_file = 'data/projections_cache.json'
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return {'projections': [], 'total_players': 0}

    def _get_current_week(self) -> str:
        """Get current NFL week based on today's date.

        Returns:
            Current week string (e.g., "Week 7")
        """
        now = datetime.now(timezone.utc)

        # 2025 NFL Season Schedule (Thursday start dates for each week)
        week_start_dates_2025 = [
            datetime(2025, 9, 4, tzinfo=timezone.utc),   # Week 1
            datetime(2025, 9, 11, tzinfo=timezone.utc),  # Week 2
            datetime(2025, 9, 18, tzinfo=timezone.utc),  # Week 3
            datetime(2025, 9, 25, tzinfo=timezone.utc),  # Week 4
            datetime(2025, 10, 2, tzinfo=timezone.utc),  # Week 5
            datetime(2025, 10, 9, tzinfo=timezone.utc),  # Week 6
            datetime(2025, 10, 16, tzinfo=timezone.utc), # Week 7
            datetime(2025, 10, 23, tzinfo=timezone.utc), # Week 8
            datetime(2025, 10, 30, tzinfo=timezone.utc), # Week 9
            datetime(2025, 11, 6, tzinfo=timezone.utc),  # Week 10
            datetime(2025, 11, 13, tzinfo=timezone.utc), # Week 11
            datetime(2025, 11, 20, tzinfo=timezone.utc), # Week 12
            datetime(2025, 11, 27, tzinfo=timezone.utc), # Week 13
            datetime(2025, 12, 4, tzinfo=timezone.utc),  # Week 14
            datetime(2025, 12, 11, tzinfo=timezone.utc), # Week 15
            datetime(2025, 12, 18, tzinfo=timezone.utc), # Week 16
            datetime(2025, 12, 25, tzinfo=timezone.utc), # Week 17
            datetime(2026, 1, 1, tzinfo=timezone.utc),   # Week 18
        ]

        # Find which week we're currently in
        for i, week_start in enumerate(week_start_dates_2025):
            if i < len(week_start_dates_2025) - 1:
                next_week_start = week_start_dates_2025[i + 1]
                if week_start <= now < next_week_start:
                    return f"Week {i + 1}"
            else:
                # Last week (Week 18)
                if now >= week_start:
                    return f"Week {i + 1}"

        # If before Week 1, return Week 1
        if now < week_start_dates_2025[0]:
            return "Week 1"

        return "Week 1"

    def _get_next_week(self) -> str:
        """Get next NFL week based on current week.

        Returns:
            Next week string (e.g., "Week 8")
        """
        current_week_num = int(self.current_week.split()[-1])
        next_week_num = min(current_week_num + 1, 18)
        return f"Week {next_week_num}"

    def map_sleeper_to_projections(self, sleeper_player_id: str, sleeper_player: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map Sleeper player to our projection data.

        Args:
            sleeper_player_id: Sleeper player ID
            sleeper_player: Sleeper player data

        Returns:
            Projection data or None if not found
        """
        full_name = sleeper_player.get('full_name', '').lower()
        position = sleeper_player.get('position', '')

        # Try to find matching projection
        for proj in self.projections_cache.get('projections', []):
            proj_name = proj.get('player_name', '').lower()
            proj_position = proj.get('position', '')

            # Exact match
            if proj_name == full_name and proj_position == position:
                return proj

            # Partial match (handles name variations)
            if full_name in proj_name or proj_name in full_name:
                if proj_position == position:
                    return proj

        return None

    def get_player_projection(self, player_name: str, position: str, scoring_format: str = 'PPR') -> tuple[float, bool, str]:
        """Get projected points for a player for the upcoming week.

        Args:
            player_name: Player's full name
            position: Player position (QB, RB, WR, TE)
            scoring_format: Scoring format (PPR, HALF_PPR, STANDARD)

        Returns:
            Tuple of (projected points, has_projection, week)
            - projected points is 0 if not found
            - has_projection is False if player has no lines available
            - week is the week of the projection found
        """
        player_name_lower = player_name.lower()

        # Try next week first (most common case - looking ahead to upcoming games)
        # Then fall back to current week (for Thursday games during the week)
        weeks_to_check = [self.next_week, self.current_week]

        for week_to_check in weeks_to_check:
            for proj in self.projections_cache.get('projections', []):
                proj_name = proj.get('player', '').lower()  # Field is 'player', not 'player_name'
                proj_position = proj.get('position', '')
                proj_format = proj.get('format', '')
                proj_week = proj.get('week', '')

                # Must match position, format, week, and name
                if (proj_position == position and
                    proj_format == scoring_format and
                    proj_week == week_to_check):

                    # Check name matching
                    if (proj_name == player_name_lower or
                        player_name_lower in proj_name or
                        proj_name in player_name_lower):

                        total_points = proj.get('total_points', 0)
                        return (total_points, True, proj_week)

        # No projection found for this player in upcoming weeks
        return (0, False, '')

    def optimize_lineup(
        self,
        roster_players: List[Dict[str, Any]],
        sleeper_players_db: Dict[str, Any],
        scoring_format: str = 'PPR',
        roster_config: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Optimize lineup to maximize projected points.

        Args:
            roster_players: List of player IDs on roster
            sleeper_players_db: Sleeper player database
            scoring_format: Scoring format to use
            roster_config: Custom roster configuration (optional)

        Returns:
            Dict with optimized starters, bench, and analysis
        """
        if roster_config is None:
            roster_config = self.ROSTER_POSITIONS.copy()

        # Get player projections
        player_projections = []
        for player_id in roster_players:
            if not player_id:
                continue

            player_data = sleeper_players_db.get(player_id, {})
            full_name = player_data.get('full_name', 'Unknown')
            position = player_data.get('position', '')
            injury_status = player_data.get('injury_status', '')

            # Skip DEF and K for now (no projections)
            if position in ['DEF', 'K']:
                player_projections.append({
                    'player_id': player_id,
                    'name': full_name,
                    'position': position,
                    'projection': 0,
                    'injury_status': injury_status,
                    'has_projection': False,
                    'no_lines': True,
                    'week': ''
                })
                continue

            projection, has_projection, week = self.get_player_projection(full_name, position, scoring_format)

            player_projections.append({
                'player_id': player_id,
                'name': full_name,
                'position': position,
                'projection': projection,
                'injury_status': injury_status,
                'has_projection': has_projection,
                'no_lines': not has_projection,
                'week': week
            })

        # Sort by projection (highest first)
        player_projections.sort(key=lambda x: x['projection'], reverse=True)

        # Build optimal lineup
        starters = {
            'QB': [],
            'RB': [],
            'WR': [],
            'TE': [],
            'FLEX': [],
            'K': [],
            'DEF': []
        }
        bench = []
        used_players = set()

        # Fill primary positions first
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            max_starters = roster_config.get(position, 0)
            position_players = [p for p in player_projections if p['position'] == position and p['player_id'] not in used_players]

            for i, player in enumerate(position_players):
                if i < max_starters:
                    starters[position].append(player)
                    used_players.add(player['player_id'])

        # Fill FLEX with best remaining RB/WR/TE
        flex_count = roster_config.get('FLEX', 0)
        flex_eligible = [p for p in player_projections if p['position'] in self.FLEX_POSITIONS and p['player_id'] not in used_players]

        for i, player in enumerate(flex_eligible):
            if i < flex_count:
                starters['FLEX'].append(player)
                used_players.add(player['player_id'])

        # Remaining players go to bench
        bench = [p for p in player_projections if p['player_id'] not in used_players]

        # Calculate total projected points
        total_projection = sum(
            sum(p['projection'] for p in players)
            for players in starters.values()
        )

        # Find start/sit recommendations
        recommendations = self._generate_recommendations(starters, bench)

        # Determine which week we're showing (prefer next week)
        projection_week = self.next_week
        # Check if any projections are from current week
        all_players = []
        for pos_players in starters.values():
            all_players.extend(pos_players)
        all_players.extend(bench)

        if all_players:
            weeks_found = [p.get('week') for p in all_players if p.get('week')]
            if weeks_found and self.current_week in weeks_found:
                projection_week = self.current_week

        return {
            'starters': starters,
            'bench': bench,
            'total_projection': round(total_projection, 2),
            'scoring_format': scoring_format,
            'recommendations': recommendations,
            'current_week': projection_week  # The week these projections are for
        }

    def _generate_recommendations(self, starters: Dict[str, List], bench: List[Dict]) -> List[Dict[str, Any]]:
        """Generate start/sit swap recommendations.

        Args:
            starters: Current starting lineup
            bench: Current bench players

        Returns:
            List of recommended swaps
        """
        recommendations = []

        # Check each bench player against starters in their position
        for bench_player in bench:
            position = bench_player['position']
            bench_proj = bench_player['projection']

            # Check primary position
            if position in starters and starters[position]:
                for starter in starters[position]:
                    if bench_proj > starter['projection']:
                        gain = bench_proj - starter['projection']
                        recommendations.append({
                            'action': 'swap',
                            'bench_player': bench_player['name'],
                            'bench_projection': bench_proj,
                            'starter_player': starter['name'],
                            'starter_projection': starter['projection'],
                            'position': position,
                            'projected_gain': round(gain, 2)
                        })

            # Check FLEX if eligible
            if position in self.FLEX_POSITIONS and 'FLEX' in starters and starters['FLEX']:
                for flex_starter in starters['FLEX']:
                    if bench_proj > flex_starter['projection']:
                        gain = bench_proj - flex_starter['projection']
                        recommendations.append({
                            'action': 'swap',
                            'bench_player': bench_player['name'],
                            'bench_projection': bench_proj,
                            'starter_player': flex_starter['name'],
                            'starter_projection': flex_starter['projection'],
                            'position': 'FLEX',
                            'projected_gain': round(gain, 2)
                        })

        # Sort by projected gain
        recommendations.sort(key=lambda x: x['projected_gain'], reverse=True)

        return recommendations[:5]  # Return top 5 recommendations
