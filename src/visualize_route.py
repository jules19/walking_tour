"""
Route Visualization Module - Phase 2, Step 2.1

Creates interactive HTML maps showing walking tour routes using Folium.
Displays POIs as markers with information, and shows the walking path between them.
"""

import folium
from folium import Marker, PolyLine, Icon
import json
from typing import Dict, List, Optional


def create_route_map(
    route_result: Dict,
    output_file: str,
    zoom_start: int = 15,
    show_all_pois: bool = False,
    all_pois: Optional[List[Dict]] = None
) -> folium.Map:
    """
    Create an interactive map showing the walking route.

    Args:
        route_result: Result from route_planner.plan_route()
        output_file: Path to save HTML map file
        zoom_start: Initial zoom level (default 15)
        show_all_pois: Whether to show candidate POIs not in route
        all_pois: List of all candidate POIs (required if show_all_pois=True)

    Returns:
        folium.Map object
    """
    # Determine map center (middle of route or start position)
    if len(route_result['route']) > 0:
        # Calculate center from all POIs in route
        lats = [stop['poi']['geo']['lat'] for stop in route_result['route']]
        lngs = [stop['poi']['geo']['lng'] for stop in route_result['route']]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)
    else:
        # Use start coords if no POIs in route
        center_lat, center_lng = route_result['start_coords']

    # Create map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )

    # Add start marker
    folium.Marker(
        location=route_result['start_coords'],
        popup='<b>Start</b>',
        tooltip='Starting Point',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)

    # Add route POIs and path
    path_coords = [route_result['start_coords']]

    for i, stop in enumerate(route_result['route'], 1):
        poi = stop['poi']
        coords = (poi['geo']['lat'], poi['geo']['lng'])
        path_coords.append(coords)

        # Create popup with POI information
        popup_html = f"""
        <div style="width: 250px">
            <h4>{i}. {poi['name']}</h4>
            <p><b>Distance from previous:</b> {stop['distance_from_previous_km']:.2f} km</p>
            <p><b>Walking time:</b> {stop['walking_time_minutes']:.1f} min</p>
        """

        if 'vibe_tags' in poi and poi['vibe_tags']:
            tags = ', '.join(poi['vibe_tags'][:5])
            popup_html += f"<p><b>Tags:</b> {tags}</p>"

        if 'metadata' in poi and 'description' in poi['metadata']:
            popup_html += f"<p><i>{poi['metadata']['description']}</i></p>"

        popup_html += "</div>"

        # Add marker with number
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{i}. {poi['name']}",
            icon=folium.Icon(
                color='red',
                icon='info-sign',
                icon_color='white'
            )
        ).add_to(m)

        # Add numbered marker label
        folium.Marker(
            location=coords,
            icon=folium.DivIcon(
                html=f'<div style="font-size: 14pt; color: white; font-weight: bold; background-color: red; border-radius: 50%; width: 25px; height: 25px; text-align: center; line-height: 25px;">{i}</div>'
            )
        ).add_to(m)

    # Add return path if applicable
    if route_result['return_to_start'] and len(path_coords) > 1:
        path_coords.append(route_result['start_coords'])

    # Draw path between POIs
    if len(path_coords) > 1:
        folium.PolyLine(
            path_coords,
            color='blue',
            weight=3,
            opacity=0.7,
            popup=f"Total distance: {route_result['total_distance_km']} km"
        ).add_to(m)

    # Optionally show all candidate POIs not in route
    if show_all_pois and all_pois:
        visited_ids = {stop['poi']['id'] for stop in route_result['route']}

        for poi in all_pois:
            if poi['id'] in visited_ids:
                continue
            if 'geo' not in poi or 'lat' not in poi['geo']:
                continue

            coords = (poi['geo']['lat'], poi['geo']['lng'])

            popup_html = f"""
            <div style="width: 200px">
                <h4>{poi['name']}</h4>
                <p><i>Not included in route</i></p>
            """

            if 'metadata' in poi and 'description' in poi['metadata']:
                popup_html += f"<p>{poi['metadata']['description']}</p>"

            popup_html += "</div>"

            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=poi['name'],
                icon=folium.Icon(color='gray', icon='map-marker', prefix='fa')
            ).add_to(m)

    # Add route summary as a legend
    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 280px; height: auto;
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
        <h4 style="margin-top: 0;">Route Summary</h4>
        <p><b>POIs visited:</b> {route_result['pois_visited']}</p>
        <p><b>Total distance:</b> {route_result['total_distance_km']} km</p>
        <p><b>Walking time:</b> {route_result['walking_time_minutes']:.1f} min</p>
        <p><b>Visit time:</b> {route_result['visit_time_minutes']} min</p>
        <p><b>Total time:</b> {route_result['total_time_minutes']:.1f} min</p>
        {f"<p><b>Return to start:</b> Yes ({route_result['return_distance_km']} km)</p>" if route_result['return_to_start'] else ""}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save map
    m.save(output_file)
    return m


