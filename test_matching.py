"""
Test Script for Mentor Matching System
Tests matching algorithm, validates results, and saves to database
"""

import sys
from collections import defaultdict, Counter
import numpy as np
from typing import Dict, List

# Import the matching system
from mentor_matching_system import MentorMatchingSystem


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def calculate_statistics(matches: List[Dict]) -> Dict:
    """Calculate aggregate statistics from matches."""
    if not matches:
        return {}

    semantic_scores = [m['semantic_score'] for m in matches]
    expertise_scores = [m['expertise_score'] for m in matches]
    final_scores = [m['final_score'] for m in matches]

    return {
        'total_matches': len(matches),
        'semantic_avg': np.mean(semantic_scores),
        'semantic_std': np.std(semantic_scores),
        'semantic_min': np.min(semantic_scores),
        'semantic_max': np.max(semantic_scores),
        'expertise_avg': np.mean(expertise_scores),
        'expertise_std': np.std(expertise_scores),
        'expertise_min': np.min(expertise_scores),
        'expertise_max': np.max(expertise_scores),
        'final_avg': np.mean(final_scores),
        'final_std': np.std(final_scores),
        'final_min': np.min(final_scores),
        'final_max': np.max(final_scores)
    }


def analyze_capacity_utilization(matches: List[Dict], matcher: MentorMatchingSystem) -> Dict:
    """Analyze mentor capacity utilization."""
    # Get all mentors
    mentors = matcher.get_all_mentors()

    # Count matches per mentor
    mentor_match_counts = Counter(m['mentor_id'] for m in matches)

    # Build capacity analysis
    at_capacity = 0
    under_capacity = 0
    over_capacity = 0

    mentor_stats = []

    for mentor in mentors:
        mentor_id = mentor['mentor_profile_id']
        max_capacity = mentor['max_mentee_capacity']
        current_count = mentor['current_mentee_count']
        new_matches = mentor_match_counts.get(mentor_id, 0)
        total_assigned = current_count + new_matches

        mentor_stats.append({
            'mentor_id': mentor_id,
            'max_capacity': max_capacity,
            'current_count': current_count,
            'new_matches': new_matches,
            'total_assigned': total_assigned,
            'remaining': max_capacity - total_assigned
        })

        if total_assigned == max_capacity:
            at_capacity += 1
        elif total_assigned < max_capacity:
            under_capacity += 1
        else:
            over_capacity += 1

    return {
        'at_capacity': at_capacity,
        'under_capacity': under_capacity,
        'over_capacity': over_capacity,
        'total_mentors': len(mentors),
        'mentor_details': mentor_stats
    }


def analyze_mentee_coverage(matches: List[Dict], matcher: MentorMatchingSystem) -> Dict:
    """Analyze how many mentors each mentee received."""
    # Get all mentees
    mentees = matcher.get_all_mentees()

    # Count matches per mentee
    mentee_match_counts = Counter(m['mentee_id'] for m in matches)

    # Categorize mentees
    full_coverage = []  # 3+ mentors
    partial_coverage = []  # 1-2 mentors
    no_coverage = []  # 0 mentors

    for mentee in mentees:
        mentee_id = mentee['mentee_profile_id']
        match_count = mentee_match_counts.get(mentee_id, 0)

        if match_count >= 3:
            full_coverage.append((mentee_id, match_count))
        elif match_count > 0:
            partial_coverage.append((mentee_id, match_count))
        else:
            no_coverage.append(mentee_id)

    return {
        'full_coverage': full_coverage,
        'partial_coverage': partial_coverage,
        'no_coverage': no_coverage,
        'total_mentees': len(mentees)
    }


