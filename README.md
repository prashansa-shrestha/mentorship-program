## VectorBridge: Mentorship Matching System

***

## Overview

This project is a **mentor–mentee matching system** that automatically pairs mentees with suitable mentors using **semantic similarity**, **expertise levels**, and **learning preferences** stored in a PostgreSQL database with **pgvector** for vector similarity.

The system is designed for the Hack-A-Week 2026 mentorship program and currently runs on **Docker + PostgreSQL + Python** with dummy data for 20 mentors and 30 mentees.

***

## Architecture

### High-Level Flow

1. **Data collection**  
   - Google Forms collect mentor and mentee responses (interests, expertise, preferences).
   - For development, Person C generates **dummy mentor and mentee datasets** in Python and exports them to Excel.

2. **Database layer (Person B)**  
   - PostgreSQL 16 runs in Docker with the **pgvector extension** enabled for 384‑dimensional vectors.
   - A minimal schema stores users, mentor profiles, mentee profiles, embeddings, and matches. 

3. **Matching layer (Person A)**  
   - Python code loads embeddings from the database.  
   - Cosine similarity and expertise gap are combined into a final score.  
   - A capacity‑aware matching algorithm assigns each mentee to 1–3 mentors.

4. **Output**  
   - Matches are written back into the database and can be exported for organizers as CSV or reports. 

***

## Project Structure

A typical repository layout:

```text
mentorship-program/
├── claude/
│   └── mentor_matching_system.py      # Matching system (Person A) [conversation_history:73]
├── datasets/                          # Real data (future)
├── postgres/                          # Database & data scripts (Person B & C)
│   ├── docker-compose.yml             # PostgreSQL + pgvector container
│   ├── schema_minimal.sql             # 5-table schema
│   ├── init_db.py                     # Create tables & extensions
│   ├── populate_db.py                 # Insert dummy mentors/mentees + embeddings
│   ├── dummy_mentor_data.py           # Generate dummy mentor data (Person C)
│   └── dummy_mentee_data.py           # Generate dummy mentee data (Person C)
├── src/
│   ├── preprocessor.py                # Data cleaning / feature prep
│   ├── embedder.py                    # Embedding utilities
│   ├── similarity_engine.py           # Similarity helpers
│   ├── expertise_matcher.py           # Score based on skill gaps
│   └── match_generator.py             # Match orchestration
├── run_matching.py                    # CLI entrypoint to run matching
├── SCHEMA_MINIMAL_DOCS.md             # Schema documentation
└── README.md                          # This file
```

(Names may vary slightly; structure reflects the current project described so far.) 
***

## Features

- **Semantic matching** using 384‑dimensional embeddings compatible with `all-MiniLM-L6-v2`.
- **Multi-factor scoring**:
  - Interest / expertise semantic similarity.
  - Expertise level gap between mentor and mentee.
  - Potential for learning preferences (guidance style, feedback, etc.) from form responses.
- **Capacity-aware assignment**:
  - Each mentor has a maximum mentee capacity (1–4).
  - Each mentee can receive multiple mentors (e.g., top 3 matches). 
- **PostgreSQL + pgvector backend** running in Docker for easy setup and vector similarity queries.
- **Dummy data generators** to allow full end‑to‑end testing without real responses yet.

***

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker Desktop** (for PostgreSQL in a container)
- A shell (PowerShell, bash, etc.)

### 1. Clone the project

```bash
git clone <your-repo-url> mentorship-program
cd mentorship-program
```

### 2. Set up Python environment

```bash
python -m venv .venv
# Windows
. .venv/Scripts/activate
# Linux/macOS
# source .venv/bin/activate

pip install --upgrade pip
pip install psycopg2-binary numpy pandas sentence-transformers openpyxl
```

These packages cover database access, numeric operations, basic ML embeddings, and Excel handling.

### 3. Start PostgreSQL (Docker)

From the project root:

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container with pgvector enabled and the `mentor_db` database created.

You can verify it with:

```bash
docker ps         # container should be running
```

### 4. Initialize the schema

From the project root:

```bash
cd postgres
python init_db.py
```

This script:

- Connects to `mentor_db`.
- Ensures `uuid-ossp` and `vector` extensions exist.
- Executes `schema_minimal.sql` to create the tables. 

### 5. Generate dummy data

Still in `postgres/`:

```bash
python dummy_mentor_data.py   # Creates dummy_mentor_responses.xlsx
python dummy_mentee_data.py   # Creates dummy_mentee_responses.xlsx
```

These scripts generate realistic fake mentors and mentees matching your Google Form fields (names, roll numbers, interests, expertise levels, preferences).

### 6. Populate the database

```bash
python populate_db.py
```

This script typically:

- Reads dummy mentor and mentee records from the generators.  
- Inserts users into `users`, then corresponding profiles into `mentor_profiles` and `mentee_profiles`.  
- Calls the embedding generator (`generate_realistic_embedding`) to create 384‑dim vectors for each person and stores them in the `embeddings` table.

