# Phase 2.5: Auto-Enrichment System

## Overview

The auto-enrichment system uses GPT-4o to automatically generate rich POI data, eliminating hours of manual research. This enables rapid expansion to new locations.

**What it generates:**
- ✅ **Facts** - 2-3 historical/interesting facts per POI
- ✅ **Visual Cues** - 4 navigation landmarks for audio guidance
- ✅ **Vibe Tags** - Automatic classification for preference matching
- ✅ **Fact Verification** - Quality control using GPT-4o-mini

## Setup

### 1. Ensure OpenAI API Key is Configured

```bash
# If you haven't already:
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-...your_actual_key_here
```

Get your API key from: https://platform.openai.com/api-keys

### 2. Test the System

```bash
# Test single POI enrichment
python src/auto_enrich_pois.py
```

This will enrich a sample POI (Easby Abbey) and show you the results.

## Usage

### Option 1: Interactive Mode (Easiest)

```bash
python src/batch_enrich.py --interactive
```

This will:
1. Show you all unenriched POIs in `data/richmond_pois.json`
2. Let you select which to enrich
3. Update the file with enriched data

### Option 2: Batch Processing

```bash
# Enrich all POIs in a file
python src/batch_enrich.py --input data/raw_pois.json --output data/enriched_pois.json
```

Options:
- `--no-verify` - Skip fact verification (faster, less safe)
- `--interactive` - Use interactive mode

### Option 3: Programmatic Use

```python
from src.auto_enrich_pois import enrich_poi

# Your POI data
poi = {
    "id": "york_001",
    "name": "York Minster",
    "geo": {"lat": 53.9619, "lng": -1.0821},
    "tags": {"historic": "cathedral"},
    "metadata": {
        "description": "Gothic cathedral in York",
        "location": "York, England"
    }
}

# Enrich it
enriched = enrich_poi(poi, verify=True)

# Result includes:
# - enriched['facts'] - List of 3 facts
# - enriched['visual_cues'] - List of 4 navigation cues
# - enriched['vibe_tags'] - List of 3-6 categorization tags
# - enriched['source_reliability'] - Confidence score (0-1)
```

## How It Works

### Step 1: Fact Generation (GPT-4o)

**Prompt Engineering:**
- Asks for specific, verifiable facts
- Requests dates, names, and numbers
- Emphasizes historical accuracy
- Temperature: 0.3 (factual mode)

**Example Input:**
```
POI: Easby Abbey
Type: monastery
Location: Richmond, North Yorkshire
```

**Example Output:**
```
1. Easby Abbey was founded in 1152 by Roald, Constable of Richmond Castle,
   for the Premonstratensian order of monks.
2. The abbey church features 13th-century wall paintings that are among the
   finest examples of medieval art in northern England.
3. After the Dissolution of the Monasteries in 1537, much of the abbey stone
   was taken to repair Richmond Castle and local buildings.
```

### Step 2: Visual Cue Extraction (GPT-4o)

**Generates specific, observable features:**

```
- Tall ruined walls of pale stone rising from riverside meadow
- Arched windows without glass in tower structure
- River Swale visible nearby with walking path
- Gothic architectural details in remaining stonework
```

### Step 3: Vibe Tag Classification (GPT-4o)

**Classifies using predefined taxonomy:**

Available tags: history, architecture, ruins, religious, haunted, nature, scenic, etc.

**Selected for Easby Abbey:**
- history
- ruins
- religious
- medieval
- peaceful
- scenic

### Step 4: Fact Verification (GPT-4o-mini)

**Quality control check:**
- Evaluates plausibility
- Flags potential hallucinations
- Rates confidence (0-1)
- Recommends: approved / review / rejected

## Cost Estimates

**Per POI Enrichment:**
- Fact generation: ~1,500 tokens → ~$0.0075
- Visual cues: ~800 tokens → ~$0.004
- Vibe classification: ~600 tokens → ~$0.003
- Verification: ~500 tokens (mini) → ~$0.0003
- **Total: ~$0.015 per POI**

**For 50 POIs:** ~$0.75
**For 100 POIs:** ~$1.50

Compare to manual research: ~15-20 minutes per POI = 25-33 hours for 100 POIs!

## Quality Control

### Built-in Safeguards

1. **Low Temperature** - Uses temperature=0.3 for factual accuracy
2. **Structured Prompts** - Emphasizes verifiable facts only
3. **Confidence Scoring** - Each fact set gets confidence rating
4. **Verification Step** - GPT-4o-mini checks for red flags
5. **Source Notes** - Tracks where information comes from

### Manual Review Recommended For:

- ⚠️ Confidence score < 0.7
- ⚠️ Verification concerns flagged
- ⚠️ Key tourist attractions (high visibility)
- ⚠️ Historical claims with specific dates/names

### Review Workflow

```bash
# Generate enrichment
python src/batch_enrich.py --input data/new_pois.json --output data/enriched_pois.json

# Review output file
# Check 'enrichment_metadata' for each POI:
#   - confidence: Should be > 0.7
#   - verification.concerns: Should be empty
#   - verification.recommendation: Should be "approved"

# Manually verify any flagged POIs
```

