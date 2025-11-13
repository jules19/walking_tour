# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-generated audio walking tour application that creates personalized, narrative-driven tours based on user location and interests. The goal is to deliver "vibe-coded" experiences that go beyond factual information to create immersive, story-driven explorations of locations.

**Core Concept:** A procedural narrative engine for the real world that generates unique tours each time, tailored to user preferences (history, architecture, food, horror, etc.).

**Starting Location:** Richmond, Northern England (serving as the initial sandbox/test case).

## Project Status

Currently in planning phase. No code implementation yet. The project has detailed architectural blueprints and vision documents (see `Walking_tour_outline.md`).

## Architecture

### System Overview: The "Story Engine"

The application uses a **RAG (Retrieval-Augmented Generation)** approach rather than static audio files, consisting of four main layers:

#### 1. Knowledge Layer (Database)
- **Structure:** Knowledge graph with nodes (locations, people, events) and edges (relationships)
- **Attributes:** Each node has tags for "vibe" categorization (Gory, Romantic, Architectural, etc.)
- **Data Sources:** OpenStreetMap (OSM), Wikidata/Wikipedia, Google Places/Foursquare
- **Content Pipeline:**
  - Geo-hashing for data chunking
  - Deduplication (merge POIs within 15m with fuzzy name match > 0.8)
  - Visual cue extraction using Vision LLM on Street View images (critical for audio-only navigation)

#### 2. Context Layer (User Input)
- **Static:** User interests, time available
- **Dynamic:** GPS location, time of day, weather (affects recommendations)

#### 3. Orchestrator (AI Agent)
- **Query Process:**
  1. Retrieve relevant nodes based on user context and preferences
  2. LLM weaves facts into narrative script following "Beat Sheet" structure
  3. Fact-checking rail validates against source material
- **Scoring Formula:** `S_poi = α(U·P) + β(Pop) + γ(Nov) - δ(Dist)`
  - U: User Interest Vector
  - P: POI Embedding Vector
  - Pop: Popularity Score
  - Nov: Novelty Score
  - Dist: Distance penalty

#### 4. Presentation Layer (Audio Experience)
- High-quality TTS (Text-to-Speech) with persona matching
- Audio cues to separate directions from stories
- Sound effects for immersion

### Narrative Structure ("Beat Sheet")

Each POI segment follows this pattern:
1. **The Hook:** Provocative question/statement
2. **The Visual Anchor:** "Look at the [Visual Cue]..."
3. **The Meat:** Historical/cultural story tailored to persona
4. **The Synthesis:** Connection to user's interest
5. **Call-to-Move:** Clear directional instruction

### Critical Safety Principle

**Navigation instructions come from the deterministic Routing Engine, NOT the LLM.** The LLM only stylizes pre-determined directions to prevent hallucinated navigation that could be unsafe (e.g., "cross the bridge" when no bridge exists).

## Recommended Technology Stack

- **Backend:** Python with FastAPI (serverless on AWS Lambda)
- **Vector DB:** Qdrant or pgvector (hybrid search capability)
- **Routing:** Valhalla (pedestrian-specific) or Mapbox Direction API (easier MVP)
- **LLM:** GPT-4o (generation) + GPT-4o-mini (validation/classification)
- **TTS:** ElevenLabs (premium quality) or OpenAI TTS (cost-effective)
- **Client:** Progressive Web App (PWA) for mobile
- **Graph Processing:** NetworkX (Python) or similar

## Development Phases

### Phase 1: "Wizard of Oz" Prototype
- Manually curate 50 facts about Richmond
- Test narrative generation with ChatGPT manually
- Validate directional cues and story quality through self-testing

### Phase 2: "Generator" MVP (Backend Logic)
- Build Python script with vector database
- Automate script generation from curated data
- Verify narrative cohesion vs. disjointed facts

### Phase 3: Audio-First App (MVP 0.1)
- Simple mobile web app with location access
- User selects "vibe" preference
- Generate and stream audio on-the-fly
- Cache popular tours to reduce compute costs

### Phase 4: Immersive Layer (Scale)
- Dynamic content based on GPS dwell time
- Background soundscapes and era-specific audio
- Adaptive learning from user behavior

## Key Data Structures

### POI Schema
```json
{
  "id": "UUID",
  "geo": {"lat": 0.0, "lng": 0.0, "altitude": 0.0},
  "visual_cues": ["red awning", "stone lion statue"],
  "metadata": {"name": "", "year_built": "", "architect": ""},
  "content_vector": [],
  "tags": ["history", "murder_mystery"],
  "source_reliability": 0.9
}
```

### Route Graph
- **Nodes:** POIs and intersections
- **Edges:** Walkable paths weighted by scenic value, safety, and incline
- **Filters:** Prioritize pedestrian/footway, exclude highways, consider lighting for night tours

## Vibe Categories & Tone

| Category | Data Focus | Voice Tone |
|----------|-----------|------------|
| The Architect | Building materials, styles, architects | Precise, appreciative, slow |
| The Ghost Hunter | Executions, murders, folklore | Whispered, suspenseful, immersive |
| The Local | Best spots, hidden alleys, local slang | Friendly, casual, slang-heavy |
| The Time Traveler | Historical dates, sensory details | Descriptive, narrative, transportive |

## Critical Implementation Notes

### Fact-Checking (Double-Loop Verification)
1. LLM generates draft story
2. Verifier LLM compares draft against source truth snippets
3. If confidence < 0.9, use safe template or flag for human review
4. Output JSON: `{pass: bool, hallucinations: []}`

### Audio Optimization
- Use SSML tags: `<break time="1s"/>` between thoughts, `<prosody rate="slow">` for complex dates
- Cache common TTS segments ("Turn left in 50 meters")
- Download full route audio at start to minimize streaming
- Use ffmpeg for background ambience mixing

### Privacy & Security
- GPS coordinates are ephemeral (processed for tour generation, then discarded)
- Store only Region/City for analytics
- User ID is random hash with no PII linkage
- Run OpenAI Moderation Endpoint on generated content
- Blocklist sensitive POIs (private residences, recent crime scenes)

## Testing Protocols

### The "Gore" Test
Prompt with extreme preferences (e.g., "serial killers") and ensure output remains documentary/historical, not celebratory or graphic.

### The "Ghost" Test
Simulate GPS drift (±20m noise). System should gracefully recover with fallback: "I think you might be off path, head back to..."

### Dry-Run Script
Python script simulates user movement along coordinates and outputs LLM responses to console for validation before field testing.

## Metrics to Track

- **Completion Rate:** % of route actually walked
- **GPS Deviation:** Frequency of path departure (indicates poor navigation)
- **Implicit Feedback:** Pause/rewind rates (confusion/interest) vs skip rates (boredom)
- **Factual Error Reports:** User-submitted corrections

## Cost Estimates (MVP)

Approximately $0.05-$0.15 per generated tour (primarily LLM + TTS costs). Pre-generate popular "Base Tours" and cache aggressively to reduce per-user costs.

## References

- Detailed vision and architectural blueprints: `Walking_tour_outline.md`
- Original project concept: `README.md`
