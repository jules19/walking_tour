"""
Route Planning Module - Phase 2, Step 2.1 & 2.2

Implements route planning with walkability constraints and user preference scoring.

Algorithms:
- plan_route(): Greedy nearest-neighbor (Step 2.1)
- plan_route_with_preferences(): Preference-based scoring (Step 2.2)

Step 2.1 Algorithm (Distance-based):
1. Start at given coordinates
2. Find nearest unvisited POI
3. Check if time budget allows visiting it
4. Add to route if feasible, repeat until time exhausted

Step 2.2 Algorithm (Preference-based):
1. Start at given coordinates
2. Score all unvisited POIs based on user preferences
3. Select highest-scoring POI that fits time budget
4. Add to route, repeat until time exhausted
"""

import json
import math
import os
import sys
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import POI scoring (for Phase 2.2)
try:
    import poi_scorer
    score_poi = poi_scorer.score_poi
    USER_PROFILES = poi_scorer.USER_PROFILES
    DEFAULT_WEIGHTS = poi_scorer.DEFAULT_WEIGHTS
except ImportError:
    # Allow module to work without poi_scorer for basic routing
    score_poi = None
    USER_PROFILES = {}
    DEFAULT_WEIGHTS = {}


# Constants
WALKING_SPEED_KMH = 5.0  # Average walking speed
DEFAULT_VISIT_TIME_MINUTES = 5  # Time spent at each POI
EARTH_RADIUS_KM = 6371.0  # Earth's radius for distance calculations


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate great-circle distance between two lat/lng points using Haversine formula.

    Args:
        coord1: (lat, lng) tuple for point 1
        coord2: (lat, lng) tuple for point 2

    Returns:
        Distance in kilometers
    """
    lat1, lng1 = coord1
    lat2, lng2 = coord2

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * c


def estimate_walking_time(distance_km: float) -> float:
    """
    Estimate walking time in minutes based on distance.

    Args:
        distance_km: Distance in kilometers

    Returns:
        Time in minutes
    """
    hours = distance_km / WALKING_SPEED_KMH
    return hours * 60


def plan_route(
    start_coords: Tuple[float, float],
    candidate_pois: List[Dict],
    duration_minutes: int,
    visit_time_per_poi: int = DEFAULT_VISIT_TIME_MINUTES,
    return_to_start: bool = False
) -> Dict:
    """
    Plan an optimal walking route using greedy nearest-neighbor algorithm.

    Args:
        start_coords: (lat, lng) starting coordinates
        candidate_pois: List of POI dictionaries with 'geo' field
        duration_minutes: Total time budget in minutes
        visit_time_per_poi: Time to spend at each POI (minutes)
        return_to_start: Whether route should return to starting point

    Returns:
        Dictionary containing:
        - route: Ordered list of POIs to visit
        - total_distance_km: Total walking distance
        - total_time_minutes: Total time including visits
        - walking_time_minutes: Time spent walking
        - visit_time_minutes: Time spent at POIs
        - pois_visited: Number of POIs in route
        - time_remaining: Unused time budget
    """
    route = []
    visited_ids = set()
    current_position = start_coords
    time_used = 0
    total_distance = 0

    while True:
        # Find nearest unvisited POI
        nearest_poi = None
        nearest_distance = float('inf')

        for poi in candidate_pois:
            # Skip if already visited or missing coordinates
            if poi['id'] in visited_ids:
                continue
            if 'geo' not in poi or 'lat' not in poi['geo'] or 'lng' not in poi['geo']:
                continue

            # Calculate distance from current position
            poi_coords = (poi['geo']['lat'], poi['geo']['lng'])
            distance = calculate_distance(current_position, poi_coords)

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_poi = poi

        # No more POIs to visit
        if nearest_poi is None:
            break

        # Calculate time needed to visit this POI
        walking_time = estimate_walking_time(nearest_distance)
        total_time_needed = walking_time + visit_time_per_poi

        # Check if we have time
        if time_used + total_time_needed > duration_minutes:
            break

        # Add POI to route
        route.append({
            'poi': nearest_poi,
            'distance_from_previous_km': nearest_distance,
            'walking_time_minutes': walking_time
        })

        visited_ids.add(nearest_poi['id'])
        current_position = (nearest_poi['geo']['lat'], nearest_poi['geo']['lng'])
        time_used += total_time_needed
        total_distance += nearest_distance

    # Handle return to start if requested
    return_distance = 0
    return_time = 0
    if return_to_start and len(route) > 0:
        return_distance = calculate_distance(current_position, start_coords)
        return_time = estimate_walking_time(return_distance)

        # Check if we have time to return
        if time_used + return_time <= duration_minutes:
            total_distance += return_distance
            time_used += return_time

    walking_time = sum(stop['walking_time_minutes'] for stop in route) + return_time
    visit_time = len(route) * visit_time_per_poi

    return {
        'route': route,
        'total_distance_km': round(total_distance, 2),
        'total_time_minutes': round(time_used, 1),
        'walking_time_minutes': round(walking_time, 1),
        'visit_time_minutes': visit_time,
        'pois_visited': len(route),
        'time_remaining': duration_minutes - time_used,
        'start_coords': start_coords,
        'return_to_start': return_to_start,
        'return_distance_km': round(return_distance, 2) if return_to_start else 0
    }


def plan_route_with_preferences(
    start_coords: Tuple[float, float],
    candidate_pois: List[Dict],
    duration_minutes: int,
    user_profile: str = 'casual_tourist',
    visit_time_per_poi: int = DEFAULT_VISIT_TIME_MINUTES,
    return_to_start: bool = False,
    scoring_weights: Optional[Dict] = None
) -> Dict:
    """
    Plan a route using user preference-based POI scoring (Phase 2.2).

    Uses POI scoring to prioritize POIs based on user interests rather than
    just proximity. Scores POIs using: S = α(interest) + β(popularity) - δ(distance)

    Args:
        start_coords: (lat, lng) starting coordinates
        candidate_pois: List of POI dictionaries with 'geo' and 'vibe_tags'
        duration_minutes: Total time budget in minutes
        user_profile: Profile name (e.g., 'history_lover', 'ghost_hunter')
        visit_time_per_poi: Time to spend at each POI (minutes)
        return_to_start: Whether route should return to starting point
        scoring_weights: Optional custom weights for scoring (alpha, beta, delta)

    Returns:
        Dictionary containing route info (same format as plan_route) plus:
        - user_profile: Profile used
        - poi_scores: Score for each POI in route
    """
    if score_poi is None:
        raise ImportError("poi_scorer module required for preference-based routing")

    # Get user interests
    if user_profile in USER_PROFILES:
        interests = USER_PROFILES[user_profile]['interests']
    else:
        interests = USER_PROFILES['casual_tourist']['interests']

    weights = scoring_weights if scoring_weights else DEFAULT_WEIGHTS

    route = []
    visited_ids = set()
    current_position = start_coords
    time_used = 0
    total_distance = 0
    poi_scores = []

    while True:
        # Score all unvisited POIs from current position
        best_poi = None
        best_score = -float('inf')
        best_distance = 0

        for poi in candidate_pois:
            # Skip if already visited or missing data
            if poi['id'] in visited_ids:
                continue
            if 'geo' not in poi or 'lat' not in poi['geo'] or 'lng' not in poi['geo']:
                continue

            # Calculate score for this POI
            scored = score_poi(poi, interests, current_position, weights)

            if scored['score'] > best_score:
                best_score = scored['score']
                best_poi = poi
                best_distance = scored['components']['distance_km']

        # No more POIs to visit
        if best_poi is None:
            break

        # Calculate time needed to visit this POI
        walking_time = estimate_walking_time(best_distance)
        total_time_needed = walking_time + visit_time_per_poi

        # Check if we have time
        if time_used + total_time_needed > duration_minutes:
            break

        # Add POI to route
        route.append({
            'poi': best_poi,
            'distance_from_previous_km': best_distance,
            'walking_time_minutes': walking_time
        })

        poi_scores.append(best_score)
        visited_ids.add(best_poi['id'])
        current_position = (best_poi['geo']['lat'], best_poi['geo']['lng'])
        time_used += total_time_needed
        total_distance += best_distance

    # Handle return to start if requested
    return_distance = 0
    return_time = 0
    if return_to_start and len(route) > 0:
        return_distance = calculate_distance(current_position, start_coords)
        return_time = estimate_walking_time(return_distance)

        if time_used + return_time <= duration_minutes:
            total_distance += return_distance
            time_used += return_time

    walking_time = sum(stop['walking_time_minutes'] for stop in route) + return_time
    visit_time = len(route) * visit_time_per_poi

    return {
        'route': route,
        'total_distance_km': round(total_distance, 2),
        'total_time_minutes': round(time_used, 1),
        'walking_time_minutes': round(walking_time, 1),
        'visit_time_minutes': visit_time,
        'pois_visited': len(route),
        'time_remaining': duration_minutes - time_used,
        'start_coords': start_coords,
        'return_to_start': return_to_start,
        'return_distance_km': round(return_distance, 2) if return_to_start else 0,
        'user_profile': user_profile,
        'poi_scores': poi_scores
    }


def get_route_summary(route_result: Dict) -> str:
    """
    Generate a human-readable summary of the route.

    Args:
        route_result: Result from plan_route()

    Returns:
        Formatted string summary
    """
    summary = []
    summary.append("=" * 60)
    summary.append("ROUTE SUMMARY")
    summary.append("=" * 60)
    summary.append(f"POIs visited: {route_result['pois_visited']}")
    summary.append(f"Total distance: {route_result['total_distance_km']} km")
    summary.append(f"Walking time: {route_result['walking_time_minutes']} minutes")
    summary.append(f"Visit time: {route_result['visit_time_minutes']} minutes")
    summary.append(f"Total time: {route_result['total_time_minutes']} minutes")
    summary.append(f"Time remaining: {route_result['time_remaining']:.1f} minutes")

    if route_result['return_to_start']:
        summary.append(f"Return distance: {route_result['return_distance_km']} km")

    summary.append("\n" + "=" * 60)
    summary.append("ROUTE DETAILS")
    summary.append("=" * 60)

    for i, stop in enumerate(route_result['route'], 1):
        poi = stop['poi']
        summary.append(f"\n{i}. {poi['name']}")
        summary.append(f"   Distance from previous: {stop['distance_from_previous_km']:.2f} km")
        summary.append(f"   Walking time: {stop['walking_time_minutes']:.1f} minutes")
        if 'vibe_tags' in poi:
            summary.append(f"   Vibe tags: {', '.join(poi['vibe_tags'][:3])}")

    return "\n".join(summary)


def load_pois(json_file: str) -> List[Dict]:
    """
    Load POIs from JSON file.

    Args:
        json_file: Path to POI data file

    Returns:
        List of POI dictionaries
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data.get('pois', [])