## Expanding to New Locations

### Process

**1. Collect Raw POI Data**

```bash
# Use existing data collection script (Phase 0)
python src/data_collection.py --location "York, UK" --radius 2000
```

Or create manually:
```json
{
  "pois": [
    {
      "id": "york_001",
      "name": "York Minster",
      "geo": {"lat": 53.9619, "lng": -1.0821},
      "tags": {"historic": "cathedral"},
      "metadata": {
        "description": "Gothic cathedral",
        "location": "York, England"
      }
    }
  ]
}
```

**2. Auto-Enrich**

```bash
python src/batch_enrich.py \
  --input data/york_raw_pois.json \
  --output data/york_enriched_pois.json
```

**3. Test Routes**

```bash
# Copy enriched file to main data location
cp data/york_enriched_pois.json data/york_pois.json

# Test routing (will work immediately!)
python test_phase2_step2.py
```

**4. Generate Tours**

```bash
# Audio tours work with enriched data
python src/generate_tour_with_verification.py
```

## Example: Richmond Expansion

### Current State
- 15 POIs in dataset
- 10 enriched (manual)
- 5 unenriched

### Expansion Plan

**1. Add More Richmond POIs**

Candidates within 2km:
- Easby Abbey (ruins, 1km east)
- Richmond Station & Museum (railway heritage)
- Hudswell Woods (nature trails)
- Billy Bank Wood (scenic walking)
- Additional riverside paths
- Historic pubs and buildings

**2. Auto-Enrich New POIs**

```bash
# Interactive mode
python src/batch_enrich.py --interactive

# Will enrich only the 5 unenriched + any new ones you add
```

**3. Result**

Expanded from 15 → 40-50 POIs in ~30 minutes:
- Better route variety
- Realistic 60-90 minute tours
- More diverse preferences coverage
- Still focused on Richmond area

## Output Format

### Enriched POI Structure

```json
{
  "id": "richmond_001",
  "name": "Richmond Castle",
  "geo": {"lat": 54.4039, "lng": -1.7394},
  "tags": {"historic": "castle"},
  "metadata": {...},

  "facts": [
    "Richmond Castle was built starting in 1071...",
    "The castle's 100-foot-tall keep is one of...",
    "During World War I, the castle was used as..."
  ],

  "visual_cues": [
    "Massive stone keep rising 100 feet above the town",
    "Thick castle walls made of local limestone",
    "Arched Norman gateway entrance",
    "Towers visible from the market square"
  ],

  "vibe_tags": [
    "history",
    "architecture",
    "military",
    "medieval",
    "dramatic"
  ],

  "source_reliability": 0.9,

  "enrichment_metadata": {
    "enriched_at": "2025-11-15T12:00:00",
    "facts_confidence": 0.85,
    "facts_source": "Historical records and local histories",
    "verification": {
      "confidence": 0.9,
      "concerns": [],
      "recommendation": "approved"
    },
    "total_tokens_used": 3500
  }
}
```

## Troubleshooting

### "OpenAI API key not set"
- Create `.env` file with `OPENAI_API_KEY=sk-...`
- Verify no extra spaces

### "Rate limit exceeded"
- Add delays between POIs: modify `batch_enrich.py` to add `time.sleep(2)`
- Upgrade OpenAI account tier

### "Low confidence scores"
- Normal for obscure POIs with limited historical records
- Manually verify facts for important locations
- Consider adjusting prompts for specific POI types

### "Generic/vague facts"
- Some POIs genuinely have limited information
- Try adding more context in metadata.description
- Consider manual research for key attractions

## Best Practices

### ✅ Do:
- Review verification results before using
- Manually verify key/popular attractions
- Keep source_reliability > 0.7
- Test generated routes to ensure POIs work well
- Spot-check facts against Wikipedia

### ❌ Don't:
- Blindly trust all generated facts without review
- Use for locations requiring 100% accuracy without validation
- Skip verification step for public-facing content
- Ignore low confidence warnings

## Integration with Existing System

The auto-enriched POIs work seamlessly with:
- ✅ Route planning (Phase 2.1)
- ✅ Preference-based scoring (Phase 2.2)
- ✅ Narrative generation (Phase 1.1)
- ✅ Fact-checking (Phase 1.2)
- ✅ Audio generation (Phase 1.3)

No code changes needed - enriched POIs use same schema!

## Next Steps

After enriching your dataset:

1. **Test routes** - Verify new POIs work well in routes
2. **Generate tours** - Create sample audio tours
3. **Gather feedback** - Listen to generated content
4. **Iterate** - Refine prompts if needed
5. **Scale** - Apply to new locations

---

**Ready to expand?** Start with:
```bash
python src/batch_enrich.py --interactive
```

Or read `IMPLEMENTATION_PLAN.md` for Phase 3: RAG & Embeddings.
