# mentor_matching_system.py Documentation

## Overview
Python class for mentor-mentee matching using semantic similarity and stable matching algorithms.

**File**: `claude/mentor_matching_system.py`  
**Lines**: 411  
**Dependencies**: `psycopg2`, standard Python libraries  
**Database**: PostgreSQL with pgvector extension

---

## Purpose

This file implements the core matching engine that:
- Calculates compatibility scores between mentees and mentors
- Generates preference rankings for stable matching
- Runs Gale-Shapley algorithm to produce optimal pairings
- Stores results in database for analysis

---

## Class: `MentorMatchingSystem`

### Initialization

```python
matcher = MentorMatchingSystem(db_connection_string)
```

**Parameters**:
- `db_connection_string` (str): PostgreSQL connection string
  - Format: `"postgresql://user:password@host:port/database"`
  - Example: `"postgresql://postgres:password123@localhost:5432/mentor_db"`

**Establishes**:
- Database connection using psycopg2
- RealDictCursor for dict-like query results
- Error handling for connection failures

---

## Implemented Functions (Day 1)

### 1. `compute_semantic_similarity(mentee_id, mentor_id)`

Calculates semantic similarity using pgvector cosine similarity.

**Parameters**:
- `mentee_id` (str): UUID of mentee profile
- `mentor_id` (str): UUID of mentor profile

**Returns**: 
- `float`: Similarity score between 0 and 1 (1 = identical vectors)

**How it works**:
- Queries embeddings table for both profiles
- Uses pgvector's `<=>` operator for cosine distance
- Formula: `1 - cosine_distance`

**SQL Query**:
```sql
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = %s 
  AND e2.mentor_profile_id = %s
  AND e1.embedding_type = 'combined'
  AND e2.embedding_type = 'combined'
```

**Example**:
```python
similarity = matcher.compute_semantic_similarity(
    "mentee-uuid-123",
    "mentor-uuid-456"
)
# Returns: 0.87 (87% similar)
```

---

### 2. `compute_expertise_match(mentee_id, mentor_id)`

Calculates expertise level compatibility based on skill gap.

**Parameters**:
- `mentee_id` (str): UUID of mentee profile
- `mentor_id` (str): UUID of mentor profile

**Returns**: 
- `float`: Expertise match score (0.3 or 1.0)

**Scoring Logic**:
| Mentor Level - Mentee Level | Score | Reason |
|------------------------------|-------|--------|
| 2 or 3 levels higher | 1.0 | Optimal mentoring gap |
| Any other gap | 0.3 | Too close or too far |

**Example**:
```python
# Mentee at level 2, Mentor at level 4
score = matcher.compute_expertise_match(mentee_id, mentor_id)
# Returns: 1.0 (gap = 2, optimal)

# Mentee at level 3, Mentor at level 4
score = matcher.compute_expertise_match(mentee_id, mentor_id)
# Returns: 0.3 (gap = 1, too close)
```

---

### 3. `compute_combined_score(mentee_id, mentor_id)`

Calculates final weighted compatibility score.

**Parameters**:
- `mentee_id` (str): UUID of mentee profile
- `mentor_id` (str): UUID of mentor profile

**Returns**: 
- `dict` with keys:
  - `semantic_score` (float): Cosine similarity score
  - `expertise_score` (float): Expertise match score
  - `final_score` (float): Weighted combination

**Formula**:
```
final_score = (0.8 × semantic_score) + (0.2 × expertise_score)
```

**Weighting Breakdown**:
- **80% semantic similarity**: Primary driver - interest/expertise alignment
- **20% expertise match**: Secondary - ensures appropriate skill gap

**Example**:
```python
scores = matcher.compute_combined_score(mentee_id, mentor_id)
# Returns:
# {
#     'semantic_score': 0.85,
#     'expertise_score': 1.0,
#     'final_score': 0.88  # (0.8 * 0.85) + (0.2 * 1.0)
# }
```

---

## Skeleton Functions (TODO: Days 2-4)

### 4. `generate_preference_rankings()`

Generates ranked preference lists for Gale-Shapley algorithm.

**Status**: TODO - Day 2  
**Returns**: `Tuple[Dict, Dict, Dict]`

