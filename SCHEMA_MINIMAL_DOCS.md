# Schema Minimal Documentation

## Overview
Simplified PostgreSQL schema for mentor-mentee matching prototype using pgvector for semantic similarity.

**Model**: all-MiniLM-L6-v2 (384-dimensional embeddings)  
**Tables**: 5 core tables only  
**File**: `postgres/schema_minimal.sql`

---

## Core Tables

### 1. `users`
Basic user identity and role management.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID | Primary key (auto-generated) |
| `name` | VARCHAR(255) | Full name |
| `email` | VARCHAR(255) | Unique email address |
| `role` | VARCHAR(20) | `'mentor'`, `'mentee'`, or `'both'` |
| `created_at` | TIMESTAMP | Registration timestamp |

**Indexes**: `role`, `email`

---

### 2. `mentor_profiles`
Mentor expertise and capacity tracking.

| Column | Type | Description |
|--------|------|-------------|
| `mentor_profile_id` | UUID | Primary key (auto-generated) |
| `user_id` | UUID | FK to users (unique) |
| `expertise_area` | TEXT | Domain expertise (e.g., "Machine Learning") |
| `expertise_level` | INTEGER | 1-5 scale (1=Beginner, 5=Master) |
| `max_mentee_capacity` | INTEGER | Maximum mentees allowed (default: 3) |
| `current_mentee_count` | INTEGER | Current active mentees (default: 0) |
| `created_at` | TIMESTAMP | Profile creation timestamp |

**Constraints**: 
- `current_mentee_count <= max_mentee_capacity`
- `expertise_level BETWEEN 1 AND 5`

**Indexes**: `user_id`, `(current_mentee_count, max_mentee_capacity)`, `(expertise_area, expertise_level)`

---

### 3. `mentee_profiles`
Mentee learning interests.

| Column | Type | Description |
|--------|------|-------------|
| `mentee_profile_id` | UUID | Primary key (auto-generated) |
| `user_id` | UUID | FK to users (unique) |
| `main_interest` | TEXT | Primary learning interest |
| `main_interest_level` | INTEGER | 1-5 scale (1=Novice, 5=Expert) |
| `created_at` | TIMESTAMP | Profile creation timestamp |

**Constraints**: `main_interest_level BETWEEN 1 AND 5`

**Indexes**: `user_id`, `(main_interest, main_interest_level)`

---

### 4. `embeddings` ⭐
Vector embeddings for semantic similarity matching.

| Column | Type | Description |
|--------|------|-------------|
| `embedding_id` | UUID | Primary key (auto-generated) |
| `mentor_profile_id` | UUID | FK to mentor_profiles (nullable) |
| `mentee_profile_id` | UUID | FK to mentee_profiles (nullable) |
| `embedding_type` | VARCHAR(50) | `'main_interest'`, `'expertise'`, or `'combined'` |
| `embedding_vector` | **vector(384)** | 384-dimensional embedding from all-MiniLM-L6-v2 |
| `created_at` | TIMESTAMP | Embedding creation timestamp |

**Critical Constraints**:
- **Mutual exclusivity**: Either `mentor_profile_id` OR `mentee_profile_id` must be set (not both)
- Vector dimension: **384** (not 768)

**Indexes**: 
- `mentor_profile_id`, `mentee_profile_id`, `embedding_type`
- **IVFFlat index** on `embedding_vector` for fast cosine similarity search (100 lists)

---

### 5. `matches`
Final mentor-mentee pairings with scoring.

| Column | Type | Description |
|--------|------|-------------|
| `match_id` | UUID | Primary key (auto-generated) |
| `mentor_id` | UUID | FK to mentor_profiles |
| `mentee_id` | UUID | FK to mentee_profiles |
| `algorithm_name` | VARCHAR(100) | Algorithm that generated match |
| `semantic_score` | FLOAT | Cosine similarity score (0-1) |
| `expertise_score` | FLOAT | Expertise compatibility score (0-1) |
| `final_score` | FLOAT | Combined weighted score (0-1) |
| `status` | VARCHAR(20) | `'pending'`, `'active'`, `'completed'`, `'declined'` |
| `created_at` | TIMESTAMP | Match creation timestamp |

**Scoring Formula**: `final_score = 0.8 × semantic_score + 0.2 × expertise_score`

