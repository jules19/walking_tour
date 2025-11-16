"""
Test script for Phase 2, Step 2.2: POI Scoring with User Preferences

Demonstrates how different user profiles generate different routes from the same starting point.
"""

import os
import sys
from src.route_planner import load_pois, plan_route_with_preferences, get_route_summary
from src.visualize_route import create_route_map
from src.poi_scorer import USER_PROFILES


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def compare_routes():
    """Compare routes generated for different user profiles."""
    print_header("PHASE 2, STEP 2.2: PREFERENCE-BASED ROUTE PLANNING TEST")

    # Load POI data
    data_file = 'data/richmond_pois.json'
    print(f"\n1. Loading POI data from {data_file}...")

    if not os.path.exists(data_file):
        print(f"❌ Error: {data_file} not found!")
        return False

    pois = load_pois(data_file)
    print(f"✓ Loaded {len(pois)} POIs")

    # Count enriched POIs
    enriched = sum(1 for poi in pois if 'facts' in poi and poi['facts'])
    print(f"  - {enriched} POIs have enriched content")

    # Common test parameters
    start_coords = (54.4025, -1.7367)  # Market Place
    start_name = "Market Place"
    duration = 45  # 45-minute tours
    visit_time = 5  # 5 minutes per POI

    # Test different user profiles
    profiles_to_test = [
        'history_lover',
        'ghost_hunter',
        'architecture_fan',
        'nature_seeker'
    ]

    print_header(f"2. Generating routes for {len(profiles_to_test)} different user profiles")
    print(f"\nCommon parameters:")
    print(f"  - Start: {start_name}")
    print(f"  - Duration: {duration} minutes")
    print(f"  - Visit time: {visit_time} minutes per POI")

    # Create output directories
    output_routes_dir = 'output/routes_with_preferences'
    output_maps_dir = 'output/maps_with_preferences'
    os.makedirs(output_routes_dir, exist_ok=True)
    os.makedirs(output_maps_dir, exist_ok=True)

    results = []

    for profile in profiles_to_test:
        print_header(f"Profile: {profile.upper().replace('_', ' ')}")
        profile_info = USER_PROFILES[profile]
        print(f"Description: {profile_info['description']}")
        print(f"Interests: {', '.join(profile_info['interests'])}")
        print()

        # Generate route with preferences
        route = plan_route_with_preferences(
            start_coords=start_coords,
            candidate_pois=pois,
            duration_minutes=duration,
            user_profile=profile,
            visit_time_per_poi=visit_time,
            return_to_start=False
        )

        # Display route
        print(get_route_summary(route))

        # Show POI scores
        if route['pois_visited'] > 0:
            print("\n" + "-" * 60)
            print("POI SCORES (how well each POI matched this profile)")
            print("-" * 60)
            for i, (stop, score) in enumerate(zip(route['route'], route['poi_scores']), 1):
                poi = stop['poi']
                tags = ', '.join(poi.get('vibe_tags', [])[:3]) if 'vibe_tags' in poi else 'none'
                print(f"{i}. {poi['name']}")
                print(f"   Score: {score:.3f} | Tags: {tags}")

        # Create visualization
        filename_base = f"{profile}_45min"
        map_file = os.path.join(output_maps_dir, f'{filename_base}.html')
        create_route_map(route, map_file, show_all_pois=True, all_pois=pois)
        print(f"\n✓ Map created: {map_file}")

        results.append({
            'profile': profile,
            'route': route
        })

        print()

    # Comparison analysis
    print_header("3. ROUTE COMPARISON ANALYSIS")

    print("\nRoutes Generated:")
    print("-" * 80)
    for result in results:
        route = result['route']
        profile = result['profile']
        poi_names = [stop['poi']['name'] for stop in route['route']]

        print(f"\n{profile.upper().replace('_', ' ')}:")
        print(f"  POIs: {route['pois_visited']}")
        print(f"  Distance: {route['total_distance_km']} km")
        print(f"  Route: {' → '.join(poi_names)}")

    # Find unique POIs selected by each profile
    print("\n" + "-" * 80)
    print("UNIQUE POI SELECTIONS (what makes each profile different)")
    print("-" * 80)

    all_poi_sets = {}
    for result in results:
        profile = result['profile']
        poi_ids = {stop['poi']['id'] for stop in result['route']['route']}
        all_poi_sets[profile] = poi_ids

    for result in results:
        profile = result['profile']
        this_set = all_poi_sets[profile]

        # Find POIs unique to this profile
        other_sets = [all_poi_sets[p] for p in profiles_to_test if p != profile]
        if other_sets:
            unique = this_set - set.union(*other_sets)

            if unique:
                print(f"\n{profile.upper().replace('_', ' ')} uniquely visits:")
                for poi_id in unique:
                    poi = next(p for p in pois if p['id'] == poi_id)
                    tags = ', '.join(poi.get('vibe_tags', [])[:3])
                    print(f"  - {poi['name']} ({tags})")

    # Evaluation
    print_header("4. EVALUATION CHECKLIST")

    print("\n✓ Check that different profiles produce different routes")
    print("✓ Verify POIs match the profile interests (check tags)")
    print("✓ Ensure scores are higher for well-matched POIs")
    print("✓ Compare maps side-by-side in browser")

    print(f"\n📍 Interactive maps: {output_maps_dir}/")
    print(f"   Open these files to compare routes visually")

    # Success criteria
    print_header("5. SUCCESS CRITERIA")

    # Check if routes are different
    routes_different = len(set(
        tuple(stop['poi']['id'] for stop in r['route']['route'])
        for r in results
    )) > 1

    if routes_different:
        print("✅ PASS: Different profiles generated different routes")
    else:
        print("⚠️  WARNING: All profiles generated identical routes")
        print("   (This may indicate POI dataset is too small or scoring needs tuning)")

    # Check if high-scoring POIs are included
    scoring_works = all(
        len(r['route']['poi_scores']) > 0 and max(r['route']['poi_scores']) > 0.3
        for r in results if r['route']['pois_visited'] > 0
    )

    if scoring_works:
        print("✅ PASS: POI scoring is working (scores > 0.3)")
    else:
        print("❌ FAIL: POI scores are too low")

    print("\n" + "=" * 80)

    return routes_different and scoring_works


if __name__ == "__main__":
    success = compare_routes()
    sys.exit(0 if success else 1)
