# Phase 2: Route Intelligence

## What We've Built

Phase 2 adds intelligent route planning that automatically selects and orders POIs based on location and time constraints.

### Files Created

**Step 2.1: Basic Routing with Walkability Constraints** ✅ COMPLETE

1. **`src/route_planner.py`** - Core route planning module
   - Greedy nearest-neighbor algorithm for route optimization
   - Haversine distance calculation for lat/lng coordinates
   - Time budget constraints with walking speed modeling
   - Configurable visit time per POI
   - Support for circular routes (return to start)
   - Route statistics and summaries

2. **`src/visualize_route.py`** - Interactive map visualization
   - Creates HTML maps using Folium library
   - Shows route path with numbered POI markers
   - Displays route statistics in map legend
   - Option to show all candidate POIs (visited and unvisited)
   - Popups with POI details and vibe tags

3. **`test_phase2_step1.py`** - Comprehensive test suite
   - Tests multiple route scenarios (30, 60, 90 minutes)
   - Validates time constraints
   - Generates example routes and maps
   - Evaluation criteria for route quality

### How It Works

The route planner uses a **greedy nearest-neighbor algorithm**:

1. **Start** at given coordinates
2. **Find** nearest unvisited POI
3. **Calculate** time needed (walking + visit time)
4. **Check** if time budget allows
5. **Add** to route if feasible
6. **Repeat** until time exhausted or no POIs left

**Algorithm Parameters:**
- Walking speed: 5 km/h (standard pedestrian pace)
- Default visit time: 5 minutes per POI (configurable)
- Distance calculation: Haversine formula (great-circle distance)

### Key Features

**Route Planning:**
- ✓ Time-based constraints (e.g., "30 minute tour")
- ✓ Distance optimization (greedy nearest-neighbor)
- ✓ Flexible starting points
- ✓ Circular routes (return to start option)
- ✓ Detailed route statistics

**Visualization:**
- ✓ Interactive HTML maps with Folium
- ✓ Numbered route markers
- ✓ Walking path visualization
- ✓ POI information popups
- ✓ Route summary legend
- ✓ Optional display of unvisited POIs

## Setup Instructions

### Install Dependencies

```bash
pip install folium
```

All other dependencies (numpy, scikit-learn, networkx) are already in `requirements.txt`.

### Verify Setup

```bash
python test_phase2_step1.py
```

You should see:
```
✓ PASS - 🎯 Quick Lunchtime Tour (30 min)
✓ PASS - 🏰 Castle Explorer Tour (60 min)
✓ PASS - 🔄 Circular Walking Tour (90 min)
```

## Using the Route Planner

### Basic Usage

```python
from src.route_planner import load_pois, plan_route, get_route_summary
from src.visualize_route import create_route_map

# Load POI data
pois = load_pois('data/richmond_pois.json')

# Plan a 45-minute route starting from Market Place
route = plan_route(
    start_coords=(54.4025, -1.7367),  # lat, lng
    candidate_pois=pois,
    duration_minutes=45,
    visit_time_per_poi=7,
    return_to_start=True  # circular route
)

# Display summary
print(get_route_summary(route))

# Create interactive map
create_route_map(route, 'my_route.html', show_all_pois=True, all_pois=pois)
```

### Command-Line Testing

Generate example routes and visualizations:

```bash
# Test route planner
python src/route_planner.py

# Test visualization
python src/visualize_route.py

# Comprehensive test suite
python test_phase2_step1.py
```

### Output Files

**Route Data** (`output/routes/*.json`):
```json
{
  "generated_at": "2025-11-15T...",
  "total_distance_km": 0.32,
  "total_time_minutes": 51.8,
  "walking_time_minutes": 3.8,
  "visit_time_minutes": 48,
  "pois_visited": 6,
  "time_remaining": 8.2,
  "start_coords": [54.4039, -1.7394],
  "return_to_start": false,
  "route": [
    {
      "poi_id": "richmond_001",
      "poi_name": "Richmond Castle",
      "coordinates": {"lat": 54.4039, "lng": -1.7394},
      "distance_from_previous_km": 0.0,
      "walking_time_minutes": 0.0
    },
    ...
  ]
}
```

**Interactive Maps** (`output/maps/*.html`):
- Open in any web browser
- Zoom, pan, click on markers
- View route statistics in legend
- See POI details in popups

## Route Planning Algorithm Details

### Distance Calculation

