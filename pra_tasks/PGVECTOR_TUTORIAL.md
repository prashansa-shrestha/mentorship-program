# pgvector Tutorial: Semantic Similarity Search for Mentor Matching

## Your Setup

**Table**: `embeddings`
```sql
CREATE TABLE embeddings (
    embedding_id UUID PRIMARY KEY,
    mentor_profile_id UUID,
    mentee_profile_id UUID,
    embedding_type VARCHAR(50),
    embedding_vector vector(384),  -- 384-dimensional vectors
    CONSTRAINT chk_profile_exclusivity CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);
```

**Your data**:
- 20 mentors (rows with `mentor_profile_id` set)
- 30 mentees (rows with `mentee_profile_id` set)
- 384-dimensional vectors from all-MiniLM-L6-v2 model

---

## Understanding pgvector Operators

### The `<=>` Operator (Cosine Distance)

**What it does**: Calculates cosine distance between two vectors

**Formula**: `cosine_distance = 1 - cosine_similarity`

**Range**: 
- `0` = identical vectors (100% similar)
- `2` = completely opposite vectors (0% similar)

**Example**:
```sql
-- If vectors are identical
SELECT '[1,2,3]'::vector <=> '[1,2,3]'::vector;
-- Returns: 0

-- If vectors are opposite
SELECT '[1,0,0]'::vector <=> '[-1,0,0]'::vector;
-- Returns: 2
```

---

### Converting Distance to Similarity

**Similarity Score Formula**:
```sql
similarity = 1 - (vector1 <=> vector2)
```

**Why this works**:
- Distance 0 → Similarity 1.0 (100% similar)
- Distance 1 → Similarity 0.0 (neutral)
- Distance 2 → Similarity -1.0 (opposite)

**Your queries should use**: `1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity`

---

## Task 1: Find Similarity for One Mentee vs All Mentors

### Basic Query (No Filtering)

```sql
-- Find similarity between mentee 'abc-123' and all mentors
SELECT 
    e_mentor.mentor_profile_id,
    e_mentor.embedding_vector <=> e_mentee.embedding_vector as cosine_distance,
    1 - (e_mentor.embedding_vector <=> e_mentee.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
WHERE e_mentee.mentee_profile_id = 'abc-123'  -- Replace with actual UUID
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.mentor_profile_id IS NOT NULL
  AND e_mentor.embedding_type = 'combined';
```

**Output**:
```
mentor_profile_id | cosine_distance | similarity
------------------+-----------------+------------
uuid-mentor-1     | 0.15            | 0.85
uuid-mentor-2     | 0.32            | 0.68
uuid-mentor-3     | 0.21            | 0.79
...
```

---

### With Mentor Profile Details

```sql
-- Include mentor expertise information
SELECT 
    m.mentor_profile_id,
    m.expertise_area,
    m.expertise_level,
    m.max_mentee_capacity,
    m.current_mentee_count,
    (m.max_mentee_capacity - m.current_mentee_count) as available_slots,
    1 - (e_mentor.embedding_vector <=> e_mentee.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
JOIN mentor_profiles m ON e_mentor.mentor_profile_id = m.mentor_profile_id
WHERE e_mentee.mentee_profile_id = 'abc-123'
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
  AND m.current_mentee_count < m.max_mentee_capacity  -- Only available mentors
ORDER BY similarity DESC;
```

---

## Task 2: Get Top 3 Most Similar Mentors

### Simple Top 3

```sql
SELECT 
    e_mentor.mentor_profile_id,
    1 - (e_mentor.embedding_vector <=> e_mentee.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
WHERE e_mentee.mentee_profile_id = 'abc-123'
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.mentor_profile_id IS NOT NULL
  AND e_mentor.embedding_type = 'combined'
ORDER BY similarity DESC
LIMIT 3;
```

**Output**:
```
mentor_profile_id | similarity
------------------+------------
uuid-mentor-5     | 0.92
uuid-mentor-12    | 0.88
uuid-mentor-3     | 0.85
```

---

### Top 3 with Mentor Names and Details

