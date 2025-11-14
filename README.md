# Richmond Walking Tour

An AI-generated audio walking tour application that creates personalized, narrative-driven tours based on user location and interests.

## 🎯 Project Vision

Create "vibe-coded" experiences that go beyond factual information to deliver immersive, story-driven explorations of locations. A procedural narrative engine for the real world that generates unique tours each time, tailored to user preferences (history, architecture, food, horror, etc.).

**Starting Location:** Richmond, Northern England (serving as the initial test case)

## ✅ Current Status: Phase 1 Complete!

The project has a working **static tour generator** that produces complete audio tour packages:

- ✅ **Narrative Generation** - GPT-4o creates persona-driven stories following "Beat Sheet" structure
- ✅ **Fact Verification** - GPT-4o-mini validates content (strict about facts, lenient about style)
- ✅ **Audio Production** - OpenAI TTS generates high-quality audio with persona-matched voices
- ✅ **Tour Packages** - Outputs JSON (metadata) + TXT (readable) + MP3 (audio)

### Features

**4 Personas:**
- 🎓 **The Historian** - Scholarly, precise, date-heavy
- 👻 **The Ghost Hunter** - Mysterious, atmospheric, suspenseful
- 🗺️ **The Local** - Friendly, casual, insider knowledge
- ⏳ **The Time Traveler** - Vivid, descriptive, transporting

**Quality Assurance:**
- Double-loop fact-checking prevents hallucinations
- Visual navigation cues for audio-only wayfinding
- Intelligent audio pacing separates story from directions

**Cost:** ~$0.04-0.06 per complete tour (narrative + verification + audio)

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install openai python-dotenv

# Configure OpenAI API key
cp .env.example .env
# Edit .env and add your API key
```

### Generate a Tour

```bash
# Complete pipeline (narrative + verification + audio)
python src/generate_tour_with_verification.py
```

This creates:
- `output/tours/*.json` - Full metadata
- `output/tours/*.txt` - Readable narrative
- `output/audio/*.mp3` - Audio file (2-4 minutes)

### Test Individual Components

```bash
# Test fact-checker
python src/fact_checker.py

# Test text-to-speech
python src/text_to_speech.py

# Test complete Step 1.3
python test_step_1_3.py
```

## 📚 Documentation

- **[PHASE1_README.md](PHASE1_README.md)** - Complete Phase 1 guide (setup, usage, evaluation)
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Full roadmap and architecture
- **[CLAUDE.md](CLAUDE.md)** - Project overview and technical principles
- **[Walking_tour_outline.md](Walking_tour_outline.md)** - Original vision and architectural blueprints

## 🗺️ Roadmap

### ✅ Phase 1: Static Tour Generator (Complete)
- Step 1.1: Narrative generation with GPT-4o
- Step 1.2: Fact-checking rail with GPT-4o-mini
- Step 1.3: Text-to-speech with OpenAI TTS

### 🔜 Phase 2: Route Intelligence (Next)
- Step 2.1: Route planning with walkability constraints
- Step 2.2: POI scoring based on user preferences
- Deliverable: Automatic route generation

### 📋 Phase 3: RAG & Embeddings
- Step 3.1: Create embeddings for semantic search
- Step 3.2: Replace keyword matching with vector similarity
- Step 3.3: Context-aware narrative generation

### 🎧 Phase 4: Location-Aware Prototype
- Step 4.1: CLI interface for tour generation
- Step 4.2: GPS-triggered audio playback
- Step 4.3: Off-path detection and recovery

### 🌐 Phase 5: Web Interface
- Step 5.1: FastAPI backend
- Step 5.2: PWA frontend for mobile

## 🏗️ Architecture

The system uses a **RAG (Retrieval-Augmented Generation)** approach:

1. **Knowledge Layer** - POI database with facts, visual cues, and vibe tags
2. **Context Layer** - User interests, time available, GPS location
3. **Orchestrator** - AI agent that retrieves, generates, and verifies narratives
4. **Presentation Layer** - High-quality TTS with persona matching

**Critical Safety Principle:** Navigation instructions come from a deterministic routing engine, NOT the LLM. The LLM only stylizes pre-determined directions to prevent dangerous hallucinated navigation.

## 💰 Cost Estimates

- **Generation (GPT-4o)**: ~$0.01 per tour
- **Verification (GPT-4o-mini)**: ~$0.005 per tour
- **Audio (TTS)**: ~$0.02-0.04 per tour
- **Total**: ~$0.04-0.06 per complete tour

Pre-generate and cache popular "Base Tours" to reduce per-user costs at scale.

## 🧪 Key Data

- **POIs**: 10 curated locations in Richmond with enriched facts
- **Route**: 3 POIs per test tour
- **Audio Duration**: ~2-4 minutes per tour
- **Fact-Check Confidence**: 0.9+ threshold for approval

## 🤝 Contributing

This is a learning project focused on building a procedural narrative engine. See `IMPLEMENTATION_PLAN.md` for the complete technical roadmap and evaluation criteria.

## 📄 License

This project is for educational and experimental purposes.
