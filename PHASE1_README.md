# Phase 1: Static Tour Generator

## What We've Built

Phase 1 creates AI-generated tour narratives using GPT-4o with different personas.

### Files Created

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

### Generate Test Tours

Run the default test (Castle → Greyfriars → Market Place with 3 personas):

```bash
python src/generate_tour.py
```

This will:
1. Generate narratives for Historian, Ghost Hunter, and Local personas
2. Save outputs to `output/tours/`
3. Create both JSON (full data) and TXT (readable narrative) files
4. Display token usage and preview

### Output Files

Generated files in `output/tours/`:
- `tour_historian_YYYYMMDD_HHMMSS.json` - Full generation data
- `tour_historian_YYYYMMDD_HHMMSS.txt` - Readable narrative text
- (same for ghost_hunter and local personas)

### Example Output Structure

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

## Evaluation Criteria (Step 1.1)

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

## Cost Estimates

- **Per narrative**: ~1,500-2,000 tokens total
  - Prompt: ~1,000 tokens
  - Completion: ~500-1,000 tokens
- **Cost**: ~$0.01-0.02 per narrative (GPT-4o pricing)
- **Test run (3 personas)**: ~$0.03-0.06

## Next Steps

After generating and reviewing narratives:

- **Step 1.2**: Add fact-checking rail to detect hallucinations
- **Step 1.3**: Integrate text-to-speech to generate audio
- **Phase 2**: Add route planning and POI scoring

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