**Constraints**: 
- Unique `(mentor_id, mentee_id)` pairs
- All scores between 0 and 1

**Indexes**: `mentor_id`, `mentee_id`, `status`, `final_score DESC`, `algorithm_name`

---

## Helper Views

### `v_available_mentors`
Mentors with available capacity.

```sql
SELECT * FROM v_available_mentors;
```

**Returns**: `mentor_profile_id`, `name`, `email`, `expertise_area`, `expertise_level`, `available_slots`

---

### `v_mentees`
All mentees with user details.

```sql
SELECT * FROM v_mentees;
```

**Returns**: `mentee_profile_id`, `name`, `email`, `main_interest`, `main_interest_level`

---

### `v_match_details`
Complete match information with mentor/mentee details.

```sql
SELECT * FROM v_match_details WHERE final_score > 0.7;
```

**Returns**: Match scores, status, mentor name/expertise, mentee name/interest

---

## Helper Functions

### `get_available_mentors()`
Returns mentors with capacity for new matches.

```sql
SELECT * FROM get_available_mentors();
```

**Returns**: TABLE(`mentor_profile_id`, `expertise_area`, `expertise_level`, `available_slots`)

---

## Key Queries

### Find semantic similarity for a mentee
```sql
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

### Check embedding dimensions
```sql
SELECT 
    embedding_type,
    vector_dims(embedding_vector) as dimensions
FROM embeddings
LIMIT 5;
```

**Expected output**: `dimensions = 384`

---

## What's Removed from Original Schema

❌ Personality fields (guidance_style, feedback_preference, etc.)  
❌ MBTI compatibility tables  
❌ Triggers for profile_completeness  
❌ Additional interest fields  
❌ Hobby/CV/LinkedIn fields  
❌ Complex metadata tables (algorithm_configurations, matching_rounds, etc.)  
❌ A/B testing tables  
❌ Ground truth tracking  

---

## Extensions Required

```sql
CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
```

---

## Setup Instructions

```bash
# 1. Start PostgreSQL with pgvector
docker-compose up -d

# 2. Load schema
psql -h localhost -U postgres -d mentor_db -f postgres/schema_minimal.sql

# 3. Verify tables
psql -d mentor_db -c "\dt"

# 4. Verify vector extension
psql -d mentor_db -c "SELECT vector_dims('[1,2,3]'::vector);"
```

---

## Validation

Run these commands to validate schema:

```bash
# Should return 1 match
cat postgres/schema_minimal.sql | grep "vector(384)"

# Should return 5 matches
cat postgres/schema_minimal.sql | grep "CREATE TABLE" | wc -l

# Should complete without errors
psql -d mentor_db -f postgres/schema_minimal.sql
```

---

## For Person B (Database Setup)

**Connection String**:
```
postgresql://postgres:password123@localhost:5432/mentor_db
```

**Your tasks**:
1. Run `docker-compose up -d`
2. Load schema: `psql -f postgres/schema_minimal.sql`
3. Verify tables exist
4. Provide connection string to Person A

---

## For Person C (Data Generation)

**Required data format** (Python dict):

```python
# Mentor format
{
    'user_id': 'uuid-string',
    'name': 'John Doe',
    'email': 'john@example.com',
    'expertise_area': 'Machine Learning',
    'expertise_level': 4,
    'max_mentee_capacity': 3
}

# Mentee format
{
    'user_id': 'uuid-string',
    'name': 'Jane Smith',
    'email': 'jane@example.com',
    'main_interest': 'Machine Learning',
    'main_interest_level': 2
}

# Embedding format
{
    'mentor_profile_id': 'uuid-string',  # OR mentee_profile_id
    'embedding_type': 'combined',
    'embedding_vector': [0.123, -0.456, ...],  # 384 floats
}
```

**Your tasks**:
1. Generate 20 mentors, 30 mentees
2. Generate 384-dim embeddings using all-MiniLM-L6-v2
3. Insert using Person B's connection

---

## Summary

| Metric | Value |
|--------|-------|
| **Tables** | 5 |
| **Views** | 3 |
| **Functions** | 1 |
| **Indexes** | 15+ |
| **Vector Dimension** | 384 |
| **Total Lines** | ~320 |
| **Complexity** | Minimal (prototype-ready) |
