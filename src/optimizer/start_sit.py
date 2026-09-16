"""Start/Sit Optimizer for Fantasy Football lineup decisions."""

from typing import Dict, List, Any, Tuple, Optional, Set
import json
import os
import re
from datetime import datetime, timezone

from config.team_abbreviations import team_full_name


def normalize_name(name: str) -> str:
    """Normalize a player name for matching across data sources.

    Sleeper's full_name and The Odds API's outcome descriptions disagree on
    punctuation for the same real player (e.g. "C.J. Stroud" vs "CJ Stroud"),
    which breaks plain substring matching. Stripping periods fixes the known
    cases without touching hyphens/apostrophes, which are used consistently.
    """
    return re.sub(r'\.', '', name or '').lower().strip()


def estimate_dst_points(opponent_implied_total: Optional[float]) -> Optional[float]:
    """Rough DST fantasy points from the opponent's implied point total.

    Not a real defensive projection (no sack/INT/TD props exist to build one
    from) - just the standard "points allowed" scoring bands from typical DST
    scoring rules, using the Vegas-implied total as a stand-in for points
    allowed. Better than nothing, not a substitute for real defensive stats.
    """
    if opponent_implied_total is None:
        return None
    if opponent_implied_total <= 6:
        return 9.0
    if opponent_implied_total <= 13:
        return 6.0
    if opponent_implied_total <= 17:
        return 4.0
    if opponent_implied_total <= 20:
        return 2.0
    if opponent_implied_total <= 27:
        return 0.0
    if opponent_implied_total <= 34:
        return -1.0
    return -3.0


