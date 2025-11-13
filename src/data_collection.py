"""
Step 0.1: Data Collection Script
Queries OpenStreetMap Overpass API for POIs in Richmond, North Yorkshire
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime


# Richmond, North Yorkshire coordinates
RICHMOND_LAT = 54.4028
RICHMOND_LNG = -1.7350
SEARCH_RADIUS = 2000  # meters

# Try multiple Overpass API instances (in case one is down/blocking)
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter"
]


def build_overpass_query(lat: float, lng: float, radius: int) -> str:
    """
    Build Overpass QL query for POIs in Richmond
    Focuses on: historic, tourism, and amenity tags
    """
    query = f"""
    [out:json][timeout:25];
    (
      // Historic sites
      node["historic"](around:{radius},{lat},{lng});
      way["historic"](around:{radius},{lat},{lng});
      relation["historic"](around:{radius},{lat},{lng});

      // Tourism POIs
      node["tourism"](around:{radius},{lat},{lng});
      way["tourism"](around:{radius},{lat},{lng});
      relation["tourism"](around:{radius},{lat},{lng});

      // Amenities (museums, theatres, etc.)
      node["amenity"]["amenity"~"theatre|cinema|arts_centre|museum|library"](around:{radius},{lat},{lng});
      way["amenity"]["amenity"~"theatre|cinema|arts_centre|museum|library"](around:{radius},{lat},{lng});
    );
    out body;
    >;
    out skel qt;
    """
    return query


def fetch_pois(lat: float, lng: float, radius: int) -> List[Dict[str, Any]]:
    """
    Fetch POIs from OpenStreetMap via Overpass API
    """
    query = build_overpass_query(lat, lng, radius)

    print(f"Querying Overpass API for POIs within {radius}m of Richmond...")
    print(f"Center point: ({lat}, {lng})")

    headers = {
        "User-Agent": "WalkingTourApp/0.1 (Learning Project)"
    }

    # Try multiple Overpass API instances
    for i, url in enumerate(OVERPASS_URLS, 1):
        try:
            print(f"Trying API instance {i}/{len(OVERPASS_URLS)}: {url}")
            response = requests.post(
                url,
                data={"data": query},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Extract elements (nodes, ways, relations)
            elements = data.get("elements", [])
            print(f"✓ Success! Raw elements received: {len(elements)}")

            return elements

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed: {e}")
            if i < len(OVERPASS_URLS):
                print(f"Trying next instance...")
            continue

    print("All Overpass API instances failed.")
    return []


def process_poi(element: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process raw OSM element into structured POI format
    """
    tags = element.get("tags", {})

    # Get coordinates (for nodes, use lat/lon; for ways, we'll need to calculate centroid later)
    if element["type"] == "node":
        lat = element.get("lat")
        lng = element.get("lon")
    else:
        # For ways/relations, we'll skip for now or mark as needing processing
        lat = None
        lng = None

    poi = {
        "id": f"osm_{element['type']}_{element['id']}",
        "osm_type": element["type"],
        "osm_id": element["id"],
        "name": tags.get("name", tags.get("historic", "Unknown")),
        "geo": {
            "lat": lat,
            "lng": lng
        },
        "tags": {
            "historic": tags.get("historic"),
            "tourism": tags.get("tourism"),
            "amenity": tags.get("amenity"),
            "building": tags.get("building"),
            "heritage": tags.get("heritage"),
        },
        "metadata": {
            "description": tags.get("description"),
            "wikipedia": tags.get("wikipedia"),
            "wikidata": tags.get("wikidata"),
            "website": tags.get("website"),
            "opening_hours": tags.get("opening_hours"),
        },
        "raw_tags": tags,  # Keep all tags for reference
        "visual_cues": [],  # To be populated manually in Step 0.2
        "facts": [],  # To be populated manually in Step 0.2
        "source_reliability": 0.8,  # OSM data is generally reliable
    }

    # Remove None values from tags
    poi["tags"] = {k: v for k, v in poi["tags"].items() if v is not None}
    poi["metadata"] = {k: v for k, v in poi["metadata"].items() if v is not None}

    return poi


def categorize_pois(pois: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize POIs by type for easier analysis
    """
    categories = {
        "historic": [],
        "tourism": [],
        "amenity": [],
        "other": []
    }

    for poi in pois:
        tags = poi["tags"]
        if tags.get("historic"):
            categories["historic"].append(poi)
        elif tags.get("tourism"):
            categories["tourism"].append(poi)
        elif tags.get("amenity"):
            categories["amenity"].append(poi)
        else:
            categories["other"].append(poi)

    return categories


def print_statistics(pois: List[Dict[str, Any]], categories: Dict[str, List[Dict[str, Any]]]):
    """
    Print statistics about collected POIs
    """
    print("\n" + "="*60)
    print("POI COLLECTION STATISTICS")
    print("="*60)
    print(f"Total POIs found: {len(pois)}")
    print(f"\nBreakdown by category:")
    print(f"  Historic sites: {len(categories['historic'])}")
    print(f"  Tourism POIs: {len(categories['tourism'])}")
    print(f"  Amenities: {len(categories['amenity'])}")
    print(f"  Other: {len(categories['other'])}")

    print(f"\n{'='*60}")
    print("EVALUATION:")
    if len(pois) >= 50:
        print("✓ PASS: Found 50+ POIs. Richmond has sufficient content!")
    elif len(pois) >= 30:
        print("⚠ BORDERLINE: Found 30-49 POIs. Should be workable but limited.")
    else:
        print("✗ FAIL: Found <30 POIs. Richmond might be too sparse.")
    print("="*60)

    # Show top 10 most interesting POIs
    print("\nTop 10 POIs by name:")
    for i, poi in enumerate(pois[:10], 1):
        name = poi["name"]
        tags = poi["tags"]
        tag_summary = ", ".join([f"{k}:{v}" for k, v in tags.items() if v])
        print(f"  {i}. {name}")
        print(f"     Tags: {tag_summary}")


def main():
    """
    Main execution function
    """
    print("Richmond Walking Tour - Data Collection (Step 0.1)")
    print("="*60)

    # Fetch POIs from OpenStreetMap
    elements = fetch_pois(RICHMOND_LAT, RICHMOND_LNG, SEARCH_RADIUS)

    if not elements:
        print("No POIs found or error occurred.")
        return

    # Process elements into structured POIs
    pois = []
    for element in elements:
        # Only process nodes with coordinates for now (simplifies MVP)
        if element["type"] == "node" and "tags" in element:
            poi = process_poi(element)
            # Only include POIs with names
            if poi["name"] != "Unknown":
                pois.append(poi)

    # Sort by name for consistency
    pois.sort(key=lambda x: x["name"])

    # Categorize POIs
    categories = categorize_pois(pois)

    # Print statistics
    print_statistics(pois, categories)

    # Save to JSON file
    output_file = "data/richmond_pois.json"
    output_data = {
        "metadata": {
            "location": "Richmond, North Yorkshire",
            "center": {"lat": RICHMOND_LAT, "lng": RICHMOND_LNG},
            "search_radius_m": SEARCH_RADIUS,
            "collected_at": datetime.now().isoformat(),
            "total_pois": len(pois),
        },
        "pois": pois,
        "categories": {k: len(v) for k, v in categories.items()}
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Data saved to {output_file}")
    print(f"\nNext step: Review the POIs and select 10 for manual enrichment (Step 0.2)")


if __name__ == "__main__":
    main()
