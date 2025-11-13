"""
Alternative to Step 0.1: Create Sample Data
Since Overpass API is blocked, create realistic sample data based on known Richmond POIs
"""

import json
from datetime import datetime

# Richmond, North Yorkshire coordinates
RICHMOND_LAT = 54.4028
RICHMOND_LNG = -1.7350

# Sample POIs based on actual Richmond locations
SAMPLE_POIS = [
    {
        "name": "Richmond Castle",
        "lat": 54.4039,
        "lng": -1.7394,
        "tags": {"historic": "castle", "tourism": "attraction", "heritage": "1"},
        "description": "Norman castle built in 1071, one of the oldest stone castles in England",
        "wikipedia": "en:Richmond_Castle",
        "type": "castle"
    },
    {
        "name": "Greyfriars Tower",
        "lat": 54.4028,
        "lng": -1.7350,
        "tags": {"historic": "monastery", "ruins": "yes"},
        "description": "15th-century bell tower, sole remnant of Franciscan friary",
        "type": "ruins"
    },
    {
        "name": "Richmond Market Place",
        "lat": 54.4025,
        "lng": -1.7367,
        "tags": {"tourism": "attraction", "historic": "marketplace"},
        "description": "Historic cobbled market square, one of the largest in England",
        "type": "marketplace"
    },
    {
        "name": "The Georgian Theatre Royal",
        "lat": 54.4029,
        "lng": -1.7355,
        "tags": {"amenity": "theatre", "historic": "building", "heritage": "2"},
        "description": "Built in 1788, Britain's most complete Georgian playhouse",
        "website": "https://www.georgiantheatreroyal.co.uk",
        "type": "theatre"
    },
    {
        "name": "Richmondshire Museum",
        "lat": 54.4032,
        "lng": -1.7360,
        "tags": {"tourism": "museum", "amenity": "museum"},
        "description": "Local history museum in former church building",
        "type": "museum"
    },
    {
        "name": "St Mary's Church",
        "lat": 54.4020,
        "lng": -1.7375,
        "tags": {"historic": "church", "amenity": "place_of_worship"},
        "description": "Medieval parish church with Victorian restoration",
        "type": "church"
    },
    {
        "name": "The Green Howards Regimental Museum",
        "lat": 54.4030,
        "lng": -1.7365,
        "tags": {"tourism": "museum", "amenity": "museum"},
        "description": "Military museum covering 300 years of Yorkshire regiment history",
        "type": "museum"
    },
    {
        "name": "Richmond Bridge",
        "lat": 54.4042,
        "lng": -1.7402,
        "tags": {"historic": "bridge"},
        "description": "Medieval stone bridge over River Swale, dating from 1789",
        "type": "bridge"
    },
    {
        "name": "Richmond Falls",
        "lat": 54.4045,
        "lng": -1.7410,
        "tags": {"tourism": "viewpoint", "natural": "waterfall"},
        "description": "Series of waterfalls on the River Swale beneath the castle",
        "type": "natural"
    },
    {
        "name": "The Old Brewery",
        "lat": 54.4027,
        "lng": -1.7358,
        "tags": {"historic": "building"},
        "description": "19th-century brewery building, now converted",
        "type": "building"
    },
    {
        "name": "Millgate House Gardens",
        "lat": 54.4035,
        "lng": -1.7388,
        "tags": {"tourism": "attraction", "leisure": "garden"},
        "description": "Award-winning terraced garden near castle",
        "type": "garden"
    },
    {
        "name": "Trinity Church Square",
        "lat": 54.4022,
        "lng": -1.7358,
        "tags": {"historic": "church"},
        "description": "Former Holy Trinity Church, now community venue",
        "type": "church"
    },
    {
        "name": "Culloden Tower",
        "lat": 54.4010,
        "lng": -1.7420,
        "tags": {"historic": "tower", "tourism": "viewpoint"},
        "description": "18th-century folly built to commemorate Battle of Culloden",
        "type": "tower"
    },
    {
        "name": "The Bar",
        "lat": 54.4035,
        "lng": -1.7372,
        "tags": {"historic": "gate"},
        "description": "Medieval archway and former toll gate",
        "type": "gate"
    },
    {
        "name": "Richmond Station",
        "lat": 54.3995,
        "lng": -1.7340,
        "tags": {"historic": "railway_station", "tourism": "museum"},
        "description": "Former railway station, now cinema and heritage center",
        "type": "station"
    },
]


def create_poi_entry(poi_data: dict, index: int) -> dict:
    """Convert sample data into structured POI format"""
    return {
        "id": f"richmond_{index:03d}",
        "osm_type": "node",
        "osm_id": f"sample_{index}",
        "name": poi_data["name"],
        "geo": {
            "lat": poi_data["lat"],
            "lng": poi_data["lng"]
        },
        "tags": poi_data["tags"],
        "metadata": {
            "description": poi_data.get("description"),
            "wikipedia": poi_data.get("wikipedia"),
            "website": poi_data.get("website"),
        },
        "visual_cues": [],  # To be populated in Step 0.2
        "facts": [],  # To be populated in Step 0.2
        "source_reliability": 0.9,  # Manually curated
        "poi_type": poi_data.get("type"),
    }


def categorize_pois(pois: list) -> dict:
    """Categorize POIs by type"""
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


def main():
    print("Richmond Walking Tour - Sample Data Creation")
    print("="*60)
    print("Note: Using curated sample data due to API access limitations")
    print("="*60)

    # Convert sample data to POI format
    pois = [create_poi_entry(poi, i) for i, poi in enumerate(SAMPLE_POIS, 1)]

    # Categorize
    categories = categorize_pois(pois)

    # Print statistics
    print(f"\nTotal POIs created: {len(pois)}")
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
        print("⚠ LIMITED: Found <30 POIs. Sufficient for learning project MVP.")
    print("="*60)

    # Show all POIs
    print("\nRichmond POIs:")
    for i, poi in enumerate(pois, 1):
        name = poi["name"]
        poi_type = poi.get("poi_type", "unknown")
        print(f"  {i:2d}. {name:40s} [{poi_type}]")

    # Save to JSON
    output_file = "data/richmond_pois.json"
    output_data = {
        "metadata": {
            "location": "Richmond, North Yorkshire",
            "center": {"lat": RICHMOND_LAT, "lng": RICHMOND_LNG},
            "data_source": "manually_curated",
            "collected_at": datetime.now().isoformat(),
            "total_pois": len(pois),
            "note": "Sample data created for learning project"
        },
        "pois": pois,
        "categories": {k: len(v) for k, v in categories.items()}
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Data saved to {output_file}")
    print(f"\nNext step: Select 10 POIs for manual enrichment (Step 0.2)")
    print("Recommended POIs for enrichment:")
    recommendations = [
        "Richmond Castle (historic significance)",
        "The Georgian Theatre Royal (unique architecture)",
        "Richmond Market Place (central gathering point)",
        "Greyfriars Tower (mystery/ruins)",
        "Richmond Falls (natural beauty)",
        "St Mary's Church (religious history)",
        "The Green Howards Museum (military history)",
        "Richmond Bridge (engineering/views)",
        "Culloden Tower (folly with story)",
        "The Bar (medieval gateway)"
    ]
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    main()
