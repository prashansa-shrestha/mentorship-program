"""
Greedy Matching Algorithm with Capacity Constraints
Matches mentees to multiple mentors based on similarity scores
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict


def greedy_match(
    similarity_matrix: np.ndarray,
    mentor_capacities: Dict[str, int],
    mentee_ids: List[str],
    mentor_ids: List[str],
    mentees_per_mentor: int = 3
) -> List[Dict]:
    """
    Greedy matching algorithm that assigns multiple mentors to each mentee.

    Algorithm:
    1. For each mentee (in order of lowest average score to highest):
       - Find top-k mentors by similarity score
       - Assign up to mentees_per_mentor mentors if they have capacity
       - Track and decrement mentor capacity

    Args:
        similarity_matrix: 2D array of shape (n_mentees, n_mentors) with scores
        mentor_capacities: Dict mapping mentor_id to max capacity
        mentee_ids: List of mentee IDs (length n_mentees)
        mentor_ids: List of mentor IDs (length n_mentors)
        mentees_per_mentor: Number of mentors each mentee should receive (default: 3)

    Returns:
        List[Dict]: Match results with keys:
            - mentee_id: str
            - mentor_id: str
            - score: float
            - priority: int (1=first choice, 2=second choice, etc.)
    """

    n_mentees, n_mentors = similarity_matrix.shape

    # Validate inputs
    assert len(mentee_ids) == n_mentees, "Mentee IDs length mismatch"
    assert len(mentor_ids) == n_mentors, "Mentor IDs length mismatch"

    # Initialize capacity tracking
    current_capacities = mentor_capacities.copy()
    matches = []

    # Calculate average score per mentee (for prioritization)
    # Lower average = harder to match, so prioritize them first
    mentee_avg_scores = similarity_matrix.mean(axis=1)
    mentee_order = np.argsort(mentee_avg_scores)  # Ascending order

    print(f"Starting greedy matching for {n_mentees} mentees and {n_mentors} mentors")
    print(f"Target: {mentees_per_mentor} mentors per mentee")

    # Process each mentee
    for mentee_idx in mentee_order:
        mentee_id = mentee_ids[mentee_idx]
        mentee_scores = similarity_matrix[mentee_idx]

        # Get mentor indices sorted by score (descending)
        mentor_ranking = np.argsort(mentee_scores)[::-1]

        assigned_count = 0

        # Try to assign top mentors
        for rank_position, mentor_idx in enumerate(mentor_ranking):
            mentor_id = mentor_ids[mentor_idx]
            score = mentee_scores[mentor_idx]

            # Check if mentor has capacity
            if current_capacities.get(mentor_id, 0) > 0:
                # Assign match
                matches.append({
                    'mentee_id': mentee_id,
                    'mentor_id': mentor_id,
                    'score': float(score),
                    'priority': assigned_count + 1,
                    'mentor_rank': rank_position + 1  # Which choice this was
                })

                # Update capacity
                current_capacities[mentor_id] -= 1
                assigned_count += 1

                # Stop if mentee has enough mentors
                if assigned_count >= mentees_per_mentor:
                    break

        # Log if mentee didn't get full allocation
        if assigned_count < mentees_per_mentor:
            print(f"  Warning: Mentee {mentee_id[:8]} only got {assigned_count}/{mentees_per_mentor} mentors")

    print(f"\nMatching complete: {len(matches)} total assignments")

    # Calculate statistics
    mentees_matched = len(set(m['mentee_id'] for m in matches))
    avg_score = sum(m['score'] for m in matches) / len(matches) if matches else 0

    print(f"  Mentees matched: {mentees_matched}/{n_mentees}")
    print(f"  Average match score: {avg_score:.3f}")

    # Count mentors per mentee
    mentee_counts = defaultdict(int)
    for match in matches:
        mentee_counts[match['mentee_id']] += 1

    distribution = defaultdict(int)
    for count in mentee_counts.values():
        distribution[count] += 1

    print(f"  Distribution of mentors per mentee:")
    for num_mentors in sorted(distribution.keys()):
        print(f"    {num_mentors} mentors: {distribution[num_mentors]} mentees")

    return matches


def greedy_match_alternative(
    similarity_matrix: np.ndarray,
    mentor_capacities: Dict[str, int],
    mentee_ids: List[str],
    mentor_ids: List[str],
    mentees_per_mentor: int = 3,
    prioritize_high_scores: bool = False
) -> List[Dict]:
    """
    Alternative greedy matching with different prioritization strategy.

    This version processes mentees in order of HIGHEST average score first,
    which can lead to better overall match quality but may leave lower-scoring
    mentees with fewer options.

    Args:
        similarity_matrix: 2D array of shape (n_mentees, n_mentors)
        mentor_capacities: Dict mapping mentor_id to max capacity
        mentee_ids: List of mentee IDs
        mentor_ids: List of mentor IDs
        mentees_per_mentor: Number of mentors per mentee (default: 3)
        prioritize_high_scores: If True, process high-scoring mentees first

    Returns:
        List[Dict]: Match results
    """

    n_mentees, n_mentors = similarity_matrix.shape

    current_capacities = mentor_capacities.copy()
    matches = []

    # Prioritization strategy
    if prioritize_high_scores:
        # High scorers go first (may get better mentors)
        mentee_avg_scores = similarity_matrix.mean(axis=1)
        mentee_order = np.argsort(mentee_avg_scores)[::-1]  # Descending
        print("Strategy: High-scoring mentees first")
    else:
        # Low scorers go first (equity-focused)
        mentee_avg_scores = similarity_matrix.mean(axis=1)
        mentee_order = np.argsort(mentee_avg_scores)
        print("Strategy: Low-scoring mentees first (equity)")

    # Process mentees
    for mentee_idx in mentee_order:
        mentee_id = mentee_ids[mentee_idx]
        mentee_scores = similarity_matrix[mentee_idx]

        # Sort mentors by score
        mentor_ranking = np.argsort(mentee_scores)[::-1]

        assigned = []
        for mentor_idx in mentor_ranking:
            if len(assigned) >= mentees_per_mentor:
                break

            mentor_id = mentor_ids[mentor_idx]

            if current_capacities.get(mentor_id, 0) > 0:
                assigned.append({
                    'mentee_id': mentee_id,
                    'mentor_id': mentor_id,
                    'score': float(mentee_scores[mentor_idx]),
                    'priority': len(assigned) + 1
                })
                current_capacities[mentor_id] -= 1

        matches.extend(assigned)

    print(f"Matched {len(matches)} pairs")
    return matches


# Example usage and test
if __name__ == "__main__":

    # Simulate data
    np.random.seed(42)

    n_mentees = 30
    n_mentors = 20

    # Generate synthetic similarity matrix (values between 0 and 1)
    similarity_matrix = np.random.beta(2, 2, size=(n_mentees, n_mentors))

    # Create IDs
    mentee_ids = [f"mentee_{i:03d}" for i in range(n_mentees)]
    mentor_ids = [f"mentor_{i:02d}" for i in range(n_mentors)]

    # Set mentor capacities (1-4 mentees each)
    mentor_capacities = {
        mentor_id: np.random.randint(1, 5) 
        for mentor_id in mentor_ids
    }

    total_capacity = sum(mentor_capacities.values())
    print(f"Total mentor capacity: {total_capacity} slots")
    print(f"Total mentee demand: {n_mentees * 3} slots (3 mentors each)")
    print(f"Capacity ratio: {total_capacity / (n_mentees * 3):.2f}")
    print()

    # Run matching
    matches = greedy_match(
        similarity_matrix=similarity_matrix,
        mentor_capacities=mentor_capacities,
        mentee_ids=mentee_ids,
        mentor_ids=mentor_ids,
        mentees_per_mentor=3
    )

    # Display sample results
    print("\n=== Sample Matches ===")
    for i, match in enumerate(matches[:10]):
        print(f"{i+1}. {match['mentee_id']} → {match['mentor_id']} "
              f"(score: {match['score']:.3f}, priority: {match['priority']})")

    # Verify capacity constraints
    print("\n=== Capacity Verification ===")
    mentor_usage = defaultdict(int)
    for match in matches:
        mentor_usage[match['mentor_id']] += 1

    violations = 0
    for mentor_id, used in mentor_usage.items():
        max_cap = mentor_capacities[mentor_id]
        if used > max_cap:
            print(f"  ✗ {mentor_id}: {used}/{max_cap} (VIOLATED)")
            violations += 1

    if violations == 0:
        print(f"  ✓ All {len(mentor_usage)} mentors within capacity")

    # Score distribution
    scores = [m['score'] for m in matches]
    print(f"\n=== Score Statistics ===")
    print(f"  Mean: {np.mean(scores):.3f}")
    print(f"  Median: {np.median(scores):.3f}")
    print(f"  Std: {np.std(scores):.3f}")
    print(f"  Range: [{np.min(scores):.3f}, {np.max(scores):.3f}]")
