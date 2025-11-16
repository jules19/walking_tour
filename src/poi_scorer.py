"""
POI Scoring Module - Phase 2, Step 2.2

Implements user preference-based POI scoring to enable personalized route generation.

Scoring Formula:
S_poi = α(interest_match) + β(popularity) - δ(distance)

Where:
- interest_match: How well POI tags match user interests (0-1)
- popularity: POI importance/quality score (0-1)
- distance: Distance from current position (km)
- α, β, δ: Weighting coefficients
"""

from typing import List, Dict, Tuple, Set
import math


# Predefined user preference profiles
USER_PROFILES = {
    'history_lover': {
        'interests': ['history', 'medieval', 'military', 'political', 'victorian'],
        'description': 'Loves historical sites, dates, and significant events'
    },
    'ghost_hunter': {
        'interests': ['haunted', 'mysterious', 'ruins', 'religious', 'dramatic'],
        'description': 'Fascinated by spooky stories, legends, and atmospheric locations'
    },
    'architecture_fan': {
        'interests': ['architecture', 'georgian', 'engineering', 'folly', 'medieval'],
        'description': 'Appreciates building design, construction, and architectural styles'
    },
    'nature_seeker': {
        'interests': ['nature', 'scenic', 'picturesque', 'peaceful', 'romantic'],
        'description': 'Enjoys natural beauty, viewpoints, and tranquil settings'
    },
    'culture_enthusiast': {
        'interests': ['culture', 'arts', 'educational', 'local', 'social'],
        'description': 'Interested in arts, museums, local culture, and community'
    },
    'casual_tourist': {
        'interests': ['history', 'architecture', 'scenic', 'culture', 'picturesque'],
        'description': 'Balanced mix of popular tourist attractions'
    }
}


# Default scoring weights
DEFAULT_WEIGHTS = {
    'alpha': 0.6,    # Interest match weight (most important)
    'beta': 0.3,     # Popularity weight
    'delta': 0.1     # Distance penalty (least important for now)
}


def calculate_interest_match(poi: Dict, user_interests: List[str]) -> float:
    """
    Calculate how well a POI matches user interests using vibe tags.

    Uses Jaccard similarity: intersection / union of tags

    Args:
        poi: POI dictionary with vibe_tags
        user_interests: List of interest keywords

    Returns:
        Match score between 0 and 1
    """
    if 'vibe_tags' not in poi or not poi['vibe_tags']:
        return 0.0

    poi_tags = set(tag.lower() for tag in poi['vibe_tags'])
    user_tags = set(interest.lower() for interest in user_interests)

    if not poi_tags or not user_tags:
        return 0.0

    # Jaccard similarity: |intersection| / |union|
    intersection = len(poi_tags & user_tags)
    union = len(poi_tags | user_tags)

    return intersection / union if union > 0 else 0.0


def calculate_popularity_score(poi: Dict) -> float:
    """
    Calculate POI popularity/quality score.

    For now, uses simple heuristics:
    - Has enriched content (facts, visual cues) = higher score
    - Source reliability score if available

    Args:
        poi: POI dictionary

    Returns:
        Popularity score between 0 and 1
    """
    score = 0.5  # Base score

    # Bonus for enriched content
    if 'facts' in poi and poi['facts']:
        score += 0.3

    if 'visual_cues' in poi and poi['visual_cues']:
        score += 0.1

    # Use source reliability if available
    if 'source_reliability' in poi:
        score = max(score, poi['source_reliability'])

    return min(score, 1.0)


def calculate_distance_penalty(distance_km: float, max_distance: float = 2.0) -> float:
    """
    Calculate distance penalty (normalized).

    Args:
        distance_km: Distance in kilometers
        max_distance: Maximum expected distance for normalization

    Returns:
        Penalty between 0 and 1 (0 = very close, 1 = very far)
    """
    # Normalize distance to 0-1 range
    normalized = min(distance_km / max_distance, 1.0)
    return normalized