```sql
SELECT 
    m.mentor_profile_id,
    u.name as mentor_name,
    u.email as mentor_email,
    m.expertise_area,
    m.expertise_level,
    (m.max_mentee_capacity - m.current_mentee_count) as available_slots,
    1 - (e_mentor.embedding_vector <=> e_mentee.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
JOIN mentor_profiles m ON e_mentor.mentor_profile_id = m.mentor_profile_id
JOIN users u ON m.user_id = u.user_id
WHERE e_mentee.mentee_profile_id = 'abc-123'
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
  AND m.current_mentee_count < m.max_mentee_capacity
ORDER BY similarity DESC
LIMIT 3;
```

**Output**:
```
mentor_profile_id | mentor_name | mentor_email      | expertise_area    | expertise_level | available_slots | similarity
------------------+-------------+-------------------+-------------------+-----------------+-----------------+------------
uuid-5            | John Doe    | john@example.com  | Machine Learning  | 4               | 2               | 0.92
uuid-12           | Jane Smith  | jane@example.com  | Deep Learning     | 5               | 1               | 0.88
uuid-3            | Bob Johnson | bob@example.com   | Data Science      | 4               | 3               | 0.85
```

---

## Task 3: Calculate ALL Mentee-Mentor Pairs

### Complete Similarity Matrix

```sql
-- Warning: This produces 20 × 30 = 600 rows
SELECT 
    me.mentee_profile_id,
    m.mentor_profile_id,
    1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
FROM mentee_profiles me
CROSS JOIN mentor_profiles m
JOIN embeddings e_mentee ON me.mentee_profile_id = e_mentee.mentee_profile_id
JOIN embeddings e_mentor ON m.mentor_profile_id = e_mentor.mentor_profile_id
WHERE e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
ORDER BY me.mentee_profile_id, similarity DESC;
```

**Output** (600 rows):
```
mentee_profile_id | mentor_profile_id | similarity
------------------+-------------------+------------
mentee-1          | mentor-5          | 0.92
mentee-1          | mentor-3          | 0.88
mentee-1          | mentor-12         | 0.85
...
mentee-2          | mentor-8          | 0.91
mentee-2          | mentor-15         | 0.87
...
```

---

### Similarity Matrix with Names

```sql
SELECT 
    mentee_user.name as mentee_name,
    me.main_interest as mentee_interest,
    me.main_interest_level as mentee_level,
    mentor_user.name as mentor_name,
    m.expertise_area as mentor_expertise,
    m.expertise_level as mentor_level,
    1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
FROM mentee_profiles me
CROSS JOIN mentor_profiles m
JOIN users mentee_user ON me.user_id = mentee_user.user_id
JOIN users mentor_user ON m.user_id = mentor_user.user_id
JOIN embeddings e_mentee ON me.mentee_profile_id = e_mentee.mentee_profile_id
JOIN embeddings e_mentor ON m.mentor_profile_id = e_mentor.mentor_profile_id
WHERE e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
  AND m.current_mentee_count < m.max_mentee_capacity
ORDER BY me.mentee_profile_id, similarity DESC;
```

---

### Filtered: Only Top Match Per Mentee

```sql
-- Get best mentor for each mentee
WITH ranked_matches AS (
    SELECT 
        me.mentee_profile_id,
        m.mentor_profile_id,
        1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity,
        ROW_NUMBER() OVER (PARTITION BY me.mentee_profile_id ORDER BY (1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector)) DESC) as rank
    FROM mentee_profiles me
    CROSS JOIN mentor_profiles m
    JOIN embeddings e_mentee ON me.mentee_profile_id = e_mentee.mentee_profile_id
    JOIN embeddings e_mentor ON m.mentor_profile_id = e_mentor.mentor_profile_id
    WHERE e_mentee.embedding_type = 'combined'
      AND e_mentor.embedding_type = 'combined'
)
SELECT mentee_profile_id, mentor_profile_id, similarity
FROM ranked_matches
WHERE rank = 1;
```

**Output** (30 rows - one per mentee):
```
mentee_profile_id | mentor_profile_id | similarity
------------------+-------------------+------------
mentee-1          | mentor-5          | 0.92
mentee-2          | mentor-8          | 0.91
mentee-3          | mentor-5          | 0.89  -- Same mentor as mentee-1
...
```

---

## pgvector Indexing: How It Works

### Index Types

#### 1. IVFFlat Index (Approximate Nearest Neighbor)

