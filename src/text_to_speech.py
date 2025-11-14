"""
Step 1.3: Text-to-Speech Generation
Convert verified narratives into audio files using OpenAI TTS
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Map personas to OpenAI TTS voices
PERSONA_VOICES = {
    "historian": "onyx",      # Deep, authoritative male voice
    "ghost_hunter": "fable",  # British, mysterious quality
    "local": "nova",          # Warm, friendly female voice
    "time_traveler": "echo"   # Smooth, descriptive male voice
}


def add_audio_pacing(narrative: str) -> str:
    """
    Add pauses and pacing cues to narrative text.
    OpenAI TTS doesn't support SSML, but responds to punctuation and formatting.

    Key features:
    - Separates story content from navigation with clear pauses
    - Adds emphasis to directional instructions for safety
    - Creates natural breathing room in the narrative

    Args:
        narrative: Raw narrative text

    Returns:
        Formatted narrative with enhanced pacing
    """
    formatted = narrative

    # Add longer pauses between POI sections (major story breaks)
    # Double newlines indicate POI transitions
    formatted = formatted.replace("\n\n", "...\n\n")

    # Add clear separation before navigation instructions
    # This is critical for safety - directions need to be distinct from story
    direction_starters = [
        "Turn left",
        "Turn right",
        "Head toward",
        "Head to",
        "Walk toward",
        "Walk to",
        "Continue along",
        "Continue down",
        "Cross the street",
        "Cross over to",
        "Follow the path",
        "Take the path"
    ]

    for marker in direction_starters:
        # Add pause and emphasis before directions
        formatted = formatted.replace(f" {marker}", f"... Now, {marker}")
        formatted = formatted.replace(f"\n{marker}", f"\n\n... Now, {marker}")
        # Avoid double "Now" if it's already there
        formatted = formatted.replace(f"... Now, Now, {marker}", f"... Now, {marker}")

    # Add brief pauses after transition phrases for natural pacing
    transitions = [
        "Imagine",
        "Picture this",
        "Back then",
        "In those days",
        "At that time",
        "During this period",
        "Years later",
        "But here's the thing"
    ]

    for transition in transitions:
        formatted = formatted.replace(f"{transition},", f"{transition}...")

    # Add breathing room after questions (common in hooks)
    formatted = formatted.replace("?", "?...")
    # But avoid triple ellipsis
    formatted = formatted.replace("?......", "?...")

    # Slow down numbers and dates for clarity
    # Add slight pause before dates in format "in YEAR"
    import re
    formatted = re.sub(r'in (\d{4})', r'in... \1', formatted)
    formatted = re.sub(r'built in... (\d{4})', r'built in \1', formatted)  # Fix overcorrection

    return formatted


def generate_audio(
    narrative: str,
    persona_key: str,
    output_filename: str,
    model: str = "tts-1",
    speed: float = 1.0,
    output_dir: str = "output/audio"
) -> Dict[str, Any]:
    """
    Generate audio file from narrative text using OpenAI TTS.

    Args:
        narrative: The narrative text to convert to speech
        persona_key: Persona identifier (historian, ghost_hunter, etc.)
        output_filename: Name for the output file (without extension)
        model: TTS model to use ("tts-1" or "tts-1-hd")
        speed: Playback speed (0.25 to 4.0, default 1.0)
        output_dir: Directory to save audio files

    Returns:
        Dict with audio generation metadata
    """
    print(f"\nGenerating audio with {PERSONA_VOICES[persona_key]} voice...")
    print("-" * 60)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Add pacing to narrative
    formatted_narrative = add_audio_pacing(narrative)

    # Select voice based on persona
    voice = PERSONA_VOICES.get(persona_key, "alloy")

    # Calculate approximate duration (rough estimate: 150 words per minute)
    word_count = len(formatted_narrative.split())
    estimated_duration_mins = word_count / 150

    print(f"  Voice: {voice}")
    print(f"  Model: {model}")
    print(f"  Word count: {word_count}")
    print(f"  Estimated duration: {estimated_duration_mins:.1f} minutes")

    try:
        # Generate speech
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=formatted_narrative,
            speed=speed
        )

        # Save to file
        output_path = Path(output_dir) / f"{output_filename}.mp3"
        response.stream_to_file(output_path)

        # Get file size
        file_size_kb = os.path.getsize(output_path) / 1024

        print(f"✓ Audio generated successfully")
        print(f"  File: {output_path}")
        print(f"  Size: {file_size_kb:.1f} KB")

        return {
            "success": True,
            "file_path": str(output_path),
            "file_size_kb": file_size_kb,
            "voice": voice,
            "model": model,
            "word_count": word_count,
            "estimated_duration_mins": estimated_duration_mins,
            "speed": speed
        }

    except Exception as e:
        print(f"✗ Audio generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "voice": voice,
            "model": model
        }


def test_tts():
    """
    Test the TTS module with a sample narrative
    """
    print("="*60)
    print("TEXT-TO-SPEECH TEST")
    print("="*60)

    # Sample narrative
    test_narrative = """Welcome to Richmond Castle, one of England's finest medieval fortresses.

Look up at the massive stone keep rising before you. This is Scolland's Hall, standing 100 feet tall, one of the oldest stone keeps in Britain.

This castle was built starting in 1071 by Alan Rufus, a Breton nobleman who had fought alongside William the Conqueror at the Battle of Hastings just five years earlier.

During World War I, these ancient walls served a darker purpose—as a prison for conscientious objectors, men who refused to fight.

Now, turn left and head toward the cobbled street. We're walking to Greyfriars Tower, about 200 meters ahead."""

    # Test with historian voice
    print("\nGenerating test audio with Historian persona...")

    result = generate_audio(
        narrative=test_narrative,
        persona_key="historian",
        output_filename="test_historian_tts",
        model="tts-1",
        speed=0.95  # Slightly slower for clarity
    )

    if result["success"]:
        print("\n" + "="*60)
        print("✓ TTS TEST PASSED")
        print("="*60)
        print(f"Listen to the audio file at: {result['file_path']}")
        print("\nEvaluation checklist:")
        print("  - Is the pacing natural?")
        print("  - Can you understand the directions clearly?")
        print("  - Are pauses between sections appropriate?")
        print("  - Does the voice match the historian persona?")
    else:
        print("\n" + "="*60)
        print("✗ TTS TEST FAILED")
        print("="*60)
        print(f"Error: {result.get('error')}")

    return result


if __name__ == "__main__":
    test_tts()