**Will produce**:
- `mentee_preferences`: `{mentee_id: [(mentor_id, score), ...]}`
- `mentor_preferences`: `{mentor_id: [(mentee_id, score), ...]}`
- `score_matrix`: `{mentee_id: {mentor_id: score_dict}}`

**Implementation Steps** (from TODO comments):
1. Fetch all active mentees from mentee_profiles
2. Fetch available mentors (current_mentee_count < max_mentee_capacity)
3. For each mentee:
   - Compute combined_score with every available mentor
   - Sort mentors by final_score (descending)
   - Store as mentee_preferences[mentee_id] = [(mentor_id, score), ...]
4. For each mentor:
   - Compute combined_score with every mentee
   - Sort mentees by final_score (descending)
   - Store as mentor_preferences[mentor_id] = [(mentee_id, score), ...]
5. Create score_matrix[mentee_id][mentor_id] = final_score

**Example Output**:
```python
mentee_preferences = {
    'mentee-uuid-1': [
        ('mentor-uuid-5', 0.92),
        ('mentor-uuid-3', 0.85),
        ('mentor-uuid-1', 0.78)
    ],
    # ... more mentees
}

mentor_preferences = {
    'mentor-uuid-1': [
        ('mentee-uuid-2', 0.88),
        ('mentee-uuid-5', 0.82),
        ('mentee-uuid-1', 0.78)
    ],
    # ... more mentors
}

score_matrix = {
    'mentee-uuid-1': {
        'mentor-uuid-1': {'semantic_score': 0.75, 'expertise_score': 1.0, 'final_score': 0.80},
        'mentor-uuid-2': {'semantic_score': 0.82, 'expertise_score': 0.3, 'final_score': 0.72},
        # ... all mentors
    },
    # ... all mentees
}
```

---

### 5. `gale_shapley_matching(mentee_preferences, mentor_preferences, mentor_capacities)`

Implements stable matching algorithm with capacity constraints.

**Status**: TODO - Day 3  
**Returns**: `List[Tuple[str, str]]` (list of mentee_id, mentor_id pairs)

**Parameters**:
- `mentee_preferences` (Dict): Mentee's ranked mentor list
- `mentor_preferences` (Dict): Mentor's ranked mentee list
- `mentor_capacities` (Dict): {mentor_id: available_slots}

**Algorithm Steps** (from TODO comments):
1. Initialize free_mentees list with all mentees
2. Initialize mentor_matches dict: {mentor_id: [list of matched mentees]}
3. Initialize mentee_matches dict: {mentee_id: mentor_id or None}
4. While free_mentees is not empty:
   a. Pop a mentee from free_mentees
   b. Get mentee's next preferred mentor (not yet proposed to)
   c. If mentor has capacity:
      - Accept proposal
      - Add mentee to mentor_matches[mentor_id]
   d. If mentor is at capacity:
      - Compare with least preferred current match
      - If mentee is more preferred, replace least preferred
      - Otherwise reject mentee (add back to free_mentees)
5. Return list of (mentee_id, mentor_id) pairings

**What it produces**:
```python
pairings = [
    ('mentee-uuid-1', 'mentor-uuid-5'),
    ('mentee-uuid-2', 'mentor-uuid-3'),
    ('mentee-uuid-3', 'mentor-uuid-5'),  # Same mentor (capacity > 1)
    # ... more pairs
]
```

**Why Gale-Shapley**:
- Guarantees stable matches (no "blocking pairs")
- Handles capacity constraints (mentors can take multiple mentees)
- Optimal for mentee-proposing variant

---

### 6. `store_matches(pairings, score_matrix, algorithm_name)`

Stores final matches in database.

**Status**: TODO - Day 2-3  
**Returns**: `int` (number of successful inserts)

**Parameters**:
- `pairings` (List[Tuple]): List of (mentee_id, mentor_id) pairs
- `score_matrix` (Dict): Nested dict with score breakdowns
- `algorithm_name` (str): Name of algorithm used (e.g., 'Gale-Shapley')

