# System Architecture Documentation

## Overview

Comprehensive architecture for the mentor-mentee matching system prototype, detailing database schema, matching algorithm, data flow, and team interfaces.

**System**: Mentor-Mentee Matching Platform  
**Timeline**: Week 1 Prototype (4 days)  
**Stack**: PostgreSQL + pgvector, Python, Docker  
**Algorithm**: Gale-Shapley with semantic similarity scoring

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MENTOR-MENTEE MATCHING SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Person C   │────▶│   Person B   │────▶│   Person A   │
│ Data Generator│     │  Database    │     │  Algorithm   │
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │                     │
      │ Generates           │ Provides            │ Produces
      ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Dummy Users  │────▶│ PostgreSQL   │────▶│   Matches    │
│ Embeddings   │     │ + pgvector   │     │   Table      │
│ (384-dim)    │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘

DATA FLOW:
1. Person C: Generate users → profiles → embeddings (384-dim)
2. Person B: Setup database → load schema → verify data
3. Person A: Query embeddings → compute scores → run matching → store results
```

---

## Database Schema

### Core Tables (5 Total)

#### 1. `users`
Basic user identity and role management.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('mentor', 'mentee', 'both')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Central user registry  
**Keys**: Primary key on `user_id`  
**Indexes**: `role`, `email`

---

#### 2. `mentor_profiles`
Mentor expertise and capacity tracking.

```sql
CREATE TABLE mentor_profiles (
    mentor_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
    expertise_area TEXT NOT NULL,
    expertise_level INTEGER NOT NULL CHECK (expertise_level BETWEEN 1 AND 5),
    max_mentee_capacity INTEGER DEFAULT 3 CHECK (max_mentee_capacity > 0),
    current_mentee_count INTEGER DEFAULT 0 CHECK (current_mentee_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_capacity CHECK (current_mentee_count <= max_mentee_capacity)
);
```

**Purpose**: Mentor-specific data with capacity management  
**Foreign Keys**: `user_id` → `users.user_id`  
**Constraints**: `current_mentee_count <= max_mentee_capacity`  
**Indexes**: `user_id`, `(current_mentee_count, max_mentee_capacity)`, `(expertise_area, expertise_level)`

---

#### 3. `mentee_profiles`
Mentee learning interests.

```sql
CREATE TABLE mentee_profiles (
    mentee_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,
    main_interest TEXT NOT NULL,
    main_interest_level INTEGER NOT NULL CHECK (main_interest_level BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Mentee-specific learning goals  
**Foreign Keys**: `user_id` → `users.user_id`  
**Indexes**: `user_id`, `(main_interest, main_interest_level)`

---

#### 4. `embeddings` ⭐
Vector embeddings for semantic similarity matching.

```sql
CREATE TABLE embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_profile_id UUID REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_profile_id UUID REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    embedding_type VARCHAR(50) NOT NULL CHECK (embedding_type IN ('main_interest', 'expertise', 'combined')),
    embedding_vector vector(384) NOT NULL,  -- CRITICAL: 384 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_profile_exclusivity CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);
```

**Purpose**: Store 384-dim vectors from all-MiniLM-L6-v2 model  
**Foreign Keys**: `mentor_profile_id` OR `mentee_profile_id` (mutually exclusive)  
**Critical Constraint**: Exactly one profile type per embedding  
**Indexes**: 
- `mentor_profile_id`, `mentee_profile_id`, `embedding_type`
- **IVFFlat index** on `embedding_vector` for fast cosine similarity (100 lists)

---

#### 5. `matches`
Final mentor-mentee pairings with scoring.

```sql
CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID NOT NULL REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_id UUID NOT NULL REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    algorithm_name VARCHAR(100) NOT NULL,
    semantic_score FLOAT CHECK (semantic_score BETWEEN 0 AND 1),
    expertise_score FLOAT CHECK (expertise_score BETWEEN 0 AND 1),
    final_score FLOAT NOT NULL CHECK (final_score BETWEEN 0 AND 1),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'declined')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_mentor_mentee_pair UNIQUE (mentor_id, mentee_id)
);
```

**Purpose**: Store final matching results  
**Foreign Keys**: `mentor_id` → `mentor_profiles`, `mentee_id` → `mentee_profiles`  
**Constraints**: Unique mentor-mentee pairs  
**Indexes**: `mentor_id`, `mentee_id`, `status`, `final_score DESC`, `algorithm_name`

---

### Helper Views

#### `v_available_mentors`
```sql
CREATE VIEW v_available_mentors AS
SELECT 
    m.mentor_profile_id,
    u.name,
    u.email,
    m.expertise_area,
    m.expertise_level,
    m.max_mentee_capacity,
    m.current_mentee_count,
    (m.max_mentee_capacity - m.current_mentee_count) as available_slots
FROM mentor_profiles m
JOIN users u ON m.user_id = u.user_id
WHERE m.current_mentee_count < m.max_mentee_capacity
ORDER BY available_slots DESC;
```

**Usage**: Quick lookup of mentors accepting new mentees

---

#### `v_mentees`
```sql
CREATE VIEW v_mentees AS
SELECT 
    me.mentee_profile_id,
    u.name,
    u.email,
    me.main_interest,
    me.main_interest_level
FROM mentee_profiles me
JOIN users u ON me.user_id = u.user_id
ORDER BY me.created_at DESC;
```

**Usage**: List all mentees with contact info

---

#### `v_match_details`
```sql
CREATE VIEW v_match_details AS
SELECT 
    m.match_id,
    m.algorithm_name,
    m.semantic_score,
    m.expertise_score,
    m.final_score,
    m.status,
    mentor_user.name as mentor_name,
    mp.expertise_area as mentor_expertise,
    mp.expertise_level as mentor_level,
    mentee_user.name as mentee_name,
    mep.main_interest as mentee_interest,
    mep.main_interest_level as mentee_level,
    m.created_at as matched_at
FROM matches m
JOIN mentor_profiles mp ON m.mentor_id = mp.mentor_profile_id
JOIN users mentor_user ON mp.user_id = mentor_user.user_id
JOIN mentee_profiles mep ON m.mentee_id = mep.mentee_profile_id
JOIN users mentee_user ON mep.user_id = mentee_user.user_id
ORDER BY m.final_score DESC;
```

**Usage**: Complete match information for analysis

---

## Matching Algorithm

### Scoring System

#### Semantic Similarity (80% weight)
Uses pgvector cosine similarity between 384-dim embeddings.

**Query**:
```sql
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = %s 
  AND e2.mentor_profile_id = %s
  AND e1.embedding_type = 'combined'
  AND e2.embedding_type = 'combined'
```

**Output**: Score between 0 and 1 (1 = identical interests/expertise)

---

#### Expertise Match (20% weight)
Binary scoring based on skill level gap.

**Logic**:
```python
level_gap = mentor_level - mentee_level

if 2 <= level_gap <= 3:
    expertise_score = 1.0  # Optimal mentoring gap
else:
    expertise_score = 0.3  # Suboptimal
```

**Rationale**:
- Gap 2-3: Mentor experienced enough to guide effectively
- Gap 0-1: Too similar, peer relationship
- Gap 4-5: Too far, communication barriers

---

#### Combined Score
**Formula**:
```
final_score = (0.8 × semantic_similarity) + (0.2 × expertise_match)
```

**Example**:
```
Semantic: 0.85
Expertise: 1.0 (gap = 2)
Final: (0.8 × 0.85) + (0.2 × 1.0) = 0.88
```

---

### Gale-Shapley Stable Matching

#### Algorithm Overview
1. Generate preference rankings for all mentees and mentors
2. Run Gale-Shapley with capacity constraints
3. Produce stable pairings (no blocking pairs)

#### Preference Generation
```python
mentee_preferences = {
    'mentee-1': [('mentor-5', 0.92), ('mentor-3', 0.85), ...],
    'mentee-2': [('mentor-2', 0.88), ('mentor-1', 0.81), ...],
    # ... sorted by final_score descending
}

mentor_preferences = {
    'mentor-1': [('mentee-2', 0.88), ('mentee-5', 0.82), ...],
    'mentor-2': [('mentee-1', 0.91), ('mentee-3', 0.87), ...],
    # ... sorted by final_score descending
}
```

#### Matching Process
1. All mentees start as "free"
2. Free mentee proposes to next mentor on preference list
3. If mentor has capacity: accept
4. If mentor at capacity: compare with least preferred current match
5. Replace if new mentee is more preferred
6. Repeat until all mentees matched or exhausted options

**Output**: List of (mentee_id, mentor_id) stable pairs

---

## Data Formats

### Mentor Data Format (Person C → Database)

```python
{
    'user_id': 'uuid-string',           # Generated UUID
    'name': 'John Doe',
    'email': 'john@example.com',
    'role': 'mentor',
    'expertise_area': 'Machine Learning',
    'expertise_level': 4,               # Integer 1-5
    'max_mentee_capacity': 3,
    'current_mentee_count': 0
}
```

---

### Mentee Data Format (Person C → Database)

```python
{
    'user_id': 'uuid-string',           # Generated UUID
    'name': 'Jane Smith',
    'email': 'jane@example.com',
    'role': 'mentee',
    'main_interest': 'Machine Learning',
    'main_interest_level': 2            # Integer 1-5
}
```

---

### Embedding Format (Person C → Database)

```python
{
    'embedding_id': 'uuid-string',
    'mentor_profile_id': 'uuid-string',  # OR mentee_profile_id (not both)
    'mentee_profile_id': None,           # Mutually exclusive
    'embedding_type': 'combined',        # 'main_interest', 'expertise', or 'combined'
    'embedding_vector': [0.123, -0.456, 0.789, ...],  # 384 floats
}
```

**Critical**: `embedding_vector` must be exactly 384 dimensions (all-MiniLM-L6-v2 model output)

---

### Match Output Format (Person A → Database)

```python
{
    'match_id': 'uuid-string',
    'mentor_id': 'mentor-uuid',
    'mentee_id': 'mentee-uuid',
    'algorithm_name': 'Gale-Shapley',
    'semantic_score': 0.85,
    'expertise_score': 1.0,
    'final_score': 0.88,
    'status': 'pending',
    'created_at': '2026-01-22T12:30:00'
}
```

---

## File Responsibilities

### Person A (Algorithm Lead)
**Files**:
- `claude/mentor_matching_system.py` - Matching algorithm implementation
- `postgres/schema_minimal.sql` - Database schema definition

**Responsibilities**:
1. Design minimal database schema (5 tables)
2. Implement scoring functions (semantic + expertise)
3. Implement preference ranking generation
4. Implement Gale-Shapley matching algorithm
5. Store results in matches table
6. Provide interface documentation for Person B & C

**Deliverables**:
- Working Python class with scoring functions (Day 1)
- Complete matching pipeline (Day 4)
- Documentation of data formats

---

### Person B (Database Administrator)
**Files**:
- `postgres/docker-compose.yml` - Docker configuration
- `postgres/init_db.py` - Database initialization script

**Responsibilities**:
1. Set up PostgreSQL + pgvector in Docker
2. Load schema_minimal.sql into database
3. Verify all tables created correctly
4. Create necessary indexes (including IVFFlat)
5. Provide connection string to Person C & A
6. Monitor database during matching execution

**Deliverables**:
- Running PostgreSQL database (port 5432)
- Connection string: `postgresql://postgres:password123@localhost:5432/mentor_db`
- Verified schema loaded
- pgvector extension enabled

---

### Person C (Data Generator)
**Files**:
- `generate_dummy_data.py` - Dummy data creation script
- `generate_embeddings.py` - Embedding generation using all-MiniLM-L6-v2

**Responsibilities**:
1. Generate 20 mentor profiles
2. Generate 30 mentee profiles
3. Create text descriptions for embedding generation
4. Generate 384-dim embeddings using all-MiniLM-L6-v2
5. Insert users, profiles, and embeddings into database
6. Validate data format matches Person A's requirements

**Deliverables**:
- 20 mentors with available capacity
- 30 mentees
- 50+ embeddings (type='combined') with 384 dimensions
- All data inserted into database

---

## Interface Contracts

### Person C → Person B

**What Person C Needs**:
- Database connection string
- Schema loaded and verified
- Write permissions on all tables

**What Person C Provides**:
- INSERT statements for users, profiles, embeddings
- Validation that data meets schema constraints
- Confirmation of embedding dimensions (384)

**Example Query Person C Runs**:
```sql
INSERT INTO users (user_id, name, email, role) 
VALUES ('uuid-123', 'John Doe', 'john@example.com', 'mentor');

INSERT INTO mentor_profiles (mentor_profile_id, user_id, expertise_area, expertise_level)
VALUES ('uuid-456', 'uuid-123', 'Machine Learning', 4);

INSERT INTO embeddings (embedding_id, mentor_profile_id, embedding_type, embedding_vector)
VALUES ('uuid-789', 'uuid-456', 'combined', '[0.1, 0.2, ..., 0.384]');
```

---

### Person B → Person A

**What Person A Needs**:
- Database connection string
- Confirmation schema loaded
- Access to query all tables

**What Person B Provides**:
- PostgreSQL running on localhost:5432
- Database name: `mentor_db`
- Credentials: postgres/password123
- pgvector extension enabled

**Connection String**:
```
postgresql://postgres:password123@localhost:5432/mentor_db
```

---

### Person A → Person C

**What Person C Needs**:
- Data format specifications
- Required fields for each table
- Embedding dimension (384)
- Embedding type ('combined')

**What Person A Provides**:
- Schema definition (schema_minimal.sql)
- Data format examples (this document)
- Validation queries to test data

**Validation Query Person C Uses**:
```python
from mentor_matching_system import MentorMatchingSystem

matcher = MentorMatchingSystem(DB_CONNECTION)
mentors = matcher.get_available_mentors()
mentees = matcher.get_all_mentees()

print(f"Mentors: {len(mentors)}")  # Should be 20
print(f"Mentees: {len(mentees)}")  # Should be 30
```

---

## Configuration

### Database Connection

**Connection String Format**:
```
postgresql://username:password@host:port/database
```

**Default Values**:
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mentor_db"
DB_USER = "postgres"
DB_PASSWORD = "password123"

# Full connection string
DB_CONNECTION = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

---

### Algorithm Weights

**Scoring Weights**:
```python
SEMANTIC_WEIGHT = 0.8    # 80% of final score
EXPERTISE_WEIGHT = 0.2   # 20% of final score
```

**Expertise Gap Parameters**:
```python
OPTIMAL_GAP_MIN = 2      # Minimum optimal level gap
OPTIMAL_GAP_MAX = 3      # Maximum optimal level gap
OPTIMAL_SCORE = 1.0      # Score for optimal gap
SUBOPTIMAL_SCORE = 0.3   # Score for non-optimal gap
```

**Embedding Configuration**:
```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
EMBEDDING_TYPE = "combined"  # Use for matching
```

---

## Common Queries

### For Person B (Database Setup)

**Check if database exists**:
```sql
SELECT datname FROM pg_database WHERE datname='mentor_db';
```

**Verify pgvector extension**:
```sql
SELECT * FROM pg_extension WHERE extname='vector';
```

**List all tables**:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema='public';
```

**Check table row counts**:
```sql
SELECT 
    'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'mentor_profiles', COUNT(*) FROM mentor_profiles
UNION ALL
SELECT 'mentee_profiles', COUNT(*) FROM mentee_profiles
UNION ALL
SELECT 'embeddings', COUNT(*) FROM embeddings
UNION ALL
SELECT 'matches', COUNT(*) FROM matches;
```

---

### For Person C (Data Validation)

**Verify embedding dimensions**:
```sql
SELECT 
    embedding_type,
    vector_dims(embedding_vector) as dimensions,
    COUNT(*) as count
FROM embeddings
GROUP BY embedding_type, vector_dims(embedding_vector);
```

**Expected output**: All rows show 384 dimensions

**Check mentor capacity**:
```sql
SELECT 
    mentor_profile_id,
    max_mentee_capacity,
    current_mentee_count,
    (max_mentee_capacity - current_mentee_count) as available_slots
FROM mentor_profiles
WHERE current_mentee_count < max_mentee_capacity;
```

**Verify profile completeness**:
```sql
-- Check all mentors have embeddings
SELECT m.mentor_profile_id
FROM mentor_profiles m
LEFT JOIN embeddings e ON m.mentor_profile_id = e.mentor_profile_id
WHERE e.embedding_id IS NULL;
-- Should return 0 rows

-- Check all mentees have embeddings
SELECT me.mentee_profile_id
FROM mentee_profiles me
LEFT JOIN embeddings e ON me.mentee_profile_id = e.mentee_profile_id
WHERE e.embedding_id IS NULL;
-- Should return 0 rows
```

---

### For Person A (Algorithm Testing)

**Test semantic similarity**:
```sql
-- Find most similar mentor for a mentee
SELECT 
    mp.mentor_profile_id,
    mp.expertise_area,
    1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
JOIN mentor_profiles mp ON e_mentor.mentor_profile_id = mp.mentor_profile_id
WHERE e_mentee.mentee_profile_id = 'YOUR_MENTEE_ID'
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
  AND mp.current_mentee_count < mp.max_mentee_capacity
ORDER BY similarity DESC
LIMIT 10;
```

**Check match distribution**:
```sql
SELECT 
    mentor_id,
    COUNT(*) as mentee_count,
    AVG(final_score) as avg_score
FROM matches
WHERE status = 'pending'
GROUP BY mentor_id
ORDER BY mentee_count DESC;
```

**Verify scoring formula**:
```sql
SELECT 
    match_id,
    semantic_score,
    expertise_score,
    final_score,
    (0.8 * semantic_score + 0.2 * expertise_score) as calculated_score,
    ABS(final_score - (0.8 * semantic_score + 0.2 * expertise_score)) as difference
FROM matches
WHERE ABS(final_score - (0.8 * semantic_score + 0.2 * expertise_score)) > 0.001;
-- Should return 0 rows
```

---

## Troubleshooting

### Database Connection Issues

**Problem**: "could not connect to server"
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it
cd postgres/
docker-compose up -d

# Check logs
docker-compose logs postgres
```

---

**Problem**: "database 'mentor_db' does not exist"
```bash
# Create database
docker exec -it postgres_container psql -U postgres -c "CREATE DATABASE mentor_db;"

# Load schema
docker exec -i postgres_container psql -U postgres -d mentor_db < schema_minimal.sql
```

---

**Problem**: "extension 'vector' does not exist"
```bash
# Install pgvector in container
docker exec -it postgres_container psql -U postgres -d mentor_db -c "CREATE EXTENSION vector;"
```

---

### Data Issues

**Problem**: No embeddings found
```sql
-- Check if embeddings table is populated
SELECT COUNT(*) FROM embeddings;

-- Check embedding types
SELECT embedding_type, COUNT(*) FROM embeddings GROUP BY embedding_type;
```

**Solution**: Person C needs to run embedding generation script

---

**Problem**: Wrong embedding dimensions
```sql
-- Check dimensions
SELECT DISTINCT vector_dims(embedding_vector) as dims 
FROM embeddings;
```

**Expected**: 384  
**Solution**: Regenerate embeddings using all-MiniLM-L6-v2 model

---

**Problem**: Semantic similarity always returns 0.0
```sql
-- Check if embeddings exist for both profiles
SELECT 
    (SELECT COUNT(*) FROM embeddings WHERE mentee_profile_id = 'YOUR_MENTEE_ID' AND embedding_type = 'combined') as mentee_embeddings,
    (SELECT COUNT(*) FROM embeddings WHERE mentor_profile_id = 'YOUR_MENTOR_ID' AND embedding_type = 'combined') as mentor_embeddings;
```

**Expected**: Both counts = 1  
**Solution**: Ensure both profiles have 'combined' type embeddings

---

### Algorithm Issues

**Problem**: No matches generated
```python
# Check data availability
matcher = MentorMatchingSystem(DB_CONNECTION)
mentors = matcher.get_available_mentors()
mentees = matcher.get_all_mentees()

print(f"Available mentors: {len(mentors)}")
print(f"Total mentees: {len(mentees)}")
```

**Solution**: Ensure both lists > 0

---

**Problem**: All matches have same score
```sql
SELECT DISTINCT final_score FROM matches;
```

**Solution**: Check if embeddings are diverse (not all identical vectors)

---

## Next Steps

### Day 1 (Complete)
- [x] Create minimal schema
- [x] Implement scoring functions
- [x] Document architecture

### Day 2 (TODO)
- [ ] Person B: Verify database running
- [ ] Person C: Complete data generation
- [ ] Person A: Implement preference rankings
- [ ] Person A: Implement storage functions
- [ ] Team: Integration test with real data

### Day 3 (TODO)
- [ ] Person A: Implement Gale-Shapley algorithm
- [ ] Person A: Test stable matching
- [ ] Team: Validate match quality

### Day 4 (TODO)
- [ ] Person A: Complete main pipeline
- [ ] Team: Full system integration test
- [ ] Team: Generate final results
- [ ] Team: Analyze match statistics
- [ ] Team: Document findings

---

## Summary

### System Components
| Component | Owner | Status | File |
|-----------|-------|--------|------|
| Database Schema | Person A | ✅ Done | postgres/schema_minimal.sql |
| PostgreSQL Setup | Person B | ⏳ In Progress | postgres/docker-compose.yml |
| Dummy Data | Person C | ⏳ In Progress | generate_dummy_data.py |
| Embeddings | Person C | ⏳ In Progress | generate_embeddings.py |
| Scoring Functions | Person A | ✅ Done | claude/mentor_matching_system.py |
| Preference Rankings | Person A | ⏳ TODO | claude/mentor_matching_system.py |
| Gale-Shapley | Person A | ⏳ TODO | claude/mentor_matching_system.py |
| Main Pipeline | Person A | ⏳ TODO | claude/mentor_matching_system.py |

### Data Flow
```
Person C → Generates → Users, Profiles, Embeddings
    ↓
Person B → Provides → Database Connection
    ↓
Person A → Queries → Embeddings
    ↓
Person A → Computes → Similarity Scores
    ↓
Person A → Runs → Gale-Shapley Algorithm
    ↓
Person A → Stores → Matches Table
    ↓
Team → Analyzes → Match Results
```

### Key Metrics
- **Tables**: 5 (users, mentor_profiles, mentee_profiles, embeddings, matches)
- **Views**: 3 (v_available_mentors, v_mentees, v_match_details)
- **Functions**: 1 (get_available_mentors)
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Scoring Formula**: 80% semantic + 20% expertise
- **Optimal Gap**: 2-3 levels
- **Target Matches**: ~25-30 pairs

---

**Document Version**: 1.0  
**Last Updated**: Thursday, January 22, 2026, 12:30 PM +0545  
**Status**: Architecture Complete, Ready for Implementation