**What it does**: Clusters vectors into groups for faster search

**How it works**:
1. Divides 384-dimensional space into `lists` clusters
2. Assigns each vector to nearest cluster centroid
3. During search: Only checks vectors in nearby clusters

**Creating the index**:
```sql
CREATE INDEX idx_embeddings_vector_cosine 
ON embeddings 
USING ivfflat (embedding_vector vector_cosine_ops) 
WITH (lists = 100);
```

**Parameters**:
- `lists = 100`: Number of clusters (typically sqrt(row_count))
- `vector_cosine_ops`: Use cosine distance metric

---

#### 2. HNSW Index (Better accuracy, more memory)

**Alternative** (if you want better accuracy):
```sql
CREATE INDEX idx_embeddings_vector_hnsw
ON embeddings
USING hnsw (embedding_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**For your prototype**: Stick with IVFFlat (simpler, less memory)

---

### Setting Search Accuracy (IVFFlat)

**The `probes` parameter**: Controls speed vs accuracy trade-off

```sql
-- Check current setting
SHOW ivfflat.probes;

-- Set probes for current session
SET ivfflat.probes = 10;  -- Check 10 clusters during search
```

**Rule of thumb**:
- `probes = 1`: Fastest, least accurate (check 1 cluster)
- `probes = 10`: Balanced (check 10 clusters) - **RECOMMENDED for you**
- `probes = lists`: Exact search, slowest (check all clusters)

**For 20 mentors × 30 mentees**: Use `probes = 10` (good balance)

---

### Query Performance with Index

**Before index** (sequential scan):
```sql
EXPLAIN ANALYZE
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1, embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL
LIMIT 3;
```
**Expected**: ~50-100ms for 20 mentors

**After IVFFlat index**:
```sql
SET ivfflat.probes = 10;

EXPLAIN ANALYZE
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1, embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL
ORDER BY e1.embedding_vector <=> e2.embedding_vector
LIMIT 3;
```
**Expected**: ~5-10ms (10x faster)

---

## Performance Tips for Your Use Case

### 1. Use Index with ORDER BY + LIMIT

**Slow** (no index usage):
```sql
-- Computes ALL similarities, then filters
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL;
```

**Fast** (uses index):
```sql
-- Index finds nearest neighbors directly
SELECT 
    e2.mentor_profile_id,
    1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL
ORDER BY e1.embedding_vector <=> e2.embedding_vector  -- Key: ORDER BY distance
LIMIT 3;  -- Key: LIMIT to trigger index usage
```

**Why**: PostgreSQL optimizer uses index when it sees `ORDER BY distance LIMIT k`

---

### 2. Pre-filter Before Similarity Calculation

**Slow** (computes similarity, then filters):
```sql
SELECT 
    m.mentor_profile_id,
    1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
JOIN mentor_profiles m ON e2.mentor_profile_id = m.mentor_profile_id
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL
  AND m.current_mentee_count < m.max_mentee_capacity  -- Filter AFTER similarity
ORDER BY similarity DESC
LIMIT 3;
```

**Fast** (filters first, then computes):
```sql
-- First get available mentors
WITH available_mentors AS (
    SELECT mentor_profile_id 
    FROM mentor_profiles 
    WHERE current_mentee_count < max_mentee_capacity
)
SELECT 
    e2.mentor_profile_id,
    1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IN (SELECT mentor_profile_id FROM available_mentors)
ORDER BY e1.embedding_vector <=> e2.embedding_vector
LIMIT 3;
```

---

### 3. Batch Queries for Multiple Mentees

**Instead of 30 separate queries**, use LATERAL join:

```sql
-- Get top 3 mentors for ALL mentees in one query
SELECT 
    me.mentee_profile_id,
    top_mentors.mentor_profile_id,
    top_mentors.similarity
