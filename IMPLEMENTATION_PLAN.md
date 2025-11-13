# Implementation Plan: Richmond Walking Tour

**Project Type:** Learning project focused on Richmond, North Yorkshire
**Approach:** Small testable steps with evaluations at each stage
**Timeline:** ~7 weeks for full MVP

---

## Phase 0: Foundation (Week 1)

### Goal
Get basic data and validate Richmond has enough content

### Step 0.1: Data Collection Script
**Task:** Build a Python script that queries OpenStreetMap Overpass API for Richmond, North Yorkshire
- Extract POIs with tags: `historic`, `tourism`, `amenity`
- Save to JSON file

**Eval:** You should get 50+ POIs. If <30, Richmond might be too sparse.

**Deliverable:** `richmond_pois.json` with raw POI data

### Step 0.2: Manual Enrichment
**Task:** Curate initial dataset
- Pick 10 most interesting POIs from the data
- Manually research and write 2-3 facts per POI from Wikipedia/local history sites
- Add visual cues by looking at Google Street View

**Eval:** Can you write engaging facts? Are visual cues clear enough for navigation?

**Deliverable:** `richmond_pois.json` with 10 enriched POIs

---

## Phase 1: Static Tour Generator (Week 2)

### Goal
Generate a single coherent tour narrative (no location awareness yet)

### Step 1.1: Simple Prompt Chain
**Task:** Build basic narrative generation
- Write a Python script that takes 3 POIs as input
- Use GPT-4o to generate a narrative connecting them
- Prompt template: "You are a [PERSONA] tour guide. Create a walking tour script connecting these locations: [POI data]"

**Eval:** Run with different personas (Historian, Ghost Hunter, Local). Is the output coherent? Does it have personality?

### Step 1.2: Fact-Checking Rail
**Task:** Add verification layer
- Add a verification step: send generated script + source facts to GPT-4o-mini
- Ask: "List any claims in the script not supported by the source material"

**Eval:** Intentionally add a fake fact to source data. Does the verifier catch it?

### Step 1.3: Text-to-Speech
**Task:** Generate audio output
- Integrate OpenAI TTS (cheaper for learning)
- Generate audio file from script
- Add SSML tags for pauses between POIs

**Eval:** Listen to it. Is pacing good? Can you understand directions?

**Deliverable:** `generate_tour.py` that outputs both `script.txt` and `tour.mp3`

---

## Phase 2: Route Intelligence (Week 3)

### Goal
Automatically choose and order POIs based on location

### Step 2.1: Basic Routing
**Task:** Implement route planning
- Use a simple routing library (OSRM Python wrapper or straight-line distance for MVP)
- Given: starting point, 5 candidate POIs, 30-minute time budget
- Output: ordered route that's walkable

**Eval:** Plot the route on a map (use folium library). Does it make sense? Any weird backtracking?

### Step 2.2: POI Scoring
**Task:** Implement relevance scoring
- Implement the scoring formula: `S_poi = α(interest_match) + β(popularity) - δ(distance)`
- For MVP: interest_match = simple keyword match (e.g., "historic" tags match "History" preference)

**Eval:** Generate routes with different preferences. Do "Horror" tours actually pick the castle over the tea shop?

**Deliverable:** `route_planner.py` that takes user preferences and generates optimal route

---

## Phase 3: Embeddings & RAG (Week 4)

### Goal
Use vector similarity instead of keyword matching

### Step 3.1: Create Embeddings
**Task:** Build embedding system
- Embed all POI descriptions using OpenAI text-embedding-3-small
- Store in a simple vector store (start with numpy arrays, no database needed for 10 POIs)

**Eval:** Query with "spooky stories" and "medieval architecture". Do you get different top results?

### Step 3.2: Semantic Retrieval
**Task:** Replace keyword matching with semantic search
- Replace keyword scoring with cosine similarity between user preference embedding and POI embeddings

**Eval:** Compare results to keyword approach. Is it actually better or just more complex?

### Step 3.3: Add Context to Generation
**Task:** Integrate RAG into narrative generation
- When generating narrative, retrieve relevant facts using RAG
- Instead of passing all facts, only pass top-3 most relevant per POI

**Eval:** Does this produce more focused narratives? Or do you lose important context?

**Deliverable:** `embedding_store.py` and updated generator using RAG

