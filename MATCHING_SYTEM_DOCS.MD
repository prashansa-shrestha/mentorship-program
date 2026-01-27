# mentor_matching_system.py Documentation

## Overview
Python class for mentor-mentee matching using semantic similarity and stable matching algorithms[web:15][web:19].

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
- Stores results in database for analysis[web:15]

---

## Class: `MentorMatchingSystem`

### Initialization

```python
matcher = MentorMatchingSystem(db_connection_string)
