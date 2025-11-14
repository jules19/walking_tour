"""
Step 1.1: Simple Prompt Chain
Generate tour narratives using GPT-4o with different personas
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Persona definitions matching CLAUDE.md
PERSONAS = {
    "historian": {
        "name": "The Historian",
        "description": "Scholarly, precise, and appreciative of historical detail",
        "tone": "formal, date-heavy, focuses on causal relationships",
        "voice_characteristics": "measured pace, emphasis on proper nouns and dates"
    },
    "ghost_hunter": {
        "name": "The Ghost Hunter",
        "description": "Mysterious and atmospheric, focused on dark history",
        "tone": "whispered, suspenseful, immersive in the macabre",
        "voice_characteristics": "dramatic pauses, emphasis on sensory details"
    },
    "local": {
        "name": "The Local",
        "description": "Friendly insider sharing hidden gems and stories",
        "tone": "casual, conversational, uses local slang",
        "voice_characteristics": "warm, familiar, shorter sentences"
    },
    "time_traveler": {
        "name": "The Time Traveler",
        "description": "Transports you to different eras with vivid descriptions",
        "tone": "descriptive, narrative, rich in sensory details",
        "voice_characteristics": "storytelling rhythm, present-tense immersion"
    }
}


def load_pois(filepath: str = "data/richmond_pois.json") -> List[Dict[str, Any]]:
    """Load POI data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["pois"]


def select_pois_by_ids(pois: List[Dict], poi_ids: List[str]) -> List[Dict]:
    """Select specific POIs by their IDs"""
    selected = []
    for poi_id in poi_ids:
        poi = next((p for p in pois if p["id"] == poi_id), None)
        if poi:
            selected.append(poi)
    return selected


def build_tour_prompt(pois: List[Dict], persona_key: str) -> str:
    """
    Build the prompt for GPT-4o to generate tour narrative
    Follows the "Beat Sheet" structure from CLAUDE.md
    """
    persona = PERSONAS[persona_key]

    # Build POI information
    poi_info = []
    for i, poi in enumerate(pois, 1):
        info = f"""
POI {i}: {poi['name']}
Location: {poi['geo']['lat']}, {poi['geo']['lng']}
Visual Cues: {', '.join(poi.get('visual_cues', []))}
Facts:
{chr(10).join(f'  - {fact}' for fact in poi.get('facts', []))}
Vibe Tags: {', '.join(poi.get('vibe_tags', []))}
"""
        poi_info.append(info)

    poi_details = "\n".join(poi_info)

    # Build the system prompt
    system_prompt = f"""You are {persona['name']}, an expert tour guide in Richmond, North Yorkshire.

Your personality:
- {persona['description']}
- Tone: {persona['tone']}
- Voice: {persona['voice_characteristics']}

Your task is to create an engaging walking tour narrative that connects {len(pois)} locations in Richmond.

CRITICAL RULES:
1. Use ONLY the facts provided. Do NOT invent or hallucinate details.
2. Follow the "Beat Sheet" structure for EACH location:
   - The Hook: Start with a provocative question or statement
   - The Visual Anchor: "Look at [specific visual cue]..."
   - The Meat: Tell the historical/cultural story using the provided facts
   - The Synthesis: Connect this to the broader theme or next location
   - Call-to-Move: Clear walking directions to the next POI (for POIs 1-2 only)

3. Maintain your persona's voice throughout
4. Create narrative flow between locations
5. For directional cues, reference the visual landmarks provided

Output format:
For each POI, create a section with:
- A compelling narrative (150-250 words)
- Natural transitions between locations
- Clear visual references for navigation"""

    # Build the user prompt
    user_prompt = f"""Create a walking tour narrative connecting these {len(pois)} locations in order:

{poi_details}

Generate an engaging tour script that:
1. Opens with a strong hook at the first location
2. Weaves the facts into compelling stories
3. Maintains the {persona['name']} persona throughout
4. Includes walking directions between POIs using visual cues
5. Ends with a memorable conclusion at the final location

Remember: Use ONLY the provided facts. Do not invent details."""

    return system_prompt, user_prompt


