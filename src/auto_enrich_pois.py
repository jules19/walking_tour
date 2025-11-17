"""
Auto-Enrichment Module - Phase 2.5

Automatically enriches POI data using GPT-4o to generate:
- Historical/interesting facts (2-3 per POI)
- Visual cues for navigation
- Vibe tags for preference matching

Uses existing fact-checking system to validate generated content.

This enables rapid expansion to new locations without manual research.
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Available vibe tags (from existing system)
AVAILABLE_VIBE_TAGS = [
    'history', 'architecture', 'military', 'medieval', 'dramatic',
    'ruins', 'religious', 'haunted', 'mysterious', 'peaceful',
    'nature', 'scenic', 'picturesque', 'romantic', 'engineering',
    'culture', 'arts', 'educational', 'local', 'social',
    'commerce', 'victorian', 'georgian', 'political', 'eccentric',
    'folly', 'valor', 'patriotic', 'community', 'intimate'
]


def generate_poi_facts(poi: Dict, num_facts: int = 3) -> Dict:
    """
    Generate historical/interesting facts about a POI using GPT-4o.

    Args:
        poi: POI dictionary with name, type, and basic metadata
        num_facts: Number of facts to generate (default 3)

    Returns:
        Dictionary with facts, sources, and generation metadata
    """
    poi_name = poi.get('name', 'Unknown')
    poi_type = poi.get('tags', {}).get('historic') or poi.get('tags', {}).get('tourism') or 'landmark'
    location = poi.get('metadata', {}).get('location', 'Richmond, North Yorkshire, England')
    description = poi.get('metadata', {}).get('description', '')

    prompt = f"""You are a local historian researching points of interest for an audio walking tour.

POI Name: {poi_name}
Type: {poi_type}
Location: {location}
{f'Description: {description}' if description else ''}

Generate exactly {num_facts} interesting, factual statements about this location. Each fact should:
1. Be historically accurate and verifiable
2. Be 1-2 sentences long
3. Include specific details (dates, names, numbers) when possible
4. Be engaging and suitable for audio narration
5. Focus on different aspects (history, architecture, cultural significance, notable events, etc.)

CRITICAL RULES:
- Only state facts you are confident are true
- Include specific dates, names, and numbers when you know them
- If you're uncertain about a detail, don't include it
- Cite the general source of information (e.g., "historical records show...", "built in...")
- Avoid speculation or "maybe" statements

