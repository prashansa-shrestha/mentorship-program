from your_matcher_file import MentorMatchingSystem

matcher = MentorMatchingSystem(
    "postgresql://user:password@localhost:5432/mentor_db"
)

# WARNING: Only run after embeddings table has data
matcher.create_ivfflat_indexes(lists=100)
matcher.close()