**Implementation Steps** (from TODO comments):
1. For each (mentee_id, mentor_id) pair:
   - Lookup scores from score_matrix
   - INSERT into matches table
   - Generate match_id (UUID)
   - Set status = 'pending'
   - Set created_at = current timestamp
2. Return count of successful inserts

**Database INSERT**:
```sql
INSERT INTO matches (
    match_id, mentor_id, mentee_id, algorithm_name,
    semantic_score, expertise_score, final_score, status, created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
```

**Example Usage**:
```python
num_stored = matcher.store_matches(
    pairings=pairings,
    score_matrix=score_matrix,
    algorithm_name='Gale-Shapley'
)
print(f"Stored {num_stored} matches")
```

---

### 7. `execute_matching(algorithm_name='Gale-Shapley')`

Main execution pipeline orchestrating the entire process.

**Status**: TODO - Day 4  
**Returns**: `int` (number of successful matches)

**Parameters**:
- `algorithm_name` (str): Name of matching algorithm (default: 'Gale-Shapley')

**Pipeline Steps** (from TODO comments):
1. Print "Starting matching process..."
2. Call generate_preference_rankings() → get preferences and score_matrix
3. Fetch mentor capacities from database
4. Call gale_shapley_matching() → get pairings
5. Call store_matches() → save to database
6. Print summary statistics (total matches, avg score)
7. Return number of successful matches

**Example Flow**:
```python
# Day 4: Full pipeline
num_matches = matcher.execute_matching(algorithm_name='Gale-Shapley')
# Output:
# Starting matching process...
# Generating preferences for 30 mentees and 20 mentors...
# Running Gale-Shapley algorithm...
# Storing 28 matches to database...
# Average match score: 0.82
# Returns: 28
```

---

## Utility Functions

### `get_available_mentors()`

Fetches all mentors with available capacity.

**Returns**: `List[Dict]`

**Fields returned**:
- `mentor_profile_id` (UUID)
- `user_id` (UUID)
- `expertise_area` (TEXT)
- `expertise_level` (INTEGER 1-5)
- `max_mentee_capacity` (INTEGER)
- `current_mentee_count` (INTEGER)
- `available_slots` (INTEGER) - Calculated field

**SQL Query**:
```sql
SELECT 
    mentor_profile_id,
    user_id,
    expertise_area,
    expertise_level,
    max_mentee_capacity,
    current_mentee_count,
    (max_mentee_capacity - current_mentee_count) as available_slots
FROM mentor_profiles
WHERE current_mentee_count < max_mentee_capacity
ORDER BY available_slots DESC
```

**Example**:
```python
mentors = matcher.get_available_mentors()
for mentor in mentors:
    print(f"{mentor['expertise_area']}: {mentor['available_slots']} slots")
```

---

### `get_all_mentees()`

Fetches all mentee profiles.

**Returns**: `List[Dict]`

**Fields returned**:
- `mentee_profile_id` (UUID)
- `user_id` (UUID)
- `main_interest` (TEXT)
- `main_interest_level` (INTEGER 1-5)

**SQL Query**:
```sql
SELECT 
    mentee_profile_id,
    user_id,
    main_interest,
    main_interest_level
FROM mentee_profiles
```

**Example**:
```python
mentees = matcher.get_all_mentees()
print(f"Total mentees: {len(mentees)}")
```

---

### `close()`

Closes database connection and cleans up resources.

**Returns**: None

**What it does**:
- Closes cursor
- Closes connection
- Prints confirmation message

**Usage**:
```python
matcher.close()
# Output: "✓ Database connection closed"
```

---

## Complete Usage Example

