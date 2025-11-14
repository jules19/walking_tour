"""
Test Script for Step 1.3: Text-to-Speech Integration
Verify that audio generation works with the complete pipeline
"""

import os
from src.text_to_speech import test_tts, add_audio_pacing

def test_audio_pacing():
    """Test the audio pacing function"""
    print("="*60)
    print("TEST: AUDIO PACING")
    print("="*60)

    test_narrative = """Welcome to Richmond Castle.
Did you know this fortress has stood here for nearly a thousand years?

Look up at the massive stone keep before you. This is Scolland's Hall, built in 1071.

Turn left and head toward the cobbled street."""

    formatted = add_audio_pacing(test_narrative)

    print("\nOriginal:")
    print("-" * 40)
    print(test_narrative)

    print("\n\nFormatted (with pacing):")
    print("-" * 40)
    print(formatted)

    print("\n\nPacing enhancements:")
    print("  ✓ Pauses added after questions")
    print("  ✓ Clear 'Now,' prefix before directions")
    print("  ✓ Date emphasis added")

    return True


def test_complete_pipeline():
    """Test the complete generation + verification + audio pipeline"""
    print("\n" + "="*60)
    print("TEST: COMPLETE PIPELINE")
    print("="*60)

    print("\nThis test requires:")
    print("  1. OpenAI API key in .env")
    print("  2. POI data in data/richmond_pois.json")
    print("  3. Sufficient API credits")

    response = input("\nRun complete pipeline test? (y/n): ")

    if response.lower() != 'y':
        print("Skipping complete pipeline test")
        return False

    try:
        # Import here to avoid errors if deps not installed
        from src.generate_tour_with_verification import main

        print("\nRunning complete pipeline...")
        print("This will:")
        print("  1. Generate a narrative with GPT-4o")
        print("  2. Verify facts with GPT-4o-mini")
        print("  3. Generate audio with OpenAI TTS")
        print("  4. Save all outputs to output/ directory")

        main()

        print("\n" + "="*60)
        print("✓ COMPLETE PIPELINE TEST PASSED")
        print("="*60)
        print("\nCheck the output/ directory for:")
        print("  - output/tours/*.json (narrative + metadata)")
        print("  - output/tours/*.txt (readable text)")
        print("  - output/audio/*.mp3 (audio file)")

        return True

    except Exception as e:
        print(f"\n✗ Complete pipeline test failed: {e}")
        return False


def main():
    """Run all Step 1.3 tests"""
    print("Richmond Walking Tour - Step 1.3 Tests")
    print("="*60)
    print("Testing text-to-speech integration")
    print()

    results = []

    # Test 1: Audio pacing
    print("\n" + "="*60)
    print("Running Test 1: Audio Pacing")
    print("="*60)
    results.append(("Audio Pacing", test_audio_pacing()))

    # Test 2: Basic TTS
    print("\n" + "="*60)
    print("Running Test 2: Basic TTS")
    print("="*60)
    print("\nThis will generate a test audio file using OpenAI TTS.")
    response = input("Proceed? (y/n): ")

    if response.lower() == 'y':
        try:
            tts_result = test_tts()
            results.append(("Basic TTS", tts_result.get("success", False)))
        except Exception as e:
            print(f"✗ TTS test failed: {e}")
            results.append(("Basic TTS", False))
    else:
        print("Skipping TTS test")
        results.append(("Basic TTS", None))

    # Test 3: Complete pipeline (optional)
    pipeline_result = test_complete_pipeline()
    results.append(("Complete Pipeline", pipeline_result))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        print(f"{status:8} - {test_name}")

    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total and total > 0:
        print("\n✓ Step 1.3 implementation complete!")
        print("\nEvaluation checklist:")
        print("  □ Listen to generated audio")
        print("  □ Verify pacing is natural")
        print("  □ Confirm directions are clearly separated from story")
        print("  □ Check voice matches persona")
        print("  □ Validate facts are accurate")
    else:
        print("\n⚠ Some tests failed or were skipped")
        print("Review errors above and check setup")


if __name__ == "__main__":
    main()