FROM mentee_profiles me
CROSS JOIN LATERAL (
    SELECT 
        e_mentor.mentor_profile_id,
        1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
    FROM embeddings e_mentee
    CROSS JOIN embeddings e_mentor
    WHERE e_mentee.mentee_profile_id = me.mentee_profile_id
      AND e_mentee.embedding_type = 'combined'
      AND e_mentor.mentor_profile_id IS NOT NULL
      AND e_mentor.embedding_type = 'combined'
    ORDER BY e_mentee.embedding_vector <=> e_mentor.embedding_vector
    LIMIT 3
) top_mentors
ORDER BY me.mentee_profile_id, top_mentors.similarity DESC;
```

**Output** (90 rows - 3 per mentee):
```
mentee_profile_id | mentor_profile_id | similarity
------------------+-------------------+------------
mentee-1          | mentor-5          | 0.92
mentee-1          | mentor-12         | 0.88
mentee-1          | mentor-3          | 0.85
mentee-2          | mentor-8          | 0.91
mentee-2          | mentor-15         | 0.87
mentee-2          | mentor-5          | 0.84
...
```

**Performance**: ~200ms total vs ~3000ms for 30 separate queries

---

## Your Matching Algorithm Implementation

### Python Function Using pgvector

```python
def compute_semantic_similarity(self, mentee_id: str, mentor_id: str) -> float:
    """Calculate semantic similarity using pgvector cosine similarity."""

    # Set probes for accuracy/speed tradeoff
    self.cursor.execute("SET ivfflat.probes = 10")

    # Query using pgvector <=> operator
    self.cursor.execute("""
        SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
        FROM embeddings e1
        CROSS JOIN embeddings e2
        WHERE e1.mentee_profile_id = %s 
          AND e2.mentor_profile_id = %s
          AND e1.embedding_type = 'combined'
          AND e2.embedding_type = 'combined'
    """, (mentee_id, mentor_id))

    result = self.cursor.fetchone()
    return result['similarity'] if result else 0.0
```

---

### Get Top K Mentors for a Mentee

```python
def get_top_mentors(self, mentee_id: str, k: int = 3) -> List[Dict]:
    """Get top k most similar mentors for a mentee."""

    self.cursor.execute("SET ivfflat.probes = 10")

    self.cursor.execute("""
        SELECT 
            e_mentor.mentor_profile_id,
            m.expertise_area,
            m.expertise_level,
            1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
        FROM embeddings e_mentee
        CROSS JOIN embeddings e_mentor
        JOIN mentor_profiles m ON e_mentor.mentor_profile_id = m.mentor_profile_id
        WHERE e_mentee.mentee_profile_id = %s
          AND e_mentee.embedding_type = 'combined'
          AND e_mentor.embedding_type = 'combined'
          AND m.current_mentee_count < m.max_mentee_capacity
        ORDER BY e_mentee.embedding_vector <=> e_mentor.embedding_vector
        LIMIT %s
    """, (mentee_id, k))

    return self.cursor.fetchall()
```

---

## Complete Example Workflow

### Step 1: Setup Index

```sql
-- Create IVFFlat index (one-time setup)
CREATE INDEX idx_embeddings_vector_cosine 
ON embeddings 
USING ivfflat (embedding_vector vector_cosine_ops) 
WITH (lists = 100);

-- Verify index created
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'embeddings';
```

---

### Step 2: Test Single Query

```sql
-- Set probes
SET ivfflat.probes = 10;

-- Find top 3 mentors for mentee 'abc-123'
SELECT 
    m.mentor_profile_id,
    u.name as mentor_name,
    m.expertise_area,
    1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as similarity
FROM embeddings e_mentee
CROSS JOIN embeddings e_mentor
JOIN mentor_profiles m ON e_mentor.mentor_profile_id = m.mentor_profile_id
JOIN users u ON m.user_id = u.user_id
WHERE e_mentee.mentee_profile_id = 'abc-123'
  AND e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
ORDER BY e_mentee.embedding_vector <=> e_mentor.embedding_vector
LIMIT 3;
```

---

### Step 3: Generate Full Similarity Matrix

```sql
-- For your matching algorithm: compute all pairs
SELECT 
    me.mentee_profile_id,
    m.mentor_profile_id,
    1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as semantic_similarity
FROM mentee_profiles me
CROSS JOIN mentor_profiles m
JOIN embeddings e_mentee ON me.mentee_profile_id = e_mentee.mentee_profile_id
JOIN embeddings e_mentor ON m.mentor_profile_id = e_mentor.mentor_profile_id
WHERE e_mentee.embedding_type = 'combined'
  AND e_mentor.embedding_type = 'combined'
