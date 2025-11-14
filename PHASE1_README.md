# Phase 1: Static Tour Generator

## What We've Built

Phase 1 creates AI-generated tour narratives using GPT-4o with different personas, and verifies them for factual accuracy.

### Files Created

**Step 1.1: Narrative Generation**

1. **`src/generate_tour.py`** - Main narrative generation script
   - Connects 3 POIs into a coherent tour story
   - Supports 4 personas: Historian, Ghost Hunter, Local, Time Traveler
   - Follows "Beat Sheet" structure (Hook → Visual Anchor → Story → Synthesis → Directions)
   - Uses GPT-4o with temperature=0.7 for creative but consistent output

2. **`setup_check.py`** - Setup verification tool
   - Checks dependencies are installed
   - Verifies .env file and API key configuration
   - Validates POI data is enriched

3. **`.gitignore`** - Prevents committing sensitive files

**Step 1.2: Fact-Checking**

4. **`src/fact_checker.py`** - Fact verification module
   - Uses GPT-4o-mini to verify narratives against source facts
   - Detects hallucinations (claims not supported by sources)
   - Returns confidence scores and specific issues found
   - Tests with both good and bad narratives
   - Distinguishes factual errors from narrative style

**Step 1.3: Text-to-Speech (NEW)**

5. **`src/text_to_speech.py`** - Audio generation module
   - Converts narratives to speech using OpenAI TTS API
   - Maps personas to appropriate voices (historian → onyx, ghost_hunter → fable, etc.)
   - Adds intelligent pacing with pauses and emphasis
   - Separates story content from navigation instructions for safety
   - Estimates audio duration and file size

6. **`src/generate_tour_with_verification.py`** - Complete integrated pipeline
   - Generates narrative with GPT-4o
   - Verifies facts with GPT-4o-mini
   - Generates audio with OpenAI TTS
   - Marks tours as: approved / review needed / rejected
   - Tracks total costs and token usage
   - Outputs JSON (data), TXT (readable), and MP3 (audio)

### Persona Types

| Persona | Description | Tone |
|---------|-------------|------|
| **The Historian** | Scholarly, precise, appreciative | Formal, date-heavy, causal relationships |
| **The Ghost Hunter** | Mysterious, atmospheric, dark | Whispered, suspenseful, macabre |
| **The Local** | Friendly insider, hidden gems | Casual, conversational, slang |
| **The Time Traveler** | Vivid era descriptions | Descriptive, narrative, sensory-rich |

## Setup Instructions

### 1. Install Dependencies

Already completed! ✓

```bash
pip install openai python-dotenv
```

### 2. Configure OpenAI API Key

**You need to add your OpenAI API key:**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and replace with your actual API key
# OPENAI_API_KEY=sk-proj-...your_actual_key_here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Verify Setup

```bash
python setup_check.py
```

You should see:
```
✓ Setup complete! Ready to generate tours.
```

## Running the Generator

### Step 1.1: Generate Basic Tours

Run the default test (Castle → Greyfriars → Market Place with 3 personas):

```bash
python src/generate_tour.py
```

This will:
1. Generate narratives for Historian, Ghost Hunter, and Local personas
2. Save outputs to `output/tours/`
3. Create both JSON (full data) and TXT (readable narrative) files
4. Display token usage and preview

### Step 1.2: Generate with Fact-Checking (Recommended)

Run the integrated pipeline with verification:

```bash
python src/generate_tour_with_verification.py
```

This will:
1. Generate narrative with GPT-4o
2. Verify facts with GPT-4o-mini
3. Mark tour as approved/review/rejected based on verification
4. Save results with verification metadata
5. Display any hallucinations detected

### Step 1.3: Generate with Audio (Complete Pipeline)

The verification script now includes audio generation by default:

```bash
python src/generate_tour_with_verification.py
```

This complete pipeline will:
1. Generate narrative with GPT-4o (persona-driven storytelling)
2. Verify facts with GPT-4o-mini (catch hallucinations)
3. **Generate audio with OpenAI TTS** (persona-matched voice)
4. Save all outputs: JSON, TXT, and MP3 files
5. Display verification results and audio metadata

### Test Individual Modules

Test the fact-checking module independently:

```bash
python src/fact_checker.py
```

This runs two tests:
- **Test 1**: Good narrative (only uses provided facts) → should PASS
- **Test 2**: Bad narrative (contains hallucinations) → should FAIL

