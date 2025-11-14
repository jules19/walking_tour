"""
Step 1.2: Fact-Checking Rail
Verify generated narratives contain no hallucinations using GPT-4o-mini
"""

import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_verification_prompt(narrative: str, source_facts: List[Dict[str, Any]]) -> tuple[str, str]:
    """
    Build prompts for fact-checking the narrative against source facts
    """

    # Compile all source facts
    fact_list = []
    for poi in source_facts:
        poi_name = poi.get("name", "Unknown")
        facts = poi.get("facts", [])

        fact_list.append(f"\n{poi_name}:")
        for fact in facts:
            fact_list.append(f"  - {fact}")

    source_text = "\n".join(fact_list)

    system_prompt = """You are a fact-checker for historical tour narratives. Your job is to catch FACTUAL ERRORS and INVENTED INFORMATION, not to penalize engaging storytelling.

WHAT TO FLAG AS HALLUCINATIONS (these are REAL problems):
- Wrong dates, numbers, or measurements (e.g., "built in 1650" when source says "1071")
- Non-existent people, buildings, or events (e.g., "King Henry VIII visited" with no source support)
- False attributions (e.g., "designed by Christopher Wren" when architect is unknown)
- Invented physical features (e.g., "stone lion statue" when no such statue exists)
- Contradictions of source facts (e.g., "made of wood" when source says "stone")

WHAT NOT TO FLAG (these are ACCEPTABLE narrative devices):
- Poetic/metaphorical language (e.g., "stones whisper tales", "weathered grey walls")
- Sensory descriptions (e.g., "imposing structure", "ancient walls")
- Reasonable historical interpretations connecting stated facts (e.g., "sought to secure the North" when granted northern lands)
- Standard historical phrasing (e.g., "reflects the turbulent times" about documented religious changes)
- Narrative transitions (e.g., "evolved from medieval market" when continuity is documented)
- Atmospheric framing (e.g., "complex tapestry of history", "speaks to")
- Minor date conversions (e.g., "1071" vs "eleventh century" vs "late 1000s")
- Navigation cues and directional language

BE STRICT ABOUT FACTS, LENIENT ABOUT STYLE.

Output a JSON object with this exact structure:
{
  "pass": true/false,
  "confidence": 0.0-1.0,
  "hallucinations": [
    {
      "claim": "the specific factual claim from the narrative",
      "reason": "why this contradicts or adds unsupported facts"
    }
  ],
  "warnings": [
    {
      "claim": "borderline claim that might need review",
      "reason": "why it's borderline"
    }
  ]
}

Set "pass": false ONLY if factual hallucinations are detected (wrong facts, invented information).
Set "confidence" based on how certain you are (0.9+ is high confidence)."""

    user_prompt = f"""SOURCE FACTS (Ground Truth):
{source_text}

NARRATIVE TO VERIFY:
{narrative}

Check if the narrative contains any claims not supported by the source facts. Output JSON only."""

    return system_prompt, user_prompt


def verify_narrative(narrative: str, source_pois: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify that narrative uses only provided facts
    Returns verification result with pass/fail and any hallucinations
    """
    print("\nFact-checking narrative...")
    print("-" * 60)

    system_prompt, user_prompt = build_verification_prompt(narrative, source_pois)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model, sufficient for verification
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,  # Deterministic for consistency
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # Add metadata
        result["tokens_used"] = response.usage.total_tokens
        result["model"] = "gpt-4o-mini"

        # Print results
        if result.get("pass"):
            print(f"✓ PASS - No hallucinations detected")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"✗ FAIL - Hallucinations detected")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            hallucinations = result.get("hallucinations", [])
            print(f"  Found {len(hallucinations)} hallucination(s):")
            for h in hallucinations:
                print(f"    - {h.get('claim')}")
                print(f"      Reason: {h.get('reason')}")

        warnings = result.get("warnings", [])
        if warnings:
            print(f"  ⚠ {len(warnings)} warning(s):")
            for w in warnings:
                print(f"    - {w.get('claim')}")

        print(f"  Tokens used: {result['tokens_used']}")

        return result

    except Exception as e:
        print(f"✗ Error during verification: {e}")
        return {
            "pass": False,
            "confidence": 0.0,
            "error": str(e),
            "hallucinations": [],
            "warnings": []
        }


def test_fact_checker():
    """
    Test the fact-checker with both good and bad narratives
    """
    print("="*60)
    print("FACT-CHECKER TEST")
    print("="*60)

    # Sample POI data
    test_pois = [
        {
            "name": "Richmond Castle",
            "facts": [
                "Richmond Castle was built starting in 1071 by Alan Rufus, a Breton nobleman who fought at the Battle of Hastings.",
                "The castle's keep is 100 feet tall and is called Scotland's Hall.",
                "During World War I, the castle was used as a prison for conscientious objectors."
            ]
        }
    ]

    # Test 1: Good narrative (uses only provided facts)
    print("\nTest 1: GOOD NARRATIVE (should pass)")
    print("-" * 60)
    good_narrative = """Welcome to Richmond Castle, one of England's most historic fortresses.
    Look up at the massive stone keep rising above you - that's Scotland's Hall, standing 100 feet tall.

    This castle was built in 1071 by Alan Rufus, a Breton nobleman who had fought alongside William
    the Conqueror at the Battle of Hastings just five years earlier.

    The castle has witnessed centuries of history. During World War I, these ancient walls served a
    darker purpose - as a prison for conscientious objectors, men who refused to fight."""

    result1 = verify_narrative(good_narrative, test_pois)

    # Test 2: Bad narrative (contains hallucinations)
    print("\n\nTest 2: BAD NARRATIVE (should fail)")
    print("-" * 60)
    bad_narrative = """Welcome to Richmond Castle, built in 1071 by Alan Rufus.

    The castle was originally constructed with wood, but was later rebuilt in stone in 1086.
    King Henry VIII visited this castle three times and held lavish banquets in the great hall.

    The 100-foot keep, Scotland's Hall, was named after Scottish prisoners held here during
    the Wars of Scottish Independence. During World War I, it housed conscientious objectors."""

    result2 = verify_narrative(bad_narrative, test_pois)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Good): {'PASS' if result1.get('pass') else 'FAIL'} ✓" if result1.get('pass') else f"Test 1 (Good): {'PASS' if result1.get('pass') else 'FAIL'} ✗")
    print(f"Test 2 (Bad):  {'FAIL' if not result2.get('pass') else 'PASS'} ✓" if not result2.get('pass') else f"Test 2 (Bad):  {'FAIL' if not result2.get('pass') else 'PASS'} ✗")

    if result1.get('pass') and not result2.get('pass'):
        print("\n✓ Fact-checker working correctly!")
    else:
        print("\n⚠ Fact-checker needs adjustment")

    return result1, result2


if __name__ == "__main__":
    test_fact_checker()