ORDER BY me.mentee_profile_id, semantic_similarity DESC;
```

---

### Step 4: Verify Results

```sql
-- Check similarity score distribution
SELECT 
    COUNT(*) as pair_count,
    MIN(1 - (e1.embedding_vector <=> e2.embedding_vector)) as min_similarity,
    AVG(1 - (e1.embedding_vector <=> e2.embedding_vector)) as avg_similarity,
    MAX(1 - (e1.embedding_vector <=> e2.embedding_vector)) as max_similarity
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id IS NOT NULL
  AND e2.mentor_profile_id IS NOT NULL
  AND e1.embedding_type = 'combined'
  AND e2.embedding_type = 'combined';
```

**Expected output**:
```
pair_count | min_similarity | avg_similarity | max_similarity
-----------+----------------+----------------+----------------
600        | 0.42           | 0.67           | 0.95
```

---

## Performance Benchmarks (Your Scale)

### Expected Query Times

**Without index**:
- Single mentee → all mentors: ~50ms
- All pairs (600): ~15 seconds

**With IVFFlat index** (probes=10):
- Single mentee → top 3 mentors: ~5ms
- All pairs (600): ~3 seconds

**Memory usage**:
- Embeddings table: ~20MB (50 vectors × 384 dims × 4 bytes)
- IVFFlat index: ~5MB

---

## Troubleshooting

### Issue: Index not being used

**Check query plan**:
```sql
EXPLAIN ANALYZE
SELECT 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1, embeddings e2
WHERE e1.mentee_profile_id = 'abc-123'
  AND e2.mentor_profile_id IS NOT NULL
ORDER BY e1.embedding_vector <=> e2.embedding_vector
LIMIT 3;
```

**Look for**: "Index Scan using idx_embeddings_vector_cosine"

**If you see "Seq Scan"**: Add ORDER BY + LIMIT to trigger index

---

### Issue: Similarity scores all ~0.5

**Possible causes**:
1. Embeddings not properly generated
2. All embeddings identical (bad model)

**Check diversity**:
```sql
-- Check if embeddings are diverse
SELECT 
    e1.embedding_id as id1,
    e2.embedding_id as id2,
    e1.embedding_vector <=> e2.embedding_vector as distance
FROM embeddings e1
CROSS JOIN embeddings e2
WHERE e1.embedding_id != e2.embedding_id
LIMIT 10;
```

**Expected**: Varied distances (0.1 to 1.5)

---

### Issue: Wrong dimensions error

**Error**: "different vector dimensions 768 and 384"

**Fix**: Regenerate embeddings with all-MiniLM-L6-v2 (384-dim)

**Verify dimensions**:
```sql
SELECT 
    embedding_type,
    vector_dims(embedding_vector) as dimensions,
    COUNT(*)
FROM embeddings
GROUP BY embedding_type, vector_dims(embedding_vector);
```

**Expected**:
```
embedding_type | dimensions | count
---------------+------------+-------
combined       | 384        | 50
```

---

## Summary

### Key Takeaways

1. **Use `1 - (vec1 <=> vec2)` for similarity** (not raw distance)
2. **Create IVFFlat index** for 10x speedup
3. **Set `ivfflat.probes = 10`** for balanced accuracy
4. **Use ORDER BY + LIMIT** to trigger index usage
5. **For 600 pairs**: Expect ~3 seconds with index

### Your Queries

**Top 3 mentors for one mentee**:
```sql
SET ivfflat.probes = 10;
SELECT mentor_profile_id, 1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM embeddings e1 CROSS JOIN embeddings e2
WHERE e1.mentee_profile_id = ? AND e2.mentor_profile_id IS NOT NULL
ORDER BY e1.embedding_vector <=> e2.embedding_vector LIMIT 3;
```

**All pairs**:
```sql
SELECT me.mentee_profile_id, m.mentor_profile_id,
       1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
FROM mentee_profiles me CROSS JOIN mentor_profiles m
JOIN embeddings e1 ON me.mentee_profile_id = e1.mentee_profile_id
JOIN embeddings e2 ON m.mentor_profile_id = e2.mentor_profile_id
WHERE e1.embedding_type = 'combined' AND e2.embedding_type = 'combined';
```

---

**You're ready to implement semantic similarity search!**
