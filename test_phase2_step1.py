"""
Test script for Phase 2, Step 2.1: Route Planning

This script demonstrates the route planning functionality:
1. Load POI data
2. Generate routes with different parameters
3. Visualize routes on interactive maps
4. Validate route constraints
"""

import os
import sys
from src.route_planner import load_pois, plan_route, get_route_summary, save_route
from src.visualize_route import create_route_map


def test_route_planning():
    """Test route planning with various scenarios."""
    print("=" * 80)
    print("PHASE 2, STEP 2.1: ROUTE PLANNING TEST")
    print("=" * 80)

    # Load POI data
    data_file = 'data/richmond_pois.json'
    print(f"\n1. Loading POI data from {data_file}...")

    if not os.path.exists(data_file):
        print(f"❌ Error: {data_file} not found!")
        return False

    pois = load_pois(data_file)
    print(f"✓ Loaded {len(pois)} POIs")

    # Count enriched POIs (those with facts)
    enriched = sum(1 for poi in pois if 'facts' in poi and poi['facts'])
    print(f"  - {enriched} POIs have enriched content (facts, visual cues)")

    # Test scenarios
    scenarios = [
        {
            'name': '🎯 Quick Lunchtime Tour (30 min)',
            'start': (54.4025, -1.7367),  # Market Place
            'start_name': 'Market Place',
            'duration': 30,
            'visit_time': 5,
            'return': False
        },
        {
            'name': '🏰 Castle Explorer Tour (60 min)',
            'start': (54.4039, -1.7394),  # Richmond Castle
            'start_name': 'Richmond Castle',
            'duration': 60,
            'visit_time': 8,
            'return': False
        },
        {
            'name': '🔄 Circular Walking Tour (90 min)',
            'start': (54.4028, -1.735),  # Greyfriars Tower
            'start_name': 'Greyfriars Tower',
            'duration': 90,
            'visit_time': 10,
            'return': True
        }
    ]

    print(f"\n2. Testing {len(scenarios)} route scenarios...\n")

    output_routes_dir = 'output/routes'
    output_maps_dir = 'output/maps'
    os.makedirs(output_routes_dir, exist_ok=True)
    os.makedirs(output_maps_dir, exist_ok=True)

    results = []

    for i, scenario in enumerate(scenarios, 1):
        print("=" * 80)
        print(f"Scenario {i}: {scenario['name']}")
        print("=" * 80)
        print(f"Start: {scenario['start_name']}")
        print(f"Duration: {scenario['duration']} minutes")
        print(f"Visit time per POI: {scenario['visit_time']} minutes")
        print(f"Return to start: {'Yes' if scenario['return'] else 'No'}")
        print()

        # Plan route
        route = plan_route(
            start_coords=scenario['start'],
            candidate_pois=pois,
            duration_minutes=scenario['duration'],
            visit_time_per_poi=scenario['visit_time'],
            return_to_start=scenario['return']
        )

        # Display summary
        print(get_route_summary(route))

        # Validate constraints
        print("\n" + "-" * 60)
        print("VALIDATION")
        print("-" * 60)

        time_ok = route['total_time_minutes'] <= scenario['duration']
        print(f"✓ Time constraint: {route['total_time_minutes']:.1f} / {scenario['duration']} min "
              f"({'PASS' if time_ok else 'FAIL'})")

        if route['pois_visited'] > 0:
            print(f"✓ Route generated: {route['pois_visited']} POIs")
            print(f"✓ Efficiency: {route['time_remaining']:.1f} min unused "
                  f"({100 * route['time_remaining'] / scenario['duration']:.1f}%)")
        else:
            print("⚠ Warning: No POIs could be visited in time budget")

        # Save route
        filename_base = scenario['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('🎯', '').replace('🏰', '').replace('🔄', '').strip()
        route_file = os.path.join(output_routes_dir, f'{filename_base}.json')
        save_route(route, route_file)
        print(f"✓ Route saved: {route_file}")

        # Create visualization
        map_file = os.path.join(output_maps_dir, f'{filename_base}.html')
        create_route_map(route, map_file, show_all_pois=True, all_pois=pois)
        print(f"✓ Map created: {map_file}")

        results.append({
            'scenario': scenario['name'],
            'route': route,
            'validation': time_ok
        })

        print()

    # Final summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total scenarios tested: {len(scenarios)}")
    passed = sum(1 for r in results if r['validation'])
    print(f"Passed validation: {passed} / {len(scenarios)}")
    print()

    for result in results:
        status = "✓ PASS" if result['validation'] else "✗ FAIL"
        print(f"{status} - {result['scenario']}")
        print(f"       {result['route']['pois_visited']} POIs, "
              f"{result['route']['total_distance_km']} km, "
              f"{result['route']['total_time_minutes']:.1f} min")

    print("\n" + "=" * 80)
    print("EVALUATION QUESTIONS")
    print("=" * 80)
    print("Open the HTML map files in a browser and check:\n")
    print("1. ✓ Route Logic: Does the route make sense geographically?")
    print("2. ✓ No Backtracking: Is the path efficient without weird loops?")
    print("3. ✓ Time Constraints: Did all routes stay within time budget?")
    print("4. ✓ POI Selection: Are nearby POIs being selected (greedy nearest)?")
    print("5. ✓ Circular Routes: Do return routes properly close the loop?")
    print("\n" + "=" * 80)
    print(f"📍 View interactive maps in: {output_maps_dir}/")
    print(f"📄 View route data in: {output_routes_dir}/")
    print("=" * 80)

    return all(r['validation'] for r in results)


if __name__ == "__main__":
    success = test_route_planning()
    sys.exit(0 if success else 1)