def verify_database_save(matcher: MentorMatchingSystem, expected_count: int) -> bool:
    """Verify matches were saved correctly to database."""
    try:
        matcher.cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE created_at > NOW() - INTERVAL '5 minutes'
        """)
        result = matcher.cursor.fetchone()
        actual_count = result['count']

        if actual_count == expected_count:
            print(f"  ✓ Verification passed: {actual_count} matches in database")
            return True
        else:
            print(f"  ✗ Verification failed: Expected {expected_count}, found {actual_count}")
            return False
    except Exception as e:
        print(f"  ✗ Verification error: {e}")
        return False


def run_assertions(matches: List[Dict], stats: Dict, capacity_analysis: Dict):
    """Run validation assertions."""
    print_section("Running Assertions")

    try:
        # Assertion 1: Matches were generated
        assert len(matches) > 0, "No matches generated"
        print("  ✓ Assertion 1: Matches generated")

        # Assertion 2: All scores are valid (0-1 range)
        for match in matches:
            assert 0 <= match['semantic_score'] <= 1, f"Invalid semantic score: {match['semantic_score']}"
            assert 0 <= match['expertise_score'] <= 1, f"Invalid expertise score: {match['expertise_score']}"
            assert 0 <= match['final_score'] <= 1, f"Invalid final score: {match['final_score']}"
        print("  ✓ Assertion 2: All scores in valid range [0, 1]")

        # Assertion 3: Final score calculation is correct
        for match in matches:
            expected_final = (0.7 * match['semantic_score']) + (0.3 * match['expertise_score'])
            assert abs(match['final_score'] - expected_final) < 0.001,                 f"Final score mismatch: {match['final_score']} vs {expected_final}"
        print("  ✓ Assertion 3: Final score calculation correct (70/30 split)")

        # Assertion 4: No capacity violations
        assert capacity_analysis['over_capacity'] == 0,             f"{capacity_analysis['over_capacity']} mentors over capacity"
        print("  ✓ Assertion 4: No capacity violations")

        # Assertion 5: Statistics are reasonable
        assert stats['final_avg'] > 0, "Average final score is zero"
        assert stats['final_avg'] <= 1, "Average final score exceeds 1"
        print("  ✓ Assertion 5: Statistics are reasonable")

        # Assertion 6: All matches have valid IDs
        for match in matches:
            assert match['mentee_id'], "Missing mentee_id"
            assert match['mentor_id'], "Missing mentor_id"
        print("  ✓ Assertion 6: All matches have valid IDs")

        print("\n  ✅ All assertions passed!")
        return True

    except AssertionError as e:
        print(f"\n  ❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n  ❌ Unexpected error: {e}")
        return False


def main():
    """Main test execution."""

    # Database configuration
    DB_CONFIG = "postgresql://postgres:password123@localhost:5432/mentor_db"

    print_section("Initializing Mentor Matching System")

    try:
        # Initialize system
        matcher = MentorMatchingSystem(DB_CONFIG)
        print("  ✓ System initialized successfully")

    except Exception as e:
        print(f"  ✗ Failed to initialize system: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials are correct")
        print("  3. Database schema is set up")
        sys.exit(1)

    # Run matching algorithm
    print_section("Running Matching Algorithm")

    try:
        matches = matcher.generate_matches()
        print(f"  ✓ Matching completed: {len(matches)} matches generated")

        if not matches:
            print("  ⚠ No matches generated - check data availability")
            matcher.close()
            sys.exit(0)

    except Exception as e:
        print(f"  ✗ Matching failed: {e}")
        matcher.close()
        sys.exit(1)

    # Calculate statistics
    print_section("Match Statistics")

    stats = calculate_statistics(matches)

    print(f"\n  Total Matches: {stats['total_matches']}")
    print(f"\n  Semantic Similarity Scores:")
    print(f"    Average:  {stats['semantic_avg']:.4f} ± {stats['semantic_std']:.4f}")
    print(f"    Range:    [{stats['semantic_min']:.4f}, {stats['semantic_max']:.4f}]")

    print(f"\n  Expertise Match Scores:")
    print(f"    Average:  {stats['expertise_avg']:.4f} ± {stats['expertise_std']:.4f}")
    print(f"    Range:    [{stats['expertise_min']:.4f}, {stats['expertise_max']:.4f}]")

    print(f"\n  Final Combined Scores:")
    print(f"    Average:  {stats['final_avg']:.4f} ± {stats['final_std']:.4f}")
    print(f"    Range:    [{stats['final_min']:.4f}, {stats['final_max']:.4f}]")

    # Analyze capacity utilization
    print_section("Capacity Utilization")

    capacity_analysis = analyze_capacity_utilization(matches, matcher)

    total = capacity_analysis['total_mentors']
    at_cap = capacity_analysis['at_capacity']
    under_cap = capacity_analysis['under_capacity']
    over_cap = capacity_analysis['over_capacity']

    print(f"\n  Total Mentors: {total}")
    print(f"    At capacity:    {at_cap} ({at_cap/total*100:.1f}%)")
    print(f"    Under capacity: {under_cap} ({under_cap/total*100:.1f}%)")
    print(f"    Over capacity:  {over_cap} ({over_cap/total*100:.1f}%)")

    if over_cap > 0:
        print("\n  ⚠ WARNING: Some mentors are over capacity!")

    # Show top/bottom utilized mentors
    sorted_mentors = sorted(
        capacity_analysis['mentor_details'],
        key=lambda x: x['new_matches'],
        reverse=True
    )

    print(f"\n  Top 5 Most Utilized Mentors:")
    for mentor in sorted_mentors[:5]:
        print(f"    {mentor['mentor_id'][:16]}: "
              f"{mentor['new_matches']} new matches "
              f"({mentor['total_assigned']}/{mentor['max_capacity']} total)")

    # Analyze mentee coverage
    print_section("Mentee Coverage Analysis")

    coverage = analyze_mentee_coverage(matches, matcher)

    print(f"\n  Total Mentees: {coverage['total_mentees']}")
    print(f"    Full coverage (3+ mentors):  {len(coverage['full_coverage'])}")
    print(f"    Partial coverage (1-2):      {len(coverage['partial_coverage'])}")
    print(f"    No coverage (0):             {len(coverage['no_coverage'])}")

    if coverage['partial_coverage']:
        print(f"\n  ⚠ Mentees with < 3 mentors:")
        for mentee_id, count in coverage['partial_coverage']:
            print(f"    {mentee_id[:16]}: {count} mentor(s)")

    if coverage['no_coverage']:
        print(f"\n  ⚠ Unmatched mentees:")
        for mentee_id in coverage['no_coverage'][:5]:  # Show first 5
            print(f"    {mentee_id[:16]}")
        if len(coverage['no_coverage']) > 5:
            print(f"    ... and {len(coverage['no_coverage']) - 5} more")

    # Run assertions
    assertions_passed = run_assertions(matches, stats, capacity_analysis)

    # Save to database
    print_section("Saving Matches to Database")

    try:
        saved_count = matcher.save_matches_to_db(matches)
        print(f"  ✓ Saved {saved_count} matches to database")

        # Verify save
        print("\n  Verifying database save...")
        verification_passed = verify_database_save(matcher, saved_count)

    except Exception as e:
        print(f"  ✗ Failed to save matches: {e}")
        verification_passed = False

    # Final summary
    print_section("Test Summary")

    print(f"\n  Matching: {'✓ PASSED' if len(matches) > 0 else '✗ FAILED'}")
    print(f"  Assertions: {'✓ PASSED' if assertions_passed else '✗ FAILED'}")
    print(f"  Database Save: {'✓ PASSED' if verification_passed else '✗ FAILED'}")

    overall_success = len(matches) > 0 and assertions_passed and verification_passed

    if overall_success:
        print("\n  🎉 ALL TESTS PASSED!")
    else:
        print("\n  ⚠ SOME TESTS FAILED - Review output above")

    # Cleanup
    matcher.close()

    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
