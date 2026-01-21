from your_matcher_file import MentorMatchingSystem

matcher = MentorMatchingSystem(
    "postgresql://user:password@localhost:5432/mentor_db"
)

matching_round_id = matcher.execute_matching_round("January_2026_Cohort_1")
print(f"Matching complete: {matching_round_id}")

matcher.close()
