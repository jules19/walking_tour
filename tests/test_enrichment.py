"""
Test enrichment quality for Step 0.2
"""

import json
from collections import Counter

def test_enrichment_quality():
    """
    Evaluate the quality of POI enrichment
    """
    print("Testing POI Enrichment Quality")
    print("="*60)

    # Load enriched data
    with open("data/richmond_pois.json", 'r') as f:
        data = json.load(f)

    pois = data["pois"]
    enriched_pois = [poi for poi in pois if poi.get("facts")]

    print(f"\n1. COVERAGE TEST")
    print(f"   Total POIs: {len(pois)}")
    print(f"   Enriched POIs: {len(enriched_pois)}")
    print(f"   ✓ Target: 10 POIs" if len(enriched_pois) >= 10 else "   ✗ Need more")

    print(f"\n2. FACTS TEST")
    total_facts = sum(len(poi.get("facts", [])) for poi in enriched_pois)
    avg_facts = total_facts / len(enriched_pois) if enriched_pois else 0
    print(f"   Total facts: {total_facts}")
    print(f"   Average per POI: {avg_facts:.1f}")
    print(f"   ✓ Target: 2-3 facts per POI" if 2 <= avg_facts <= 3 else "   ⚠ Check range")

    # Sample fact lengths
    fact_lengths = [len(fact) for poi in enriched_pois for fact in poi.get("facts", [])]
    avg_fact_length = sum(fact_lengths) / len(fact_lengths) if fact_lengths else 0
    print(f"   Average fact length: {avg_fact_length:.0f} characters")
    print(f"   ✓ Facts are detailed" if avg_fact_length > 100 else "   ⚠ Facts might be too brief")

    print(f"\n3. VISUAL CUES TEST")
    total_cues = sum(len(poi.get("visual_cues", [])) for poi in enriched_pois)
    avg_cues = total_cues / len(enriched_pois) if enriched_pois else 0
    print(f"   Total visual cues: {total_cues}")
    print(f"   Average per POI: {avg_cues:.1f}")
    print(f"   ✓ Good coverage" if avg_cues >= 3 else "   ⚠ Need more cues")

    print(f"\n4. VIBE DIVERSITY TEST")
    all_vibes = []
    for poi in enriched_pois:
        all_vibes.extend(poi.get("vibe_tags", []))

    vibe_counts = Counter(all_vibes)
    unique_vibes = len(vibe_counts)
    print(f"   Unique vibe tags: {unique_vibes}")
    print(f"   Most common vibes:")
    for vibe, count in vibe_counts.most_common(5):
        print(f"     - {vibe}: {count} POIs")

    print(f"\n5. VIBE CATEGORIES CHECK")
    required_categories = {
        "history": False,
        "architecture": False,
        "nature": False,
        "haunted": False,
        "military": False
    }

    for vibe in all_vibes:
        if vibe in required_categories:
            required_categories[vibe] = True

    print("   Coverage of key categories:")
    for category, present in required_categories.items():
        status = "✓" if present else "✗"
        print(f"     {status} {category}")

    all_present = all(required_categories.values())
    print(f"   ✓ All key categories covered" if all_present else "   ⚠ Missing some categories")

    print(f"\n6. SAMPLE QUALITY CHECK")
    print("   Sample POI: Richmond Castle")
    castle = next((poi for poi in pois if poi["name"] == "Richmond Castle"), None)
    if castle:
        print(f"   Facts: {len(castle.get('facts', []))}")
        print(f"   Visual cues: {len(castle.get('visual_cues', []))}")
        print(f"   Vibe tags: {', '.join(castle.get('vibe_tags', []))}")
        print(f"   Sample fact: \"{castle['facts'][0][:100]}...\"")

    print("\n" + "="*60)
    print("OVERALL EVALUATION:")

    checks = [
        len(enriched_pois) >= 10,
        2 <= avg_facts <= 3,
        avg_fact_length > 100,
        avg_cues >= 3,
        unique_vibes >= 10,
        all_present
    ]

    passed = sum(checks)
    total = len(checks)

    print(f"Passed {passed}/{total} quality checks")
    if passed == total:
        print("✓ PASS: Data quality is excellent, ready for Phase 1")
    elif passed >= total - 1:
        print("✓ PASS: Data quality is good, minor improvements possible")
    else:
        print("⚠ REVIEW: Some quality issues need attention")

    return passed == total


if __name__ == "__main__":
    test_enrichment_quality()
