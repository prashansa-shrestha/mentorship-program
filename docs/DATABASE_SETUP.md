Here's a comprehensive documentation file for your project:

## Create DATABASE_SETUP.md

```bash
cd ~/Desktop/Prashansa/project_repositories/mentorship-program
nano DATABASE_SETUP.md
```

Or create it in your editor. Here's the content:

***

```markdown
# Database Setup Guide
**Mentorship Program - PostgreSQL + pgvector Setup**

## Overview
This project uses PostgreSQL with pgvector extension for semantic matching of mentors and mentees using embeddings.

---

## File Structure

### Core Files
```
mentorship-program/
├── mentor_matching_system.py      # Main matching algorithm
├── test_matching.py                # Test script with assertions
├── docker-compose.yml              # PostgreSQL container config
└── postgres/
    ├── schema_minimal.sql          # Database schema definition
    ├── init_db.py                  # Schema initialization script
    ├── populate_minimal_db.py      # Loads dummy data from Excel
    ├── dummy_mentor_data.py        # Generates mentor test data
    └── dummy_mentee_data.py        # Generates mentee test data
```

### What Each File Does

| File | Purpose |
|------|---------|
| `schema_minimal.sql` | Defines tables: users, mentor_profiles, mentee_profiles, embeddings, matches |
| `init_db.py` | Creates tables and indexes from schema_minimal.sql |
| `populate_minimal_db.py` | Reads Excel files and inserts data with embeddings |
| `dummy_mentor_data.py` | Generates `dummy_mentor_responses.xlsx` with 20 mentors |
| `dummy_mentee_data.py` | Generates `dummy_mentee_responses.xlsx` with 30 mentees |
| `mentor_matching_system.py` | Implements matching algorithm (70% semantic + 30% expertise) |
| `test_matching.py` | Runs matching, validates results, saves to database |

---

## Prerequisites

- Docker installed
- Python 3.8+ with venv
- PostgreSQL client (optional, for manual queries)

---

## Setup Instructions

### 1. Start PostgreSQL Container

```bash
cd mentorship-program
docker-compose up -d
```

**Verify it's running:**
```bash
docker ps
# Should show: mentorship_db container on port 5432
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Required packages:**
- psycopg2-binary
- numpy
- pandas
- openpyxl

### 3. Initialize Database Schema

```bash
cd postgres
python init_db.py
```

**Expected output:**
```
✅ Schema initialized successfully
✅ Created tables: users, mentor_profiles, mentee_profiles, embeddings, matches
```

### 4. Generate Dummy Data

```bash
# Still in postgres/ directory
python dummy_mentor_data.py   # Creates dummy_mentor_responses.xlsx
python dummy_mentee_data.py   # Creates dummy_mentee_responses.xlsx
```

**Output:**
- `dummy_mentor_responses.xlsx` - 20 mentors with expertise data
- `dummy_mentee_responses.xlsx` - 30 mentees with learning interests

### 5. Populate Database

```bash
python populate_minimal_db.py
```

**Expected output:**
```
📊 Loading dummy data from Excel files...
✅ Loaded 20 mentors and 30 mentees
📝 Inserting mentors...
✅ Inserted 20 mentors with embeddings
📝 Inserting mentees...
✅ Inserted 30 mentees with embeddings
```

### 6. Run Matching Algorithm

```bash
cd ..  # Back to project root
python test_matching.py
```

**Expected results:**
```
✓ Matching completed: 20 matches generated
✓ All assertions passed!
✓ Saved 20 matches to database
🎉 ALL TESTS PASSED!
```

---

## Database Schema

### Tables

#### 1. `users`
Base user information
- `user_id` (UUID, PK)
- `name`, `email`, `role` (mentor/mentee)

#### 2. `mentor_profiles`
Mentor-specific data
- `mentor_profile_id` (UUID, PK)
- `user_id` (FK to users)
- `expertise_area`, `expertise_level` (1-5)
- `max_mentee_capacity`, `current_mentee_count`

#### 3. `mentee_profiles`
Mentee-specific data
- `mentee_profile_id` (UUID, PK)
- `user_id` (FK to users)
- `main_interest`, `main_interest_level` (1-5)