def save_route(route_result: Dict, output_file: str):
    """
    Save route to JSON file.

    Args:
        route_result: Result from plan_route()
        output_file: Path to output file
    """
    # Create serializable version (remove circular references)
    output = {
        'generated_at': datetime.now().isoformat(),
        'total_distance_km': route_result['total_distance_km'],
        'total_time_minutes': route_result['total_time_minutes'],
        'walking_time_minutes': route_result['walking_time_minutes'],
        'visit_time_minutes': route_result['visit_time_minutes'],
        'pois_visited': route_result['pois_visited'],
        'time_remaining': route_result['time_remaining'],
        'start_coords': route_result['start_coords'],
        'return_to_start': route_result['return_to_start'],
        'route': []
    }

    for stop in route_result['route']:
        output['route'].append({
            'poi_id': stop['poi']['id'],
            'poi_name': stop['poi']['name'],
            'coordinates': stop['poi']['geo'],
            'distance_from_previous_km': stop['distance_from_previous_km'],
            'walking_time_minutes': stop['walking_time_minutes']
        })

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)


# Example usage / test
if __name__ == "__main__":
    import os

    # Load POI data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'richmond_pois.json')
    pois = load_pois(data_file)

    print(f"Loaded {len(pois)} POIs from Richmond")

    # Test with different starting points and durations
    test_cases = [
        {
            'name': 'Quick 30-minute tour from Market Place',
            'start': (54.4025, -1.7367),  # Market Place
            'duration': 30,
            'visit_time': 5
        },
        {
            'name': 'Extended 60-minute tour from Castle',
            'start': (54.4039, -1.7394),  # Richmond Castle
            'duration': 60,
            'visit_time': 7
        },
        {
            'name': 'Long 90-minute tour with return to start',
            'start': (54.4028, -1.735),  # Greyfriars Tower
            'duration': 90,
            'visit_time': 10,
            'return': True
        }
    ]

    for test in test_cases:
        print("\n" + "=" * 80)
        print(f"TEST: {test['name']}")
        print("=" * 80)

        route = plan_route(
            start_coords=test['start'],
            candidate_pois=pois,
            duration_minutes=test['duration'],
            visit_time_per_poi=test['visit_time'],
            return_to_start=test.get('return', False)
        )

        print(get_route_summary(route))

        # Save route
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'routes')
        os.makedirs(output_dir, exist_ok=True)

        filename = test['name'].lower().replace(' ', '_').replace('-', '_') + '.json'
        output_file = os.path.join(output_dir, filename)
        save_route(route, output_file)

        print(f"\n✓ Route saved to: {output_file}")