```python
#!/usr/bin/env python3
"""
Example usage of MentorMatchingSystem
"""

from mentor_matching_system import MentorMatchingSystem

# Configuration
DB_CONNECTION = "postgresql://postgres:password123@localhost:5432/mentor_db"

# Initialize system
matcher = MentorMatchingSystem(DB_CONNECTION)

# Day 1: Test scoring functions with real data
print("\n=== Testing Scoring Functions ===")
mentee_id = "example-mentee-uuid"
mentor_id = "example-mentor-uuid"

# Individual scores
semantic = matcher.compute_semantic_similarity(mentee_id, mentor_id)
expertise = matcher.compute_expertise_match(mentee_id, mentor_id)
print(f"Semantic similarity: {semantic:.3f}")
print(f"Expertise match: {expertise:.3f}")

# Combined score
scores = matcher.compute_combined_score(mentee_id, mentor_id)
print(f"Final score: {scores['final_score']:.3f}")

# Check available data
print("\n=== Checking Available Data ===")
mentors = matcher.get_available_mentors()
mentees = matcher.get_all_mentees()
print(f"Available mentors: {len(mentors)}")
print(f"Total mentees: {len(mentees)}")

# Day 4: Run full matching pipeline (once implemented)
# print("\n=== Running Matching Pipeline ===")
# num_matches = matcher.execute_matching(algorithm_name='Gale-Shapley')
# print(f"Created {num_matches} matches")

# Cleanup
matcher.close()
```

---

## Dependencies

### Required Python Packages

```bash
# Install via pip
pip install psycopg2-binary

# Or if using system PostgreSQL libraries
pip install psycopg2
```

### Python Standard Library
- `typing` - Type hints (Dict, List, Tuple, Optional)
- `uuid` - UUID generation for match IDs
- `datetime` - Timestamps for match creation

### Database Requirements

**PostgreSQL Extensions**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
```

**Schema Requirements**:
- Load `postgres/schema_minimal.sql`
- 5 tables: users, mentor_profiles, mentee_profiles, embeddings, matches
- Embeddings must be 384-dimensional vectors

**Data Requirements**:
- At least 1 mentor with available capacity
- At least 1 mentee
- Each profile must have a 'combined' type embedding (384-dim)

---

## Implementation Status

| Component | Status | Day | Lines |
|-----------|--------|-----|-------|
| Database connection | ✅ Done | 1 | ~15 |
| Semantic similarity | ✅ Done | 1 | ~20 |
| Expertise matching | ✅ Done | 1 | ~20 |
| Combined scoring | ✅ Done | 1 | ~15 |
| Preference rankings | ⏳ TODO | 2 | ~50 |
| Storage functions | ⏳ TODO | 2-3 | ~30 |
| Gale-Shapley algorithm | ⏳ TODO | 3 | ~60 |
| Main pipeline | ⏳ TODO | 4 | ~40 |
| Utility functions | ✅ Done | 1 | ~20 |
| Documentation | ✅ Done | 1 | ~30 |

**Total**: ~150 lines implemented, ~180 lines TODO

---

## Technical Details

### Weighting Rationale

**80% Semantic Similarity**:
- Primary driver of compatibility
- Measures interest/expertise alignment
- Based on 384-dim embeddings from all-MiniLM-L6-v2 model
- Captures nuanced topic relationships

**20% Expertise Match**:
- Secondary constraint
- Ensures appropriate skill gap for mentoring
- Binary: optimal gap (1.0) or suboptimal (0.3)
- Prevents pairing experts with other experts

### Expertise Gap Logic

**Why 2-3 levels is optimal**:
- **Too close (0-1 gap)**: Mentor and mentee at similar level, limited teaching potential
- **Optimal (2-3 gap)**: Mentor experienced enough to guide, not overwhelmingly advanced
- **Too far (4-5 gap)**: Communication barrier, mentor may lack patience for basics

**Example**:
| Mentee | Mentor | Gap | Score | Interpretation |
|--------|--------|-----|-------|----------------|
| Level 1 | Level 3 | 2 | 1.0 | Perfect mentoring dynamic |
| Level 2 | Level 4 | 2 | 1.0 | Ideal learning progression |
| Level 3 | Level 5 | 2 | 1.0 | Advanced but teachable |
| Level 2 | Level 3 | 1 | 0.3 | Too similar, peer relationship |
| Level 1 | Level 5 | 4 | 0.3 | Too large gap, communication issues |

### Database Design Choices

**RealDictCursor**:
- Returns rows as dictionaries instead of tuples
- Cleaner code: `row['mentor_id']` vs `row[0]`
- Type-safe access to columns

**Parameterized Queries**:
- All SQL uses `%s` placeholders
- Prevents SQL injection
- Safe for user-provided UUIDs

**Error Handling**:
- Try-except on connection establishment
- Graceful failure messages
- Prevents silent failures

---

## File Structure

```
mentor_matching_system.py (411 lines)
│
├── Module Docstring (3 lines)
├── Imports (8 lines)
│   ├── psycopg2, RealDictCursor
│   ├── typing annotations
│   ├── uuid, datetime
│
├── Class: MentorMatchingSystem
│   │
│   ├── __init__(db_connection_string)  [IMPLEMENTED]
│   │   └── Database connection setup
│   │
│   ├── SCORING FUNCTIONS [IMPLEMENTED - Day 1]
│   │   ├── compute_semantic_similarity(mentee_id, mentor_id)
│   │   ├── compute_expertise_match(mentee_id, mentor_id)
│   │   └── compute_combined_score(mentee_id, mentor_id)
│   │
│   ├── PREFERENCE RANKING [TODO - Day 2]
│   │   └── generate_preference_rankings()
│   │
│   ├── MATCHING ALGORITHM [TODO - Day 3]
│   │   └── gale_shapley_matching(mentee_prefs, mentor_prefs, capacities)
│   │
│   ├── STORAGE FUNCTIONS [TODO - Day 2-3]
│   │   └── store_matches(pairings, score_matrix, algorithm_name)
│   │
│   ├── MAIN EXECUTION [TODO - Day 4]
│   │   └── execute_matching(algorithm_name)
│   │
│   └── UTILITY FUNCTIONS [IMPLEMENTED]
│       ├── get_available_mentors()
│       ├── get_all_mentees()
│       └── close()
│
└── Usage Example (if __name__ == "__main__")
    └── Test code for Day 1 functions