You can confirm it worked by connecting to the database and checking row counts:

```bash
docker exec -it mentorship-db psql -U postgres -d mentor_db

SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM mentor_profiles;
SELECT COUNT(*) FROM mentee_profiles;
SELECT COUNT(*) FROM embeddings;
```

***

## Running the Matcher

Once the database has data and embeddings:

### 1. Configure connection

The matching system expects a PostgreSQL connection string; for example in `run_matching.py`:

```python
from claude.mentor_matching_system import MentorMatchingSystem

matcher = MentorMatchingSystem(
    "postgresql://postgres:<password>@localhost:5432/mentor_db"
)

num_matches = matcher.execute_matching(algorithm_name="Gale-Shapley")
print(f"Matching complete: {num_matches} matches created")
```

The `MentorMatchingSystem` class is responsible for: 

- Connecting to the DB.  
- Loading mentor and mentee profiles with their embeddings.  
- Calculating similarity scores and expertise scores.  
- Running the actual matching algorithm (e.g., greedy or Gale–Shapley).  
- Writing matches into the `matches` table.

### 2. Run matching

From the project root:

```bash
python run_matching.py
```

When the algorithm is fully implemented, this will produce real matches and log how many were created. 


***

## Data Model (Minimal Schema)

The minimal schema typically includes: 

- `users`  
  - `user_id` (UUID primary key)  
  - `name`, `email`, `role` ("mentor" or "mentee")  
- `mentor_profiles`  
  - `mentor_profile_id`, `user_id`  
  - `expertise_area`, `expertise_level` (1–5)  
  - `max_mentee_capacity`, `current_mentee_count`  
- `mentee_profiles`  
  - `mentee_profile_id`, `user_id`  
  - `main_interest`, `main_interest_level` (1–5)  
- `embeddings`  
  - `embedding_id`, `mentor_profile_id` or `mentee_profile_id`  
  - `embedding_vector` (vector(384))  
  - `embedding_type`, `created_at`  
- `matches`  
  - `match_id`  
  - `mentor_id`, `mentee_id`  
  - `semantic_score`, `expertise_score`, `final_score`  
  - `matched_at`

This design keeps embeddings and matches separate from the core profile tables while allowing flexible similarity queries via pgvector.

***

## Matching Logic (Conceptual)

The matching algorithm usually follows these steps: 

1. Load all mentors and mentees from the database with:
   - Embeddings.
   - Expertise/interest levels.
   - Capacity information.

2. For each mentee–mentor pair:
   - Compute cosine similarity between embeddings (semantic score).  
   - Compute expertise gap score (prefer mentor level 1–2 levels above mentee).  

3. Combine scores:
   \[
   final\_score = 0.7 \times semantic\_score + 0.3 \times expertise\_score
   \]
   (weights can be tuned later).

4. Apply a capacity‑aware assignment strategy:
   - Sort potential mentors by score for each mentee.  
   - Assign top mentors until mentee has enough mentors or mentors reach capacity.

5. Save the final matches into the `matches` table.

This end‑to‑end process turns form responses into ranked mentor assignments using vector similarity.

***

## Development Workflow

A typical development loop:

1. **Update data generation** (Person C)  
   - Modify dummy generators if Google Form changes.  
   - Regenerate Excel and repopulate DB.

2. **Update schema / DB utilities** (Person B)  
   - Change schema if new fields are needed.  
   - Re-run `init_db.py` and `populate_db.py`. 

3. **Update matching logic** (Person A)  
   - Adjust scoring functions and matching strategy.  
   - Run `run_matching.py` to test new behavior. 
   

***

## Testing

Some suggested checks:

- **Data sanity**  
  - No duplicate emails.  
  - Expertise levels within expected ranges (mentors 3–5, mentees 1–3).  
  - Unique campus roll numbers.

- **Embedding validation**  
  - Length exactly 384.  
  - Norm close to 1.0 (normalized vectors).

- **Database validation**  
  - Foreign keys consistent.  
  - Embeddings exist for all profiles.

- **Matching validation**  
  - Each mentee has at least one mentor.  
  - No mentor exceeds capacity. 

These tests can be automated with small Python scripts in the `postgres/` or `src/` directories.

***

## Roadmap

Planned improvements:

- Replace random dummy embeddings with **real text embeddings** from `sentence-transformers` once real data is available.
- Add additional scoring factors:
  - Hobbies / MBTI‑like personality compatibility.
  - Learning/feedback style alignment from survey questions.
- Build a simple UI or dashboard for:
  - Inspecting matches.
  - Overriding or manually adjusting pairings.
  - Exporting final assignments.

***

## Credits

- **Hack-A-Week 2026 mentorship organizing team.**  
- **Person A** – matching algorithm & system design.
- **Person B** – database, schema, Docker, and population scripts.
- **Person C** – data generation, embeddings, and documentation.

***