---

## Phase 4: Location-Aware Prototype (Week 5)

### Goal
Build a minimal working app you can actually use while walking

### Step 4.1: CLI Interface
**Task:** Create command-line tour generator
- Build a command-line tool: `python tour.py --start "Richmond Castle" --vibe "horror" --duration 30`
- Generates tour package: audio files + a simple JSON manifest with GPS trigger points

**Eval:** Generate a tour, walk it yourself with your phone. Do the transitions work? Can you follow directions?

### Step 4.2: GPS Trigger Logic
**Task:** Implement location-based audio playback
- Simple Python script that reads your phone's GPS (or simulate with a GPS trace file)
- When you enter a 25m radius of a POI, play the corresponding audio segment

**Eval:** Test with GPS simulation first. Then do a real field test. What breaks?

### Step 4.3: Recovery Handling
**Task:** Add off-path detection
- Add logic for "off-path" detection
- If user deviates >50m from route, play fallback audio: "Head back toward [landmark]"

**Eval:** Intentionally go off route. Is the recovery clear?

**Deliverable:** Working Python CLI app you can use on a smartphone (via Termux or similar)

---

## Phase 5: Web Interface (Week 6-7)

### Goal
Make it accessible without command line

### Step 5.1: FastAPI Backend
**Task:** Create REST API
- Create API endpoints:
  - `POST /generate-tour` (takes preferences, returns tour_id)
  - `GET /tour/{tour_id}` (returns manifest + audio URLs)
- Store generated tours in simple file system (no database yet)

**Eval:** Test with curl/Postman. Can you generate tours via API?

### Step 5.2: Simple PWA Frontend
**Task:** Build web interface
- Basic HTML/JS that requests geolocation
- User picks vibe with buttons
- Calls backend API, downloads tour, plays audio at GPS triggers
- Use Web Audio API for playback

**Eval:** Test on your phone in Richmond. Can non-technical friends use it?

**Deliverable:** Deployed web app (use Vercel/Netlify for frontend, Railway/Render for backend)

---

## Key Evaluation Metrics

### Quality Evals
1. **Coherence:** Does the narrative flow or is it disjointed facts?
2. **Accuracy:** Spot-check 10 facts against Wikipedia. Any hallucinations?
3. **Navigation Clarity:** Can you follow audio directions without looking at a map?
4. **Persona Consistency:** Does "Ghost Hunter" actually sound different from "Historian"?

### Technical Evals
1. **Latency:** How long to generate a 30-min tour? (Target: <60 seconds)
2. **Cost:** Log API costs per tour. Still within $0.05-$0.15?
3. **Retrieval Quality:** Are the top-3 RAG results actually relevant?

---

## Required Dependencies

```bash
# Core dependencies
pip install openai requests numpy scikit-learn

# Geospatial and routing
pip install osmnx networkx folium

# Web API (for Phase 5)
pip install fastapi uvicorn pydantic

# Optional: for better routing
pip install requests  # for OSRM API calls
```

---

## Project Structure (Suggested)

```
walking_tour/
├── data/
│   ├── richmond_pois.json          # Raw and enriched POI data
│   └── embeddings/                  # Vector embeddings cache
├── src/
│   ├── data_collection.py          # Step 0.1: OSM scraper
│   ├── generate_tour.py            # Step 1: Static tour generation
│   ├── route_planner.py            # Step 2: Route optimization
│   ├── embedding_store.py          # Step 3: Vector store
│   ├── tour_cli.py                 # Step 4: CLI interface
│   └── api/
│       ├── main.py                 # Step 5: FastAPI backend
│       └── models.py               # Pydantic models
├── frontend/                        # Step 5.2: PWA
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── tests/
│   ├── test_generation.py
│   ├── test_routing.py
│   └── eval_accuracy.py            # Fact-checking evals
├── output/                          # Generated tours
│   ├── tours/
│   └── audio/
├── CLAUDE.md
├── IMPLEMENTATION_PLAN.md          # This file
├── README.md
└── requirements.txt
```

---

## Next Step

**Start with Step 0.1:** Build the OSM data collection script.
- Self-contained task
- Teaches you the Overpass API
- Immediately validates if Richmond has enough POIs

Once complete, review the data and decide whether to proceed with Step 0.2 (manual enrichment) or adjust the location/scope.