def estimate_kicker_points(own_implied_total: Optional[float]) -> Optional[float]:
    """Rough kicker fantasy points from the kicker's own team's implied total.

    More expected points for the offense roughly means more scoring drives,
    which means more field goal / extra point chances for the kicker. This
    is a coarse ratio (~0.35 kicker points per implied point), not a model of
    red zone efficiency or field goal distance.
    """
    if own_implied_total is None:
        return None
    return round(own_implied_total * 0.35, 1)


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
        self._projection_index = self._build_projection_index()
        self._team_game_info = self._build_team_game_info()

    def _build_projection_index(self) -> Dict[tuple, List[tuple]]:
        """Bucket projections by (week, format, position) for fast lookups.

        get_player_projection() gets called once per roster player during a
        normal optimize, and once per free agent (hundreds of players) during
        a waiver-wire scan - a full linear scan per call doesn't hold up at
        that volume.
        """
        index: Dict[tuple, List[tuple]] = {}
        for proj in self.projections_cache.get('projections', []):
            key = (proj.get('week', ''), proj.get('format', ''), proj.get('position', ''))
            index.setdefault(key, []).append((normalize_name(proj.get('player', '')), proj))
        return index

    def _build_team_game_info(self) -> Dict[str, Dict[str, Any]]:
        """Map each team's full name to its game context for the current cache.

        Every player projection already carries its game's teams and implied
        totals, so this just collapses that down to one entry per team
        (deduped since every player in a game repeats the same game info).
        """
        teams: Dict[str, Dict[str, Any]] = {}
        for proj in self.projections_cache.get('projections', []):
            home, away = proj.get('home_team'), proj.get('away_team')
            home_total, away_total = proj.get('home_implied_total'), proj.get('away_implied_total')
            week = proj.get('week', '')
            if home and home not in teams:
                teams[home] = {'own_total': home_total, 'opp_total': away_total, 'week': week}
            if away and away not in teams:
                teams[away] = {'own_total': away_total, 'opp_total': home_total, 'week': week}
        return teams

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

        # 2026 NFL Season Schedule (start date of each week)
        week_start_dates_2026 = [
            datetime(2026, 9, 9, tzinfo=timezone.utc),   # Week 1 (Wed)
            datetime(2026, 9, 17, tzinfo=timezone.utc),  # Week 2 (Thu)
            datetime(2026, 9, 24, tzinfo=timezone.utc),  # Week 3 (Thu)
            datetime(2026, 10, 1, tzinfo=timezone.utc),  # Week 4 (Thu)
            datetime(2026, 10, 8, tzinfo=timezone.utc),  # Week 5 (Thu)
            datetime(2026, 10, 15, tzinfo=timezone.utc), # Week 6 (Thu)
            datetime(2026, 10, 22, tzinfo=timezone.utc), # Week 7 (Thu)
            datetime(2026, 10, 29, tzinfo=timezone.utc), # Week 8 (Thu)
            datetime(2026, 11, 5, tzinfo=timezone.utc),  # Week 9 (Thu)
            datetime(2026, 11, 12, tzinfo=timezone.utc), # Week 10 (Thu)
            datetime(2026, 11, 19, tzinfo=timezone.utc), # Week 11 (Thu)
            datetime(2026, 11, 25, tzinfo=timezone.utc), # Week 12 (Wed, Thanksgiving)
            datetime(2026, 12, 3, tzinfo=timezone.utc),  # Week 13 (Thu)
            datetime(2026, 12, 10, tzinfo=timezone.utc), # Week 14 (Thu)
            datetime(2026, 12, 17, tzinfo=timezone.utc), # Week 15 (Thu)
            datetime(2026, 12, 24, tzinfo=timezone.utc), # Week 16 (Thu)
            datetime(2026, 12, 31, tzinfo=timezone.utc), # Week 17 (Thu)
            datetime(2027, 1, 9, tzinfo=timezone.utc),   # Week 18 (Sat)
        ]

        # Find which week we're currently in
        for i, week_start in enumerate(week_start_dates_2026):
            if i < len(week_start_dates_2026) - 1:
                next_week_start = week_start_dates_2026[i + 1]
                if week_start <= now < next_week_start:
                    return f"Week {i + 1}"
            else:
                # Last week (Week 18)
                if now >= week_start:
                    return f"Week {i + 1}"

        # If before Week 1, return Week 1
        if now < week_start_dates_2026[0]:
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
        normalized = normalize_name(player_name)

        # Try next week first (most common case - looking ahead to upcoming games)
        # Then fall back to current week (for Thursday games during the week)
        weeks_to_check = [self.next_week, self.current_week]

        for week_to_check in weeks_to_check:
            candidates = self._projection_index.get((week_to_check, scoring_format, position), [])
            for proj_name, proj in candidates:
                if proj_name == normalized or normalized in proj_name or proj_name in normalized:
                    return (proj.get('total_points', 0), True, week_to_check)

        # No projection found for this player in upcoming weeks
        return (0, False, '')

    def get_dst_or_kicker_projection(self, team_abbr: str, position: str) -> Tuple[float, bool, str]:
        """Estimate a DEF/K projection from the team's implied Vegas totals.

        The Odds API doesn't carry props for defenses or kickers, so these
        can't be built the same way as skill-position projections. This is a
        coarse stand-in (see estimate_dst_points/estimate_kicker_points) so
        DEF/K aren't just always blank - not a real defensive/kicking model.

        Returns:
            Tuple of (projected points, has_projection, week) - has_projection
            is False when the team's game context isn't in the current cache
            (e.g. a bye week).
        """
        game_info = self._team_game_info.get(team_full_name(team_abbr))
        if not game_info:
            return (0, False, '')

        if position == 'DEF':
            points = estimate_dst_points(game_info.get('opp_total'))
        elif position == 'K':
            points = estimate_kicker_points(game_info.get('own_total'))
        else:
            points = None

        if points is None:
            return (0, False, '')

        return (points, True, game_info.get('week', ''))

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

            if position in ['DEF', 'K']:
                team_abbr = player_data.get('team', '')
                projection, has_projection, week = self.get_dst_or_kicker_projection(team_abbr, position)
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

    def get_waiver_wire_targets(
        self,
        rostered_player_ids: Set[str],
        sleeper_players_db: Dict[str, Any],
        scoring_format: str = 'PPR',
        position: str = 'ALL',
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Find free agents (on nobody's roster) sorted by projected points.

        Args:
            rostered_player_ids: Every player_id rostered by anyone in the league
                (union across all rosters, not just the user's)
            sleeper_players_db: Full Sleeper player database
            scoring_format: Scoring format to project in
            position: Position filter ('ALL' or QB/RB/WR/TE/K/DEF), FLEX means RB/WR/TE
            limit: Max number of results

        Returns:
            Free agents with a projection, sorted by projected points descending.
            Players nobody has projected yet (no Vegas line, bye week, etc.) are
            left out rather than padding the list with zeroes.
        """
        relevant_positions = {'QB', 'RB', 'WR', 'TE', 'K', 'DEF'}
        if position == 'FLEX':
            wanted_positions = {'RB', 'WR', 'TE'}
        elif position and position != 'ALL':
            wanted_positions = {position}
        else:
            wanted_positions = relevant_positions

        targets = []
        for player_id, player_data in sleeper_players_db.items():
            if player_id in rostered_player_ids:
                continue

            pos = player_data.get('position')
            if pos not in wanted_positions:
                continue

            full_name = player_data.get('full_name')
            if not full_name:
                continue

            if pos in ('DEF', 'K'):
                proj, has_proj, week = self.get_dst_or_kicker_projection(player_data.get('team', ''), pos)
            else:
                proj, has_proj, week = self.get_player_projection(full_name, pos, scoring_format)

            if not has_proj:
                continue

            targets.append({
                'player_id': player_id,
                'name': full_name,
                'position': pos,
                'team': player_data.get('team', ''),
                'injury_status': player_data.get('injury_status', ''),
                'projection': proj,
                'week': week,
            })

        targets.sort(key=lambda p: p['projection'], reverse=True)
        return targets[:limit]