Uses **Haversine formula** for great-circle distance:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)
c = 2 × arcsin(√a)
distance = R × c  (where R = 6371 km, Earth's radius)
```

### Time Estimation

```
walking_time = (distance_km / 5.0 km/h) × 60  # minutes
total_time = walking_time + visit_time
```

### Greedy Selection

At each step:
1. Calculate distance to all unvisited POIs
2. Select nearest POI
3. Check: `time_used + walking_time + visit_time ≤ duration_budget`
4. If yes, add to route; if no, stop

**Pros:**
- Simple and fast (O(n²))
- Guarantees efficient local moves
- No backtracking

**Cons:**
- May not find globally optimal route
- Susceptible to local minima

**Future improvements (Phase 2.2):**
- Add user preference scoring
- Use better TSP algorithms (A*, genetic algorithms)
- Integrate real routing APIs (OSRM, Mapbox)

## Evaluation Criteria

When reviewing generated routes, check:

### 1. Route Logic ✓
- Does the route make geographic sense?
- Are POIs in a logical order?

### 2. No Backtracking ✓
- Is the path efficient?
- No weird loops or doubling back?

### 3. Time Constraints ✓
- Does total time stay within budget?
- Is efficiency reasonable (< 15% unused time)?

### 4. POI Selection ✓
- Are nearest POIs being selected?
- Does greedy algorithm work as expected?

### 5. Circular Routes ✓
- Do return routes properly close the loop?
- Is return distance calculated and included?

## Example Routes

### Quick 30-Minute Tour
- **Start:** Market Place
- **POIs visited:** 5
- **Distance:** 0.17 km
- **Efficiency:** 90% of time used
- **Character:** Compact town center tour

### Extended 60-Minute Tour
- **Start:** Richmond Castle
- **POIs visited:** 6
- **Distance:** 0.32 km
- **Efficiency:** 86% of time used
- **Character:** Castle and museums exploration

### Circular 90-Minute Tour
- **Start/End:** Greyfriars Tower
- **POIs visited:** 8
- **Distance:** 0.53 km (including return)
- **Efficiency:** 96% of time used
- **Character:** Comprehensive circular tour

## Performance Metrics

### Route Generation Speed
- **10 POIs:** < 0.01 seconds
- **50 POIs:** < 0.05 seconds
- **Complexity:** O(n²) where n = number of POIs

### Route Quality
- **Average efficiency:** 90-95% of time budget used
- **Average POIs per 30 min:** 5-6 POIs
- **Walking ratio:** ~5-10% of total time (rest is visiting)

## Limitations & Future Work

### Current Limitations

1. **Straight-line distance** - Doesn't account for actual streets
2. **No obstacles** - Assumes direct walking paths
3. **Fixed walking speed** - Doesn't adjust for terrain or user
4. **Greedy algorithm** - May miss better global routes
5. **No user preferences** - All POIs weighted equally

### Phase 2.2: POI Scoring (Next Step)

Will add:
- User interest vector (history, horror, architecture, etc.)
- POI relevance scoring: `S = α(interest_match) + β(popularity) - δ(distance)`
- Filtered candidate lists based on vibe preferences
- Different routes for different personas

**Example:**
- "Horror" preference → Prioritize castle (executions), Greyfriars (haunted)
- "Architecture" preference → Prioritize Georgian Theatre, churches, bridge

## Cost Estimates

Route planning is **free** (no API calls):
- All calculations done locally
- No LLM or external services needed
- Instant route generation

This makes it suitable for:
- Real-time route adjustment
- Multiple route comparisons
- Pre-generating cached routes

## Troubleshooting

**"No POIs in route"**
- Time budget too small (try increasing duration)
- Starting point too far from all POIs
- Visit time per POI too high

**"Map doesn't display"**
- Check that HTML file was created
- Try opening in different browser
- Check browser console for errors

**"Routes don't make sense geographically"**
- This is expected with greedy algorithm
- Phase 2.2 will add better optimization
- For now, it prioritizes nearest-neighbor

## Step 2.2: POI Scoring with User Preferences ✅ COMPLETE

### Overview

Phase 2 Step 2.2 adds **intelligent POI selection** based on user interests. Instead of just picking the nearest POI, the system now scores each POI based on how well it matches the user's preferences.

**Scoring Formula:**
```
S_poi = α(interest_match) + β(popularity) - δ(distance)
```

Where:
- **interest_match**: How well POI tags match user interests (0-1, using Jaccard similarity)
- **popularity**: POI importance/quality score based on enrichment (0-1)
- **distance**: Distance penalty, normalized (0-1)
- **α, β, δ**: Weighting coefficients (default: 0.6, 0.3, 0.1)

### User Profiles

Six predefined profiles available:

| Profile | Interests | Example POIs Prioritized |
|---------|-----------|--------------------------|
| **history_lover** | history, medieval, military, political, victorian | Richmond Castle, Museums, Churches |
| **ghost_hunter** | haunted, mysterious, ruins, religious, dramatic | Greyfriars Tower (haunted!), St Mary's |
| **architecture_fan** | architecture, georgian, engineering, folly, medieval | Georgian Theatre, Richmond Bridge |
| **nature_seeker** | nature, scenic, picturesque, peaceful, romantic | Richmond Falls, Richmond Bridge |
| **culture_enthusiast** | culture, arts, educational, local, social | Museums, Theatre, Market Place |
| **casual_tourist** | Balanced mix of all interests | Popular tourist attractions |

### Usage

```python
from src.route_planner import load_pois, plan_route_with_preferences
from src.visualize_route import create_route_map

# Load POIs
pois = load_pois('data/richmond_pois.json')

# Generate route based on user preferences
route = plan_route_with_preferences(
    start_coords=(54.4025, -1.7367),
    candidate_pois=pois,
    duration_minutes=45,
    user_profile='ghost_hunter',  # Choose profile!
    visit_time_per_poi=5,
    return_to_start=False
)

# Create map
create_route_map(route, 'ghost_tour.html', show_all_pois=True, all_pois=pois)
```

### Testing

```bash
# Run comprehensive preference-based routing test
python test_phase2_step2.py
```

This generates 4 different routes from the same starting point, one for each major profile. Maps are saved to `output/maps_with_preferences/`.

### Key Results from Testing

**Starting from Market Place, 45-minute tours:**

- **History Lover**: 6 POIs, starts with **Richmond Castle** (score: 0.515)
- **Ghost Hunter**: 7 POIs, starts with **Greyfriars Tower** (score: 0.607 - haunted!)
- **Architecture Fan**: 6 POIs, includes **Richmond Bridge** (engineering interest)
- **Nature Seeker**: 6 POIs, uniquely visits **Richmond Falls** (score: 0.852 - perfect match!)

**Observations:**
- ✅ Different profiles generate different routes
- ✅ High-interest POIs are prioritized even if not nearest
- ✅ Scoring successfully balances interest vs. distance

### How It Works

1. **User selects a profile** (or defines custom interests)
2. **At each step**, system scores all unvisited POIs:
   - Calculate interest match using vibe tag overlap
   - Add popularity bonus for enriched POIs
   - Subtract distance penalty
3. **Select highest-scoring POI** that fits time budget
4. **Repeat** until time exhausted

### Comparison: Step 2.1 vs Step 2.2

| Aspect | Step 2.1 (Nearest) | Step 2.2 (Preferences) |
|--------|-------------------|------------------------|
| **Selection** | Always picks nearest POI | Picks best-scoring POI |
| **Routes** | Same for all users | Personalized per profile |
| **Distance** | Minimized | Balanced with interest |
| **Use case** | Quick optimization | Personalized experiences |

### Custom Profiles

You can create custom profiles:

```python
# Define custom interests
my_interests = ['military', 'history', 'dramatic']

# Use with scoring weights
route = plan_route_with_preferences(
    ...,
    user_profile='custom',  # Won't match, uses casual_tourist
    scoring_weights={'alpha': 0.7, 'beta': 0.2, 'delta': 0.1}  # Prioritize interests more
)
```

Or modify `src/poi_scorer.py` to add permanent profiles.

### Files Created

- **`src/poi_scorer.py`** - POI scoring engine with user profiles
- **`src/route_planner.py`** - Updated with `plan_route_with_preferences()`
- **`test_phase2_step2.py`** - Comprehensive preference testing

### Output Files

- **Routes**: `output/routes_with_preferences/*.json`
- **Maps**: `output/maps_with_preferences/*.html` (color-coded by profile)

## Phase 2 Complete! ✅

Both Step 2.1 (basic routing) and Step 2.2 (preference-based scoring) are now implemented and tested.

**What we built:**
- ✅ Time-based route planning with walkability constraints
- ✅ Distance optimization using greedy nearest-neighbor
- ✅ User preference profiles and POI scoring
- ✅ Personalized route generation
- ✅ Interactive map visualization

**Next Phase:**

**Phase 3: RAG & Embeddings**
- Step 3.1: Create embeddings for semantic search
- Step 3.2: Replace keyword matching with vector similarity
- Step 3.3: Context-aware narrative generation

This will upgrade from keyword-based tag matching to semantic understanding, enabling even better POI matching and narrative generation.

See `IMPLEMENTATION_PLAN.md` for the complete roadmap.
