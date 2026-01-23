from mentor_matching_system import MentorMatchingSystem

DB_DSN = "postgresql://postgres:postgres123@127.0.0.1:5433/mentor_db"


print("Using DB_DSN:", DB_DSN)

matcher = MentorMatchingSystem(DB_DSN)

num_matches = matcher.execute_matching(algorithm_name="Gale-Shapley")
print(f"Matching complete: {num_matches} matches created")

matcher.close()