Test the text-to-speech module independently:

```bash
python src/text_to_speech.py
```

This generates a test audio file with:
- Sample Richmond Castle narrative
- Historian voice (onyx)
- Enhanced pacing and pauses

Test the complete Step 1.3 implementation:

```bash
python test_step_1_3.py
```

This interactive test verifies:
- Audio pacing enhancements
- TTS generation
- Complete pipeline (optional)

### Output Files

Generated files in `output/tours/`:
- `tour_historian_YYYYMMDD_HHMMSS.json` - Full generation data + metadata
- `tour_historian_YYYYMMDD_HHMMSS.txt` - Readable narrative text
- (same for ghost_hunter, local, and time_traveler personas)

Generated files in `output/audio/`:
- `tour_historian_YYYYMMDD_HHMMSS.mp3` - Audio file with persona-matched voice
- Duration: ~2-4 minutes for 3-POI tour
- Format: MP3, optimized for mobile playback

### Example Output Structure

**Basic output (Step 1.1):**
```json
{
  "persona": "historian",
  "pois": [...],
  "narrative": "Welcome to Richmond Castle...",
  "model": "gpt-4o",
  "temperature": 0.7,
  "tokens_used": 1234,
  "generated_at": "2025-11-13T12:00:00"
}
```

**Verified output with audio (Step 1.3):**
```json
{
  "persona": "historian",
  "pois": [...],
  "narrative": "Welcome to Richmond Castle...",
  "verification": {
    "pass": true,
    "confidence": 0.95,
    "hallucinations": [],
    "warnings": []
  },
  "audio": {
    "success": true,
    "file_path": "output/audio/tour_historian_20251114_120000.mp3",
    "file_size_kb": 524.3,
    "voice": "onyx",
    "model": "tts-1",
    "estimated_duration_mins": 3.2
  },
  "status": "approved",
  "passed_verification": true,
  "generated_at": "2025-11-13T12:00:00"
}
```

## Fact-Checking System (Step 1.2)

### How It Works

The fact-checking rail uses a **double-loop verification** process:

1. **Generation (GPT-4o)**: Creates the narrative from POI facts
2. **Verification (GPT-4o-mini)**: Checks narrative against source facts

The verifier applies **"strict about facts, lenient about style"**:

**Flags as hallucinations (real problems):**
- Wrong dates, numbers, measurements
- Non-existent people, buildings, events
- False attributions
- Invented physical features
- Contradictions of source facts

**Allows (acceptable narrative):**
- Poetic/metaphorical language ("stones whisper tales")
- Sensory descriptions ("weathered grey walls")
- Reasonable historical interpretations
- Atmospheric framing ("complex tapestry of history")
- Minor date conversions ("1071" vs "eleventh century")
- Navigation cues ("turn left at...")

### Verification Results

Tours are classified as:

- **✓ Approved**: Pass = true, Confidence ≥ 0.9
  - No hallucinations detected
  - High confidence in verification
  - Safe to use

- **⚠ Review Needed**: Pass = true, Confidence < 0.9
  - Technically passed but borderline
  - Manual review recommended
  - May have warnings

- **✗ Rejected**: Pass = false
  - Hallucinations detected
  - Should not be used
  - Lists specific problematic claims

### Example Hallucinations

The fact-checker catches claims like:

**Bad**: "King Henry VIII visited this castle three times"
- **Reason**: Not mentioned in source facts

**Bad**: "The castle was originally built with wood"
- **Reason**: Source says it started in 1071 as stone (one of oldest stone castles)

**OK**: "In the eleventh century, Alan Rufus began construction"
- **Reason**: Rephrasing of "built starting in 1071"

### Confidence Threshold

Default threshold: **0.9** (90% confidence)

- Higher threshold (0.95) = More strict, fewer false positives
- Lower threshold (0.85) = More lenient, may allow borderline claims

Adjust based on your risk tolerance for factual errors.

## Evaluation Criteria

When you review the generated narratives, check:

1. **Persona Distinctiveness**: Does each persona sound different?
   - Historian: Formal and fact-heavy?
   - Ghost Hunter: Atmospheric and mysterious?
   - Local: Casual and friendly?

2. **Narrative Coherence**: Do the stories flow naturally between POIs?