#### 4. `embeddings`
384-dimensional vectors for semantic matching
- `embedding_id` (UUID, PK)
- `mentor_profile_id` or `mentee_profile_id` (FK)
- `embedding_type` ('combined')
- `embedding_vector` (vector(384))

#### 5. `matches`
Generated mentor-mentee pairs
- `match_id` (UUID, PK)
- `mentor_id`, `mentee_id` (FK)
- `semantic_score`, `expertise_score`, `final_score`
- `status` (pending/accepted/rejected)

---

## Matching Algorithm

### Score Calculation
```
final_score = (0.7 × semantic_similarity) + (0.3 × expertise_match)
```

### Semantic Similarity
- Uses pgvector cosine similarity on embeddings
- Range: [0, 1]

### Expertise Match
- Optimal gap (1-2 levels): 1.0
- Good gap (3 levels): 0.6
- Same level: 0.3
- Other: 0.1

### Constraints
- Each mentee gets exactly 1 mentor
- Mentors respect capacity limits
- Greedy algorithm (highest scores first)

---

## Common Commands

### Access Database
```bash
docker exec -it mentorship_db psql -U postgres -d mentorship_db
```

**Useful queries:**
```sql
-- Count users by role
SELECT role, COUNT(*) FROM users GROUP BY role;

-- View embeddings
SELECT pg_typeof(embedding_vector), COUNT(*) 
FROM embeddings GROUP BY pg_typeof(embedding_vector);

-- View matches with scores
SELECT m.mentor_id, m.mentee_id, m.final_score 
FROM matches m 
ORDER BY m.final_score DESC LIMIT 5;

-- Exit
\q
```

### Reset Database
```bash
# Clear all data
docker exec -it mentorship_db psql -U postgres -d mentorship_db -c "TRUNCATE users CASCADE;"

# Re-populate
cd postgres
python populate_minimal_db.py
```

### Stop Container
```bash
docker-compose down       # Stop (keeps data)
docker-compose down -v    # Stop and delete all data
```

---

## Troubleshooting

### Issue: "No such container: postgres"
**Solution:** Container name is `mentorship_db` or `mentorship-db`
```bash
docker ps  # Check actual name
docker exec -it mentorship_db psql ...
```

### Issue: "Port 5432 already in use"
**Solution:** Another PostgreSQL is running
```bash
docker stop $(docker ps -q --filter ancestor=pgvector/pgvector:pg17)
docker-compose up -d
```

### Issue: Embeddings are strings (dtype errors)
**Solution:** 
1. Check pgvector extension: `SELECT * FROM pg_extension WHERE extname='vector';`
2. Verify schema: `\d embeddings` (should show `vector(384)`)
3. Re-run populate script with `::vector` cast

### Issue: Semantic scores are all 0.0
**Solution:** Embeddings not parsed correctly
- Check `mentor_matching_system.py` has `json.loads()` parsing
- Verify embeddings are numpy arrays, not strings

### Issue: "duplicate key violates unique constraint"
**Solution:** Matches already exist
```bash
docker exec -it mentorship_db psql -U postgres -d mentorship_db -c "TRUNCATE matches;"
python test_matching.py
```

---

## Database Connection String

Default: `postgresql://postgres:password123@localhost:5432/mentorship_db`

Change in:
- `init_db.py`
- `populate_minimal_db.py`
- `mentor_matching_system.py`
- `test_matching.py`

Or use environment variables (recommended for production).

---

## Next Steps

1. Replace dummy data with real Google Form responses
2. Implement real embedding generation (sentence-transformers)
3. Add API endpoints for frontend
4. Implement match acceptance/rejection workflow
5. Add email notifications

---

## Credits

**Database:** PostgreSQL 17 with pgvector extension  
**Matching Algorithm:** Greedy capacity-constrained with semantic + expertise scoring  
**Generated:** January 2026
```

***

## Save and Commit

```bash
git add DATABASE_SETUP.md
git commit -m "Add comprehensive database setup documentation"
git push
```

This documentation covers everything someone needs to set up and understand your database system!