def visualize_from_json(route_json_file: str, output_html_file: str, pois_json_file: Optional[str] = None):
    """
    Create a map from saved route JSON file.

    Args:
        route_json_file: Path to route JSON file
        output_html_file: Path to output HTML map
        pois_json_file: Optional path to all POIs JSON (to show unvisited POIs)
    """
    # Load route
    with open(route_json_file, 'r') as f:
        route_data = json.load(f)

    # Reconstruct route_result format expected by create_route_map
    # Note: This is a simplified version since we don't have full POI data
    route_result = {
        'route': [],
        'total_distance_km': route_data['total_distance_km'],
        'total_time_minutes': route_data['total_time_minutes'],
        'walking_time_minutes': route_data['walking_time_minutes'],
        'visit_time_minutes': route_data['visit_time_minutes'],
        'pois_visited': route_data['pois_visited'],
        'start_coords': tuple(route_data['start_coords']),
        'return_to_start': route_data['return_to_start'],
        'return_distance_km': route_data.get('return_distance_km', 0)
    }

    for stop in route_data['route']:
        route_result['route'].append({
            'poi': {
                'id': stop['poi_id'],
                'name': stop['poi_name'],
                'geo': stop['coordinates']
            },
            'distance_from_previous_km': stop['distance_from_previous_km'],
            'walking_time_minutes': stop['walking_time_minutes']
        })

    # Load all POIs if provided
    all_pois = None
    if pois_json_file:
        with open(pois_json_file, 'r') as f:
            poi_data = json.load(f)
            all_pois = poi_data.get('pois', [])

    # Create map
    create_route_map(
        route_result,
        output_html_file,
        show_all_pois=(all_pois is not None),
        all_pois=all_pois
    )


# Example usage
if __name__ == "__main__":
    import os
    from route_planner import load_pois, plan_route

    # Load POI data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'richmond_pois.json')
    pois = load_pois(data_file)

    print("Creating example route maps...")

    # Create a test route
    route = plan_route(
        start_coords=(54.4025, -1.7367),  # Market Place
        candidate_pois=pois,
        duration_minutes=45,
        visit_time_per_poi=7,
        return_to_start=True
    )

    # Output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'maps')
    os.makedirs(output_dir, exist_ok=True)

    # Create map with route only
    map_file = os.path.join(output_dir, 'example_route.html')
    create_route_map(route, map_file)
    print(f"✓ Route map created: {map_file}")

    # Create map showing all POIs
    map_file_all = os.path.join(output_dir, 'example_route_with_all_pois.html')
    create_route_map(route, map_file_all, show_all_pois=True, all_pois=pois)
    print(f"✓ Route map with all POIs created: {map_file_all}")

    # Test loading from JSON
    route_json = os.path.join(os.path.dirname(__file__), '..', 'output', 'routes',
                              'quick_30_minute_tour_from_market_place.json')
    if os.path.exists(route_json):
        map_from_json = os.path.join(output_dir, 'quick_tour_map.html')
        visualize_from_json(route_json, map_from_json, data_file)
        print(f"✓ Map from JSON created: {map_from_json}")

    print("\nOpen any of the HTML files in a web browser to view the interactive maps!")