```

---

## Key Features

### Design Principles
✅ **Standalone**: No imports from other project files  
✅ **Type-hinted**: All functions have type annotations for clarity  
✅ **Error-handled**: Database connection failures caught gracefully  
✅ **Documented**: Clear docstrings on all functions  
✅ **Testable**: Can test components independently  
✅ **Extensible**: Easy to add new scoring metrics  

### Code Quality
- PEP 8 compliant formatting
- Clear variable names
- Logical function organization
- Comprehensive comments on TODOs

### Performance Considerations
- Uses pgvector IVFFlat indexes for fast similarity search
- Parameterized queries prevent SQL injection
- RealDictCursor improves code readability
- Single database connection per instance

---

## Testing Strategy

### Unit Testing (Day 1)
```python
# Test database connection
def test_connection():
    matcher = MentorMatchingSystem(DB_CONNECTION)
    assert matcher.conn is not None
    matcher.close()

# Test scoring functions
def test_semantic_similarity():
    matcher = MentorMatchingSystem(DB_CONNECTION)
    score = matcher.compute_semantic_similarity(mentee_id, mentor_id)
    assert 0 <= score <= 1
    matcher.close()

# Test expertise logic
def test_expertise_match():
    matcher = MentorMatchingSystem(DB_CONNECTION)
    score = matcher.compute_expertise_match(mentee_id, mentor_id)
    assert score in [0.3, 1.0]
    matcher.close()
```

### Integration Testing (Day 4)
```python
# Test full pipeline
def test_full_matching():
    matcher = MentorMatchingSystem(DB_CONNECTION)
    num_matches = matcher.execute_matching()
    assert num_matches > 0

    # Verify matches in database
    matcher.cursor.execute("SELECT COUNT(*) FROM matches WHERE status='pending'")
    count = matcher.cursor.fetchone()[0]
    assert count == num_matches

    matcher.close()