def score_poi(
    poi: Dict,
    user_interests: List[str],
    current_position: Tuple[float, float],
    weights: Dict = None
) -> Dict:
    """
    Calculate comprehensive score for a POI.

    Args:
        poi: POI dictionary
        user_interests: List of user interest keywords
        current_position: (lat, lng) current position
        weights: Scoring weights (alpha, beta, delta)

    Returns:
        Dictionary with score and components
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Calculate distance from current position
    from route_planner import calculate_distance
    poi_coords = (poi['geo']['lat'], poi['geo']['lng'])
    distance = calculate_distance(current_position, poi_coords)

    # Calculate score components
    interest_match = calculate_interest_match(poi, user_interests)
    popularity = calculate_popularity_score(poi)
    distance_penalty = calculate_distance_penalty(distance)

    # Combined score
    score = (
        weights['alpha'] * interest_match +
        weights['beta'] * popularity -
        weights['delta'] * distance_penalty
    )

    return {
        'poi': poi,
        'score': score,
        'components': {
            'interest_match': interest_match,
            'popularity': popularity,
            'distance_km': distance,
            'distance_penalty': distance_penalty
        }
    }


def rank_pois(
    candidate_pois: List[Dict],
    user_profile: str,
    current_position: Tuple[float, float],
    weights: Dict = None,
    top_n: int = None
) -> List[Dict]:
    """
    Rank POIs by score for a given user profile.

    Args:
        candidate_pois: List of POI dictionaries
        user_profile: Profile name (from USER_PROFILES) or 'custom'
        current_position: (lat, lng) starting position
        weights: Optional custom scoring weights
        top_n: Return only top N POIs (None = all)

    Returns:
        List of scored POIs sorted by score (highest first)
    """
    # Get user interests
    if user_profile in USER_PROFILES:
        interests = USER_PROFILES[user_profile]['interests']
    else:
        # Default to balanced interests
        interests = USER_PROFILES['casual_tourist']['interests']

    # Score all POIs
    scored_pois = []
    for poi in candidate_pois:
        if 'geo' not in poi or 'lat' not in poi['geo']:
            continue

        scored = score_poi(poi, interests, current_position, weights)
        scored_pois.append(scored)

    # Sort by score (descending)
    scored_pois.sort(key=lambda x: x['score'], reverse=True)

    # Return top N if specified
    if top_n is not None:
        scored_pois = scored_pois[:top_n]

    return scored_pois


def get_profile_description(profile: str) -> str:
    """Get description of a user profile."""
    if profile in USER_PROFILES:
        return USER_PROFILES[profile]['description']
    return "Custom profile"


def print_scored_pois(scored_pois: List[Dict], top_n: int = 10):
    """Print scored POIs in a readable format."""
    print(f"\nTop {min(top_n, len(scored_pois))} POIs by Score:")
    print("=" * 80)

    for i, scored in enumerate(scored_pois[:top_n], 1):
        poi = scored['poi']
        comp = scored['components']

        print(f"\n{i}. {poi['name']}")
        print(f"   Total Score: {scored['score']:.3f}")
        print(f"   - Interest Match: {comp['interest_match']:.3f}")
        print(f"   - Popularity: {comp['popularity']:.3f}")
        print(f"   - Distance: {comp['distance_km']:.2f} km (penalty: {comp['distance_penalty']:.3f})")

        if 'vibe_tags' in poi and poi['vibe_tags']:
            print(f"   - Tags: {', '.join(poi['vibe_tags'][:5])}")


# Example usage / test
if __name__ == "__main__":
    from route_planner import load_pois
    import os

    # Load POI data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'richmond_pois.json')
    pois = load_pois(data_file)

    print("=" * 80)
    print("POI SCORING TEST - Phase 2, Step 2.2")
    print("=" * 80)

    # Test starting position (Market Place)
    start_pos = (54.4025, -1.7367)

    # Test different user profiles
    profiles_to_test = ['history_lover', 'ghost_hunter', 'architecture_fan', 'nature_seeker']

    for profile in profiles_to_test:
        print(f"\n{'=' * 80}")
        print(f"Profile: {profile.upper().replace('_', ' ')}")
        print(f"Description: {USER_PROFILES[profile]['description']}")
        print(f"Interests: {', '.join(USER_PROFILES[profile]['interests'])}")
        print("=" * 80)

        # Rank POIs for this profile
        scored = rank_pois(pois, profile, start_pos)

        # Print top 5
        print_scored_pois(scored, top_n=5)

        print()

    # Compare: same POI, different profiles
    print("\n" + "=" * 80)
    print("COMPARISON: Richmond Castle across profiles")
    print("=" * 80)

    castle = next(poi for poi in pois if poi['name'] == 'Richmond Castle')

    for profile in profiles_to_test:
        interests = USER_PROFILES[profile]['interests']
        scored = score_poi(castle, interests, start_pos)
        print(f"\n{profile}: Score = {scored['score']:.3f}")
        print(f"  Interest match: {scored['components']['interest_match']:.3f}")