Format your response as a JSON object:
{{
  "facts": ["fact 1", "fact 2", "fact 3"],
  "confidence": 0.X (0-1 scale, how confident you are in these facts),
  "source_notes": "brief note about information sources"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a meticulous historian who only states verifiable facts. You have access to historical records and local knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for factual accuracy
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'facts': result.get('facts', []),
            'confidence': result.get('confidence', 0.7),
            'source_notes': result.get('source_notes', 'General historical knowledge'),
            'model': 'gpt-4o',
            'tokens_used': response.usage.total_tokens,
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error generating facts for {poi_name}: {e}")
        return {
            'facts': [],
            'confidence': 0.0,
            'source_notes': f'Error: {str(e)}',
            'error': str(e)
        }


def generate_visual_cues(poi: Dict, num_cues: int = 4) -> Dict:
    """
    Generate visual navigation cues for a POI using GPT-4o.

    Args:
        poi: POI dictionary with name and type
        num_cues: Number of visual cues to generate (default 4)

    Returns:
        Dictionary with visual cues and metadata
    """
    poi_name = poi.get('name', 'Unknown')
    poi_type = poi.get('tags', {}).get('historic') or poi.get('tags', {}).get('tourism') or 'landmark'
    description = poi.get('metadata', {}).get('description', '')

    prompt = f"""You are helping create audio walking tour navigation cues.

POI Name: {poi_name}
Type: {poi_type}
{f'Description: {description}' if description else ''}

Generate exactly {num_cues} specific visual cues that would help someone identify this location while walking. These will be read aloud in an audio tour.

Visual cues should be:
1. Specific and observable (colors, materials, shapes, distinctive features)
2. Useful for navigation ("look for the...", "you'll see...")
3. Relatively permanent (not temporary signs or decorations)
4. Described in simple language suitable for audio
5. Varied (building features, surroundings, architectural details, etc.)

Examples of good visual cues:
- "Tall stone tower with arched windows"
- "Red brick building with white columns at the entrance"
- "Large oak tree in front of the gates"
- "Cobblestone path leading to the entrance"

Format your response as a JSON object:
{{
  "visual_cues": ["cue 1", "cue 2", "cue 3", "cue 4"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at creating clear, specific visual navigation cues for audio tours."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'visual_cues': result.get('visual_cues', []),
            'model': 'gpt-4o',
            'tokens_used': response.usage.total_tokens,
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error generating visual cues for {poi_name}: {e}")
        return {
            'visual_cues': [],
            'error': str(e)
        }


def classify_vibe_tags(poi: Dict, facts: List[str]) -> Dict:
    """
    Classify vibe tags for a POI based on its facts and description.

    Args:
        poi: POI dictionary
        facts: List of generated facts

    Returns:
        Dictionary with classified vibe tags and metadata
    """
    poi_name = poi.get('name', 'Unknown')
    poi_type = poi.get('tags', {}).get('historic') or poi.get('tags', {}).get('tourism') or 'landmark'
    description = poi.get('metadata', {}).get('description', '')
    facts_text = '\n'.join(f"- {fact}" for fact in facts)

    available_tags_str = ', '.join(AVAILABLE_VIBE_TAGS)

    prompt = f"""You are categorizing a point of interest for a walking tour app.

POI Name: {poi_name}
Type: {poi_type}
{f'Description: {description}' if description else ''}

Facts about this POI:
{facts_text}

Based on this information, select 3-6 vibe tags that best describe this location's character and appeal.

Available tags: {available_tags_str}

Selection criteria:
- Choose tags that match the POI's historical significance, atmosphere, and visitor appeal
- Prioritize the most distinctive characteristics
- Include at least one primary category (history, nature, architecture, culture)
- Add atmospheric tags if relevant (haunted, peaceful, dramatic, mysterious)
- Maximum 6 tags, minimum 3 tags

Format your response as a JSON object:
{{
  "vibe_tags": ["tag1", "tag2", "tag3"],
  "reasoning": "brief explanation of tag selection"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at categorizing tourist attractions by their character and appeal."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Validate tags are from available list
        tags = result.get('vibe_tags', [])
        valid_tags = [tag for tag in tags if tag.lower() in AVAILABLE_VIBE_TAGS]

        return {
            'vibe_tags': valid_tags,
            'reasoning': result.get('reasoning', ''),
            'model': 'gpt-4o',
            'tokens_used': response.usage.total_tokens,
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error classifying vibe tags for {poi_name}: {e}")
        return {
            'vibe_tags': [],
            'reasoning': f'Error: {str(e)}',
            'error': str(e)
        }


def verify_facts_with_checker(poi_name: str, facts: List[str]) -> Dict:
    """
    Use the existing fact-checker to validate generated facts.

    Note: This is a simplified version. In production, you'd want to
    have the fact-checker compare against retrieved source material.

    Args:
        poi_name: Name of the POI
        facts: List of generated facts

    Returns:
        Verification result
    """
    # For now, we'll do a sanity check
    # In full implementation, we'd use src/fact_checker.py with web search results

    prompt = f"""You are fact-checking content for a historical walking tour.

POI: {poi_name}

Generated facts:
{chr(10).join(f'{i+1}. {fact}' for i, fact in enumerate(facts))}

Evaluate these facts for potential issues:
1. Do any facts seem implausible or contain obvious errors?
2. Are dates, numbers, and names specific enough to be verifiable?
3. Are there any red flags that suggest hallucination or speculation?

Rate your confidence that these facts are accurate (0-1 scale).
Flag any specific concerns.

Format as JSON:
{{
  "confidence": 0.X,
  "concerns": ["any concerns, or empty list if none"],
  "recommendation": "approved/review/rejected"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model for validation
            messages=[
                {"role": "system", "content": "You are a fact-checker who identifies potential errors and implausible claims."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return {
            'confidence': result.get('confidence', 0.7),
            'concerns': result.get('concerns', []),
            'recommendation': result.get('recommendation', 'review'),
            'tokens_used': response.usage.total_tokens
        }

    except Exception as e:
        print(f"Error verifying facts for {poi_name}: {e}")
        return {
            'confidence': 0.5,
            'concerns': [f'Verification error: {str(e)}'],
            'recommendation': 'review',
            'error': str(e)
        }


def enrich_poi(poi: Dict, verify: bool = True) -> Dict:
    """
    Fully enrich a POI with facts, visual cues, and vibe tags.

    Args:
        poi: Basic POI dictionary
        verify: Whether to run fact-checking verification

    Returns:
        Enriched POI dictionary
    """
    poi_name = poi.get('name', 'Unknown POI')
    print(f"\n{'='*60}")
    print(f"Enriching: {poi_name}")
    print('='*60)

    # Step 1: Generate facts
    print("1. Generating facts...")
    facts_result = generate_poi_facts(poi)
    facts = facts_result.get('facts', [])
    print(f"   ✓ Generated {len(facts)} facts")

    if not facts:
        print("   ⚠ No facts generated - skipping POI")
        return None

    # Step 2: Generate visual cues
    print("2. Generating visual cues...")
    visual_result = generate_visual_cues(poi)
    visual_cues = visual_result.get('visual_cues', [])
    print(f"   ✓ Generated {len(visual_cues)} visual cues")

    # Step 3: Classify vibe tags
    print("3. Classifying vibe tags...")
    tags_result = classify_vibe_tags(poi, facts)
    vibe_tags = tags_result.get('vibe_tags', [])
    print(f"   ✓ Classified {len(vibe_tags)} vibe tags: {', '.join(vibe_tags)}")

    # Step 4: Verify facts (optional)
    verification = None
    if verify:
        print("4. Verifying facts...")
        verification = verify_facts_with_checker(poi_name, facts)
        print(f"   ✓ Confidence: {verification['confidence']:.2f}")
        if verification['concerns']:
            print(f"   ⚠ Concerns: {', '.join(verification['concerns'])}")

    # Compile enriched POI
    enriched_poi = {
        **poi,  # Keep original data
        'facts': facts,
        'visual_cues': visual_cues,
        'vibe_tags': vibe_tags,
        'source_reliability': facts_result.get('confidence', 0.7),
        'enrichment_metadata': {
            'enriched_at': datetime.now().isoformat(),
            'facts_confidence': facts_result.get('confidence'),
            'facts_source': facts_result.get('source_notes'),
            'verification': verification,
            'total_tokens_used': (
                facts_result.get('tokens_used', 0) +
                visual_result.get('tokens_used', 0) +
                tags_result.get('tokens_used', 0) +
                (verification.get('tokens_used', 0) if verification else 0)
            )
        }
    }

    print(f"\n✓ Enrichment complete!")
    print(f"  Total tokens used: {enriched_poi['enrichment_metadata']['total_tokens_used']}")

    return enriched_poi


# Example usage / testing
if __name__ == "__main__":
    # Test with a sample POI
    test_poi = {
        "id": "test_001",
        "name": "Easby Abbey",
        "geo": {
            "lat": 54.4089,
            "lng": -1.7525
        },
        "tags": {
            "historic": "monastery",
            "ruins": "yes"
        },
        "metadata": {
            "description": "Ruined medieval abbey near Richmond",
            "location": "Richmond, North Yorkshire, England"
        }
    }

    print("="*60)
    print("AUTO-ENRICHMENT TEST")
    print("="*60)

    enriched = enrich_poi(test_poi, verify=True)

    if enriched:
        print("\n" + "="*60)
        print("ENRICHMENT RESULTS")
        print("="*60)
        print(f"\nFacts ({len(enriched['facts'])}):")
        for i, fact in enumerate(enriched['facts'], 1):
            print(f"  {i}. {fact}")

        print(f"\nVisual Cues ({len(enriched['visual_cues'])}):")
        for cue in enriched['visual_cues']:
            print(f"  - {cue}")

        print(f"\nVibe Tags: {', '.join(enriched['vibe_tags'])}")
        print(f"\nSource Reliability: {enriched['source_reliability']:.2f}")

        if enriched['enrichment_metadata'].get('verification'):
            ver = enriched['enrichment_metadata']['verification']
            print(f"\nVerification:")
            print(f"  Confidence: {ver['confidence']:.2f}")
            print(f"  Recommendation: {ver['recommendation']}")
            if ver['concerns']:
                print(f"  Concerns: {', '.join(ver['concerns'])}")

        # Save to file
        output_file = 'output/enriched_poi_test.json'
        os.makedirs('output', exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(enriched, f, indent=2)
        print(f"\n✓ Saved to: {output_file}")