3. **Factual Accuracy**: Are only the provided facts used? (No hallucinations?)

4. **Visual Navigation**: Are directions clear with visual cues?

5. **Beat Sheet Structure**: Does each POI follow the pattern?
   - Hook → Visual Anchor → Story → Synthesis → Directions

## Text-to-Speech System (Step 1.3)

### How It Works

Audio generation uses OpenAI TTS API with intelligent pacing:

1. **Voice Selection**: Personas mapped to appropriate voices
   - Historian → onyx (deep, authoritative male)
   - Ghost Hunter → fable (British, mysterious)
   - Local → nova (warm, friendly female)
   - Time Traveler → echo (smooth, descriptive male)

2. **Audio Pacing**: Automated enhancements for natural listening
   - Pauses between POI sections (`...`)
   - Clear "Now," prefix before navigation (safety-critical)
   - Breathing room after questions
   - Emphasis on dates and numbers

3. **Output**: MP3 file optimized for mobile playback
   - Quality: `tts-1` (cost-effective, sufficient quality)
   - Speed: 0.95x (slightly slower for clarity)
   - Duration: ~2-4 minutes for typical 3-POI tour

### Evaluation Checklist

Listen to generated audio and check:
- ✓ Is pacing natural and comfortable?
- ✓ Can you understand directions clearly?
- ✓ Are navigation instructions distinct from story?
- ✓ Does the voice match the persona?
- ✓ Are pauses between sections appropriate?

## Cost Estimates

### Step 1.1: Generation Only

- **Per narrative**: ~1,500-2,000 tokens total
- **Cost**: ~$0.01-0.02 per narrative (GPT-4o pricing)
- **Test run (3 personas)**: ~$0.03-0.06

### Step 1.2: Generation + Verification

- **Generation (GPT-4o)**: ~1,500-2,000 tokens
- **Verification (GPT-4o-mini)**: ~1,200-1,500 tokens
- **Total tokens**: ~2,700-3,500 per verified tour
- **Cost**: ~$0.015-0.025 per verified tour
- **Test run (1 persona)**: ~$0.02

### Step 1.3: Complete Pipeline (Generation + Verification + Audio)

- **Generation (GPT-4o)**: ~1,500-2,000 tokens (~$0.01)
- **Verification (GPT-4o-mini)**: ~1,200-1,500 tokens (~$0.005)
- **Audio (TTS)**: Variable by length (~$0.02-0.04 for 3-POI tour)
- **Total cost**: ~$0.04-0.06 per complete tour with audio
- **Test run (1 persona)**: ~$0.05

TTS pricing is based on character count. A typical 3-POI narrative (~500-800 words) costs $0.02-0.04 for audio generation.

## Next Steps

**Phase 1 is complete!** ✓

You now have a working static tour generator that:
- ✓ Generates persona-driven narratives (GPT-4o)
- ✓ Verifies factual accuracy (GPT-4o-mini)
- ✓ Produces high-quality audio (OpenAI TTS)
- ✓ Outputs tour packages (JSON + TXT + MP3)

**What's Next:**

- **Phase 2**: Route Intelligence
  - Step 2.1: Implement route planning with walkability constraints
  - Step 2.2: Add POI scoring based on user preferences
  - Deliverable: `route_planner.py` that generates optimal routes

See `IMPLEMENTATION_PLAN.md` for the complete roadmap.

## Troubleshooting

**"OpenAI API key not set"**
- Make sure you created `.env` file (not `.env.example`)
- Check that your API key starts with `sk-`
- Verify no extra spaces around the key in .env

**"Rate limit exceeded"**
- You've hit OpenAI API limits
- Wait a minute and try again
- Consider upgrading your OpenAI account tier

**"Insufficient quota"**
- You need to add credits to your OpenAI account
- Visit https://platform.openai.com/settings/organization/billing

## Architecture Notes

The generation follows this flow:

1. **Load POI data** from `richmond_pois.json`
2. **Select POIs** to connect (currently 3 POIs for testing)
3. **Build prompts** with:
   - System prompt: Defines persona and rules
   - User prompt: Provides POI facts and instructions
4. **Generate** using GPT-4o
5. **Save** results in JSON and TXT formats

The prompts enforce strict rules:
- Use ONLY provided facts (no invention)
- Follow Beat Sheet structure
- Maintain persona voice
- Reference visual cues for navigation
