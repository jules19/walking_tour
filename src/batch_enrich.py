"""
Batch Enrichment Script - Phase 2.5

Enriches multiple POIs from a JSON file and saves the enriched results.

Usage:
    python src/batch_enrich.py --input data/raw_pois.json --output data/enriched_pois.json

Or use interactively to enrich specific POIs from the current dataset.
"""

import json
import argparse
import os
from typing import List, Dict
from auto_enrich_pois import enrich_poi


def load_pois_from_file(file_path: str) -> List[Dict]:
    """Load POIs from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Handle both formats: direct list or dict with 'pois' key
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'pois' in data:
        return data['pois']
    else:
        raise ValueError("Invalid POI file format")


def save_enriched_pois(pois: List[Dict], output_file: str, metadata: Dict = None):
    """Save enriched POIs to JSON file."""
    output = {
        'metadata': metadata or {
            'enriched_at': pois[0]['enrichment_metadata']['enriched_at'] if pois else None,
            'total_pois': len(pois),
            'enrichment_method': 'auto_enrich_pois.py'
        },
        'pois': pois
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Saved {len(pois)} enriched POIs to: {output_file}")


def enrich_batch(input_file: str, output_file: str, verify: bool = True, skip_existing: bool = True):
    """
    Enrich a batch of POIs from input file.

    Args:
        input_file: Path to input POI JSON file
        output_file: Path to output enriched POI JSON file
        verify: Whether to run fact-checking verification
        skip_existing: Skip POIs that already have facts
    """
    print("="*80)
    print("BATCH POI ENRICHMENT")
    print("="*80)

    # Load POIs
    print(f"\nLoading POIs from: {input_file}")
    pois = load_pois_from_file(input_file)
    print(f"✓ Loaded {len(pois)} POIs")

    # Filter POIs to enrich
    to_enrich = []
    for poi in pois:
        if skip_existing and 'facts' in poi and poi['facts']:
            print(f"  ⊘ Skipping {poi['name']} (already enriched)")
        else:
            to_enrich.append(poi)

    print(f"\n→ {len(to_enrich)} POIs to enrich")

    if not to_enrich:
        print("\n✓ No POIs need enrichment!")
        return

    # Enrich each POI
    enriched_pois = []
    failed_pois = []
    total_tokens = 0

    for i, poi in enumerate(to_enrich, 1):
        print(f"\n[{i}/{len(to_enrich)}]")
        try:
            enriched = enrich_poi(poi, verify=verify)
            if enriched:
                enriched_pois.append(enriched)
                total_tokens += enriched['enrichment_metadata']['total_tokens_used']
            else:
                failed_pois.append(poi['name'])
        except Exception as e:
            print(f"  ✗ Error enriching {poi['name']}: {e}")
            failed_pois.append(poi['name'])

    # Combine with already-enriched POIs
    if skip_existing:
        already_enriched = [p for p in pois if 'facts' in p and p['facts']]
        all_pois = already_enriched + enriched_pois
    else:
        all_pois = enriched_pois

    # Save results
    print("\n" + "="*80)
    print("ENRICHMENT SUMMARY")
    print("="*80)
    print(f"Successfully enriched: {len(enriched_pois)}")
    print(f"Failed: {len(failed_pois)}")
    if failed_pois:
        print(f"Failed POIs: {', '.join(failed_pois)}")
    print(f"Total tokens used: {total_tokens}")
    print(f"Estimated cost: ${total_tokens * 0.000005:.4f}")  # GPT-4o pricing estimate

    save_enriched_pois(all_pois, output_file, metadata={
        'enriched_at': enriched_pois[0]['enrichment_metadata']['enriched_at'] if enriched_pois else None,
        'total_pois': len(all_pois),
        'newly_enriched': len(enriched_pois),
        'already_enriched': len(all_pois) - len(enriched_pois),
        'failed': len(failed_pois),
        'total_tokens_used': total_tokens,
        'enrichment_method': 'auto_enrich_pois.py with batch_enrich.py'
    })


def interactive_enrich():
    """Interactive mode to select and enrich specific POIs."""
    print("="*80)
    print("INTERACTIVE POI ENRICHMENT")
    print("="*80)

    # Load existing POI data
    data_file = 'data/richmond_pois.json'
    if not os.path.exists(data_file):
        print(f"\n✗ Error: {data_file} not found!")
        return

    pois = load_pois_from_file(data_file)

    # Show POIs without enrichment
    unenriched = [p for p in pois if not p.get('facts')]

    print(f"\nFound {len(pois)} total POIs")
    print(f"  - {len(pois) - len(unenriched)} already enriched")
    print(f"  - {len(unenriched)} not enriched")

    if not unenriched:
        print("\n✓ All POIs already enriched!")
        return

    print("\nUnenriched POIs:")
    for i, poi in enumerate(unenriched, 1):
        poi_type = poi.get('tags', {}).get('historic') or poi.get('tags', {}).get('tourism') or 'unknown'
        print(f"  {i}. {poi['name']} ({poi_type})")

    print(f"\n  A. Enrich all {len(unenriched)} POIs")
    print("  Q. Quit")

    choice = input("\nSelect POI to enrich (number, A, or Q): ").strip().upper()

    if choice == 'Q':
        return
    elif choice == 'A':
        selected_pois = unenriched
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(unenriched):
                selected_pois = [unenriched[idx]]
            else:
                print("Invalid selection")
                return
        except ValueError:
            print("Invalid selection")
            return

    # Enrich selected POIs
    enriched = []
    for poi in selected_pois:
        result = enrich_poi(poi, verify=True)
        if result:
            enriched.append(result)

    # Update and save
    if enriched:
        # Merge with existing POIs
        poi_dict = {p['id']: p for p in pois}
        for e_poi in enriched:
            poi_dict[e_poi['id']] = e_poi

        all_pois = list(poi_dict.values())
        save_enriched_pois(all_pois, data_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch enrich POIs with facts, visual cues, and vibe tags')
    parser.add_argument('--input', '-i', help='Input POI JSON file')
    parser.add_argument('--output', '-o', help='Output enriched POI JSON file')
    parser.add_argument('--no-verify', action='store_true', help='Skip fact verification')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')

    args = parser.parse_args()

    if args.interactive or (not args.input and not args.output):
        interactive_enrich()
    elif args.input and args.output:
        enrich_batch(args.input, args.output, verify=not args.no_verify)
    else:
        parser.print_help()
