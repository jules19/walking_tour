"""
Step 1.2: Integrated Generation + Fact-Checking
Generate narratives and verify them for hallucinations
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Import our existing modules
from generate_tour import (
    load_pois,
    select_pois_by_ids,
    PERSONAS,
    build_tour_prompt
)
from fact_checker import verify_narrative

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_and_verify(
    pois: List[Dict],
    persona_key: str,
    temperature: float = 0.7,
    confidence_threshold: float = 0.9
) -> Dict[str, Any]:
    """
    Generate a tour narrative and verify it for hallucinations

    Args:
        pois: List of POI dictionaries
        persona_key: Persona to use (historian, ghost_hunter, etc.)
        temperature: Generation temperature (0.0-1.0)
        confidence_threshold: Minimum confidence for passing (default 0.9)

    Returns:
        Dict with narrative, verification results, and metadata
    """
    print(f"\n{'='*60}")
    print(f"GENERATING VERIFIED TOUR")
    print(f"{'='*60}")
    print(f"Persona: {PERSONAS[persona_key]['name']}")
    print(f"POIs: {' → '.join([poi['name'] for poi in pois])}")
    print(f"Temperature: {temperature}")
    print(f"Confidence threshold: {confidence_threshold}")

    # Step 1: Generate narrative
    print(f"\n{'='*60}")
    print("STEP 1: GENERATE NARRATIVE")
    print(f"{'='*60}")

    system_prompt, user_prompt = build_tour_prompt(pois, persona_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=2000
        )

        narrative = response.choices[0].message.content
        generation_tokens = response.usage.total_tokens

        print(f"✓ Generated narrative ({response.usage.completion_tokens} tokens)")

    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return None

    # Step 2: Verify narrative
    print(f"\n{'='*60}")
    print("STEP 2: VERIFY FACTS")
    print(f"{'='*60}")

    verification = verify_narrative(narrative, pois)

    # Step 3: Compile results
    result = {
        "persona": persona_key,
        "pois": [{"id": poi["id"], "name": poi["name"]} for poi in pois],
        "narrative": narrative,
        "verification": verification,
        "generation": {
            "model": "gpt-4o",
            "temperature": temperature,
            "tokens": generation_tokens
        },
        "passed_verification": verification.get("pass", False),
        "confidence": verification.get("confidence", 0.0),
        "confidence_threshold": confidence_threshold,
        "generated_at": datetime.now().isoformat()
    }

    # Step 4: Evaluate result
    print(f"\n{'='*60}")
    print("FINAL EVALUATION")
    print(f"{'='*60}")

    passed = result["passed_verification"]
    confidence = result["confidence"]

    if passed and confidence >= confidence_threshold:
        print(f"✓ APPROVED - Narrative passed fact-checking")
        print(f"  Confidence: {confidence:.2f} (threshold: {confidence_threshold})")
        result["status"] = "approved"
    elif passed and confidence < confidence_threshold:
        print(f"⚠ REVIEW NEEDED - Passed but low confidence")
        print(f"  Confidence: {confidence:.2f} (threshold: {confidence_threshold})")
        result["status"] = "review"
    else:
        print(f"✗ REJECTED - Narrative contains hallucinations")
        print(f"  Confidence: {confidence:.2f}")
        hallucinations = verification.get("hallucinations", [])
        print(f"  Hallucinations: {len(hallucinations)}")
        result["status"] = "rejected"

    total_tokens = generation_tokens + verification.get("tokens_used", 0)
    estimated_cost = (total_tokens / 1000) * 0.005  # Rough estimate
    print(f"\n  Total tokens: {total_tokens}")
    print(f"  Estimated cost: ${estimated_cost:.4f}")

    return result


def save_verified_tour(result: Dict[str, Any], output_dir: str = "output/tours"):
    """Save verified tour with verification metadata"""
    os.makedirs(output_dir, exist_ok=True)

    status = result["status"]
    filename = f"tour_{result['persona']}_{status}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Also save readable text version
    txt_filename = filename.replace('.json', '.txt')
    txt_filepath = os.path.join(output_dir, txt_filename)

    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(f"PERSONA: {PERSONAS[result['persona']]['name']}\n")
        f.write(f"STATUS: {status.upper()}\n")
        f.write(f"VERIFICATION: {'PASS' if result['passed_verification'] else 'FAIL'}\n")
        f.write(f"CONFIDENCE: {result['confidence']:.2f}\n")
        f.write(f"ROUTE: {' → '.join([poi['name'] for poi in result['pois']])}\n")
        f.write(f"GENERATED: {result['generated_at']}\n")
        f.write("="*80 + "\n\n")

        if not result['passed_verification']:
            f.write("⚠ HALLUCINATIONS DETECTED:\n")
            for h in result['verification'].get('hallucinations', []):
                f.write(f"  - {h.get('claim')}\n")
                f.write(f"    ({h.get('reason')})\n")
            f.write("\n" + "="*80 + "\n\n")

        f.write(result['narrative'])

    print(f"\n✓ Saved to {filepath}")
    return filepath


def main():
    """
    Test the integrated generation + verification pipeline
    """
    print("Richmond Walking Tour - Verified Generation (Step 1.2)")
    print("="*60)

    # Load POI data
    pois = load_pois()
    print(f"Loaded {len(pois)} POIs")

    # Select test POIs
    test_poi_ids = ["richmond_001", "richmond_002", "richmond_003"]
    selected_pois = select_pois_by_ids(pois, test_poi_ids)

    print(f"\nSelected POIs:")
    for poi in selected_pois:
        print(f"  - {poi['name']}")

    # Generate and verify with one persona as test
    print("\n" + "="*60)
    print("TESTING: Historian persona")
    print("="*60)

    result = generate_and_verify(
        pois=selected_pois,
        persona_key="historian",
        temperature=0.7,
        confidence_threshold=0.9
    )

    if result:
        save_verified_tour(result)

        print("\n" + "="*60)
        print("STEP 1.2 COMPLETE")
        print("="*60)
        print("\nWhat we verified:")
        print("  ✓ Narratives can be generated with GPT-4o")
        print("  ✓ Fact-checking rail catches hallucinations")
        print("  ✓ Verification results include confidence scores")
        print("  ✓ Tours marked as approved/review/rejected")
        print("\nNext: Step 1.3 - Add text-to-speech generation")


if __name__ == "__main__":
    main()