def generate_narrative(pois: List[Dict], persona_key: str, temperature: float = 0.7) -> Dict[str, Any]:
    """
    Generate tour narrative using GPT-4o
    """
    print(f"\nGenerating narrative with persona: {PERSONAS[persona_key]['name']}")
    print(f"POIs: {' → '.join([poi['name'] for poi in pois])}")
    print(f"Temperature: {temperature}")
    print("-" * 60)

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

        result = {
            "persona": persona_key,
            "pois": [{"id": poi["id"], "name": poi["name"]} for poi in pois],
            "narrative": narrative,
            "model": "gpt-4o",
            "temperature": temperature,
            "generated_at": datetime.now().isoformat(),
            "tokens_used": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }

        print(f"✓ Generated {response.usage.completion_tokens} tokens")
        print(f"✓ Total tokens: {response.usage.total_tokens}")

        return result

    except Exception as e:
        print(f"✗ Error generating narrative: {e}")
        return None


def save_narrative(result: Dict[str, Any], output_dir: str = "output/tours"):
    """Save generated narrative to file"""
    os.makedirs(output_dir, exist_ok=True)

    filename = f"tour_{result['persona']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Also save just the narrative as txt for easy reading
    txt_filename = filename.replace('.json', '.txt')
    txt_filepath = os.path.join(output_dir, txt_filename)

    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(f"PERSONA: {PERSONAS[result['persona']]['name']}\n")
        f.write(f"ROUTE: {' → '.join([poi['name'] for poi in result['pois']])}\n")
        f.write(f"GENERATED: {result['generated_at']}\n")
        f.write("="*80 + "\n\n")
        f.write(result['narrative'])

    print(f"✓ Saved to {filepath}")
    print(f"✓ Saved text to {txt_filepath}")

    return filepath


def main():
    """
    Main execution - Step 1.1 test
    Generate narratives with different personas
    """
    print("Richmond Walking Tour - Narrative Generation (Step 1.1)")
    print("="*60)

    # Load POI data
    pois = load_pois()
    print(f"Loaded {len(pois)} POIs")

    # Select 3 interesting POIs for testing
    # Using: Castle (dramatic), Greyfriars (haunted), Market Place (social)
    test_poi_ids = ["richmond_001", "richmond_002", "richmond_003"]
    selected_pois = select_pois_by_ids(pois, test_poi_ids)

    print(f"\nSelected POIs for test:")
    for poi in selected_pois:
        print(f"  - {poi['name']} ({', '.join(poi.get('vibe_tags', [])[:3])})")

    # Test with different personas
    test_personas = ["historian", "ghost_hunter", "local"]

    print(f"\n{'='*60}")
    print(f"Generating narratives with {len(test_personas)} personas...")
    print(f"{'='*60}")

    results = []
    for persona in test_personas:
        result = generate_narrative(selected_pois, persona)
        if result:
            save_narrative(result)
            results.append(result)

            # Print preview
            print("\nNARRATIVE PREVIEW:")
            print("-" * 60)
            preview = result['narrative'][:500] + "..." if len(result['narrative']) > 500 else result['narrative']
            print(preview)
            print("-" * 60)
            print()

    print("="*60)
    print(f"STEP 1.1 COMPLETE")
    print(f"Generated {len(results)} narratives")
    print("\nEVALUATION:")
    print("Review the generated narratives and check:")
    print("  1. Does each persona have a distinct voice?")
    print("  2. Are the narratives coherent and engaging?")
    print("  3. Do they use only the provided facts (no hallucinations)?")
    print("  4. Are the visual cues and directions clear?")
    print("\nNext: Step 1.2 - Add fact-checking rail to verify accuracy")
    print("="*60)


if __name__ == "__main__":
    main()