```

---

## Troubleshooting

### Common Issues

**Issue**: "Database connection failed"
```
Solution: 
- Check PostgreSQL is running: docker ps
- Verify connection string
- Ensure database 'mentor_db' exists
- Check credentials (postgres:password123)
```

**Issue**: "relation 'embeddings' does not exist"
```
Solution:
- Load schema: psql -d mentor_db -f postgres/schema_minimal.sql
- Verify tables: psql -d mentor_db -c "\dt"
```

**Issue**: "No embeddings found"
```
Solution:
- Person C needs to generate embeddings
- Check: SELECT COUNT(*) FROM embeddings;
- Verify dimensions: SELECT vector_dims(embedding_vector) FROM embeddings LIMIT 1;
```

**Issue**: "TypeError: 'NoneType' object is not subscriptable"
```
Solution:
- Query returned no results
- Check mentee_id and mentor_id are valid UUIDs
- Ensure profiles exist in database
```

**Issue**: "Similarity score always 0.0"
```
Solution:
- Embeddings missing or wrong type
- Check: SELECT * FROM embeddings WHERE embedding_type='combined';
- Verify embedding_type is exactly 'combined'
```

---

## Next Steps

### For Implementers (Person A)
1. ✅ Day 1: Test scoring functions with real data
2. ⏳ Day 2: Implement `generate_preference_rankings()`
3. ⏳ Day 2: Implement `store_matches()`
4. ⏳ Day 3: Implement `gale_shapley_matching()`
5. ⏳ Day 4: Implement `execute_matching()`
6. ⏳ Day 4: Run full integration test
7. ⏳ Day 4: Generate results for analysis

### For Data Generators (Person C)
- Use `get_available_mentors()` to validate data format
- Ensure all mentors have embeddings (type='combined')
- Ensure all mentees have embeddings (type='combined')
- Verify embedding dimensions are 384
- Test with `compute_semantic_similarity()` once data loaded
- Provide at least 20 mentors with available capacity
- Provide at least 30 mentees

### For Database Admins (Person B)
- Load `postgres/schema_minimal.sql`
- Verify pgvector extension installed
- Create IVFFlat indexes on embeddings table
- Provide connection string: `postgresql://postgres:password123@localhost:5432/mentor_db`
- Monitor database during matching execution
- Verify matches table populated after execution

---

## Validation Checklist

Before testing this file:
- [ ] PostgreSQL running (docker ps shows container)
- [ ] pgvector extension loaded (SELECT * FROM pg_extension WHERE extname='vector')
- [ ] Schema loaded (\dt shows 5 tables)
- [ ] Users exist (SELECT COUNT(*) FROM users > 0)
- [ ] Mentor profiles exist (SELECT COUNT(*) FROM mentor_profiles > 0)
- [ ] Mentee profiles exist (SELECT COUNT(*) FROM mentee_profiles > 0)
- [ ] Embeddings exist (SELECT COUNT(*) FROM embeddings WHERE embedding_type='combined' > 0)
- [ ] Embeddings are 384-dim (SELECT vector_dims(embedding_vector) FROM embeddings LIMIT 1 = 384)
- [ ] psycopg2 installed (pip list | grep psycopg2)
- [ ] Python 3.7+ (type hints require modern Python)

---

## Performance Metrics

### Expected Performance (20 mentors, 30 mentees)

**Preference Generation**:
- Pairs to compute: 20 × 30 = 600
- Time per pair: ~5ms (semantic + expertise)
- Total time: ~3 seconds

**Gale-Shapley Matching**:
- Iterations: ~30-50 (depends on preferences)
- Time per iteration: ~1ms
- Total time: ~50ms

**Database Storage**:
- Matches to insert: ~25-30
- Time per insert: ~2ms
- Total time: ~60ms

**Total Pipeline**: ~4 seconds for full execution

---

## References

### Algorithm Resources
- Gale-Shapley Algorithm: [Wikipedia](https://en.wikipedia.org/wiki/Gale%E2%80%93Shapley_algorithm)
- Stable Matching Problem: Academic paper on stable matching with capacity constraints
- pgvector Documentation: [GitHub](https://github.com/pgvector/pgvector)

### Related Files
- `postgres/schema_minimal.sql` - Database schema definition
- `SCHEMA_MINIMAL_DOCS.md` - Schema documentation
- `docs/ARCHITECTURE.md` - System architecture (TODO)

---

## Version History

**Version 1.0** (January 21, 2026)
- Initial implementation
- Day 1 functions complete (scoring)
- Day 2-4 functions outlined with TODOs
- Documentation complete

---

**Generated**: Wednesday, January 21, 2026, 1:36 PM +0545  
**Author**: Person A (Algorithm Lead)  
**File**: `claude/mentor_matching_system.py`  
**Status**: Day 1 Complete, Ready for Testing
