#!/usr/bin/env python3
"""
Simple production runner for mentor matching system.
Run matching for a specific cohort and save results to database.
"""

import sys
import os
from mentor_matching_system import MentorMatchingSystem

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_production_matching.py <cohort_name>")
        print("Example: python run_production_matching.py 'Spring_2026_Cohort_1'")
        sys.exit(1)

    cohort_name = sys.argv[1]

    # Database configuration - load from environment or config file
    db_config = os.getenv("DATABASE_URL", "postgresql://postgres:password123@localhost:5432/mentorship_db")

    try:
        print(f"🚀 Starting matching for cohort: {cohort_name}")

        # Initialize matcher
        matcher = MentorMatchingSystem(db_config)

        # Generate matches
        matches = matcher.generate_matches()

        if not matches:
            print("❌ No matches generated - check data availability")
            return 1

        print(f"✅ Generated {len(matches)} matches")

        # Save to database
        saved_count = matcher.save_matches_to_db(matches)
        print(f"💾 Saved {saved_count} matches to database")

        # Optional: Add cohort tracking if you implement it
        # matching_round_id = matcher.create_matching_round(cohort_name, matches)

        print(f"🎉 Matching complete for {cohort_name}")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        matcher.close()

if __name__ == "__main__":
    sys.exit(main())