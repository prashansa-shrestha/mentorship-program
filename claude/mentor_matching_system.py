"""
Mentor Matching System - Simplified Algorithm Skeleton
Day 1 Implementation - Clear structure with TODOs for Days 2-4
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Tuple, Optional
import uuid
from datetime import datetime


class MentorMatchingSystem:
    """
    Simplified mentor-mentee matching system using:
    - Semantic similarity (pgvector cosine similarity)
    - Expertise matching (2-3 level gap scoring)
    - Weighted combination (80% semantic + 20% expertise)
    """

    def __init__(self, db_connection_string: str):
        """
        Initialize database connection.

        Args:
            db_connection_string: PostgreSQL connection string
                Format: "postgresql://user:password@host:port/database"
        """
        try:
            self.conn = psycopg2.connect(db_connection_string)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise

    # =====================================================
    # SCORING FUNCTIONS - IMPLEMENTED (Day 1)
    # =====================================================

    def compute_semantic_similarity(self, mentee_id: str, mentor_id: str) -> float:
        """
        Calculate semantic similarity using pgvector cosine similarity.

        Args:
            mentee_id: UUID of mentee profile
            mentor_id: UUID of mentor profile

        Returns:
            float: Similarity score between 0 and 1 (1 = identical)
        """
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

    def compute_expertise_match(self, mentee_id: str, mentor_id: str) -> float:
        """
        Calculate expertise level compatibility.

        Scoring logic:
        - Gap of 2-3 levels: score = 1.0 (optimal)
        - All other gaps: score = 0.3 (suboptimal)

        Args:
            mentee_id: UUID of mentee profile
            mentor_id: UUID of mentor profile

        Returns:
            float: Expertise match score (0.3 or 1.0)
        """
        self.cursor.execute("""
            SELECT 
                me.main_interest_level as mentee_level,
                m.expertise_level as mentor_level
            FROM mentee_profiles me
            CROSS JOIN mentor_profiles m
            WHERE me.mentee_profile_id = %s 
              AND m.mentor_profile_id = %s
        """, (mentee_id, mentor_id))

        result = self.cursor.fetchone()
        if not result:
            return 0.0

        level_gap = result['mentor_level'] - result['mentee_level']

        # High score ONLY for 2-3 level gap
        if 2 <= level_gap <= 3:
            return 1.0
        else:
            return 0.3

    def compute_combined_score(self, mentee_id: str, mentor_id: str) -> Dict:
        """
        Calculate final weighted compatibility score.

        Formula: final_score = 0.8 × semantic_similarity + 0.2 × expertise_match

        Args:
            mentee_id: UUID of mentee profile
            mentor_id: UUID of mentor profile

        Returns:
            Dict with keys:
                - semantic_score: float
                - expertise_score: float
                - final_score: float
        """
        semantic_score = self.compute_semantic_similarity(mentee_id, mentor_id)
        expertise_score = self.compute_expertise_match(mentee_id, mentor_id)

        # Weighted combination: 80% semantic + 20% expertise
        final_score = (0.8 * semantic_score) + (0.2 * expertise_score)

        return {
            'semantic_score': semantic_score,
            'expertise_score': expertise_score,
            'final_score': final_score
        }

    # =====================================================
    # PREFERENCE RANKING - SKELETON (TODO: Day 2)
    # =====================================================

    def generate_preference_rankings(self) -> Tuple[Dict, Dict, Dict]:
        """
        Generate preference rankings for all mentees and mentors.

        TODO (Day 2):
        1. Fetch all active mentees from mentee_profiles
        2. Fetch all available mentors (current_mentee_count < max_mentee_capacity)
        3. For each mentee:
           - Compute combined_score with every available mentor
           - Sort mentors by final_score (descending)
           - Store as mentee_preferences[mentee_id] = [(mentor_id, score), ...]
        4. For each mentor:
           - Compute combined_score with every mentee
           - Sort mentees by final_score (descending)
           - Store as mentor_preferences[mentor_id] = [(mentee_id, score), ...]
        5. Create score_matrix[mentee_id][mentor_id] = final_score

        Returns:
            Tuple[Dict, Dict, Dict]: (mentee_preferences, mentor_preferences, score_matrix)
                - mentee_preferences: {mentee_id: [(mentor_id, score), ...]}
                - mentor_preferences: {mentor_id: [(mentee_id, score), ...]}
                - score_matrix: {mentee_id: {mentor_id: score}}
        """
        # TODO: Implement on Day 2
        mentee_preferences = {}
        mentor_preferences = {}
        score_matrix = {}

        # PLACEHOLDER: Fetch mentees
        # self.cursor.execute("SELECT mentee_profile_id FROM mentee_profiles")
        # mentees = self.cursor.fetchall()

        # PLACEHOLDER: Fetch available mentors
        # self.cursor.execute("""
        #     SELECT mentor_profile_id 
        #     FROM mentor_profiles 
        #     WHERE current_mentee_count < max_mentee_capacity
        # """)
        # mentors = self.cursor.fetchall()

        # PLACEHOLDER: Generate rankings
        # for mentee in mentees:
        #     scores = []
        #     for mentor in mentors:
        #         score_data = self.compute_combined_score(mentee_id, mentor_id)
        #         scores.append((mentor_id, score_data['final_score']))
        #     scores.sort(key=lambda x: x[1], reverse=True)
        #     mentee_preferences[mentee_id] = scores

        return mentee_preferences, mentor_preferences, score_matrix

    # =====================================================
    # GALE-SHAPLEY MATCHING - PLACEHOLDER (TODO: Day 3)
    # =====================================================

    def gale_shapley_matching(
        self, 
        mentee_preferences: Dict,
        mentor_preferences: Dict,
        mentor_capacities: Dict
    ) -> List[Tuple[str, str]]:
        """
        Implement Gale-Shapley stable matching algorithm with capacity constraints.

        TODO (Day 3):
        1. Initialize free_mentees list with all mentees
        2. Initialize mentor_matches dict: {mentor_id: [list of matched mentees]}
        3. Initialize mentee_matches dict: {mentee_id: mentor_id or None}
        4. While free_mentees is not empty:
           a. Pop a mentee from free_mentees
           b. Get mentee's next preferred mentor (not yet proposed to)
           c. If mentor has capacity:
              - Accept proposal
              - Add mentee to mentor_matches[mentor_id]
           d. If mentor is at capacity:
              - Compare with least preferred current match
              - If mentee is more preferred, replace least preferred
              - Otherwise reject mentee (add back to free_mentees)
        5. Return list of (mentee_id, mentor_id) pairings

        Args:
            mentee_preferences: {mentee_id: [(mentor_id, score), ...]}
            mentor_preferences: {mentor_id: [(mentee_id, score), ...]}
            mentor_capacities: {mentor_id: max_capacity}

        Returns:
            List[Tuple[str, str]]: List of (mentee_id, mentor_id) pairs
        """
        # TODO: Implement on Day 3
        pairings = []

        # PLACEHOLDER: Gale-Shapley algorithm implementation goes here

        return pairings

    # =====================================================
    # STORAGE FUNCTIONS - SKELETON (TODO: Day 2-3)
    # =====================================================

    def store_matches(self, pairings: List[Tuple[str, str]], score_matrix: Dict, algorithm_name: str) -> int:
        """
        Store final matches in the database.

        TODO (Day 2-3):
        1. For each (mentee_id, mentor_id) pair:
           - Lookup scores from score_matrix
           - INSERT into matches table
           - Generate match_id (UUID)
           - Set status = 'pending'
           - Set created_at = current timestamp
        2. Return count of successful inserts

        Args:
            pairings: List of (mentee_id, mentor_id) tuples
            score_matrix: {mentee_id: {mentor_id: score_dict}}
            algorithm_name: Name of algorithm used

        Returns:
            int: Number of matches successfully stored
        """
        # TODO: Implement on Day 2-3
        successful_inserts = 0

        # PLACEHOLDER: Insert matches
        # for mentee_id, mentor_id in pairings:
        #     scores = score_matrix[mentee_id][mentor_id]
        #     self.cursor.execute("""
        #         INSERT INTO matches (
        #             match_id, mentor_id, mentee_id, algorithm_name,
        #             semantic_score, expertise_score, final_score, status
        #         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        #     """, (
        #         str(uuid.uuid4()), mentor_id, mentee_id, algorithm_name,
        #         scores['semantic_score'], scores['expertise_score'], 
        #         scores['final_score'], 'pending'
        #     ))
        #     successful_inserts += 1
        # self.conn.commit()

        return successful_inserts

    # =====================================================
    # MAIN EXECUTION - SKELETON (TODO: Day 4)
    # =====================================================

    def execute_matching(self, algorithm_name: str = 'Gale-Shapley') -> int:
        """
        Main execution pipeline - orchestrates the entire matching process.

        TODO (Day 4):
        1. Print "Starting matching process..."
        2. Call generate_preference_rankings() → get preferences and score_matrix
        3. Fetch mentor capacities from database
        4. Call gale_shapley_matching() → get pairings
        5. Call store_matches() → save to database
        6. Print summary statistics (total matches, avg score)
        7. Return number of successful matches

        Args:
            algorithm_name: Name of matching algorithm to use

        Returns:
            int: Number of successful matches created
        """
        # TODO: Implement on Day 4
        print(f"TODO: Execute {algorithm_name} matching")

        # PLACEHOLDER: Main execution flow
        # Step 1: Generate preferences
        # mentee_prefs, mentor_prefs, score_matrix = self.generate_preference_rankings()

        # Step 2: Get mentor capacities
        # self.cursor.execute("""
        #     SELECT mentor_profile_id, 
        #            (max_mentee_capacity - current_mentee_count) as capacity
        #     FROM mentor_profiles
        # """)
        # mentor_capacities = {row['mentor_profile_id']: row['capacity'] 
        #                      for row in self.cursor.fetchall()}

        # Step 3: Run matching algorithm
        # pairings = self.gale_shapley_matching(mentee_prefs, mentor_prefs, mentor_capacities)

        # Step 4: Store results
        # num_matches = self.store_matches(pairings, score_matrix, algorithm_name)

        # return num_matches

        return 0  # Placeholder

    # =====================================================
    # UTILITY FUNCTIONS
    # =====================================================

    def get_available_mentors(self) -> List[Dict]:
        """
        Fetch all mentors with available capacity.

        Returns:
            List[Dict]: List of mentor profiles with available slots
        """
        self.cursor.execute("""
            SELECT 
                mentor_profile_id,
                user_id,
                expertise_area,
                expertise_level,
                max_mentee_capacity,
                current_mentee_count,
                (max_mentee_capacity - current_mentee_count) as available_slots
            FROM mentor_profiles
            WHERE current_mentee_count < max_mentee_capacity
            ORDER BY available_slots DESC
        """)
        return self.cursor.fetchall()

    def get_all_mentees(self) -> List[Dict]:
        """
        Fetch all mentee profiles.

        Returns:
            List[Dict]: List of mentee profiles
        """
        self.cursor.execute("""
            SELECT 
                mentee_profile_id,
                user_id,
                main_interest,
                main_interest_level
            FROM mentee_profiles
        """)
        return self.cursor.fetchall()

    def close(self):
        """Close database connection and cleanup resources."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Database connection closed")


# =====================================================
# USAGE EXAMPLE
# =====================================================

if __name__ == "__main__":
    # Connection string
    DB_CONNECTION = "postgresql://postgres:password123@localhost:5432/mentor_db"

    # Initialize system
    matcher = MentorMatchingSystem(DB_CONNECTION)

    # Test implemented functions (Day 1)
    print("\n=== Testing Day 1 Implementation ===")

    # Example: Test scoring functions (requires actual data in DB)
    # mentee_id = "some-uuid"
    # mentor_id = "some-uuid"
    # scores = matcher.compute_combined_score(mentee_id, mentor_id)
    # print(f"Semantic: {scores['semantic_score']:.3f}")
    # print(f"Expertise: {scores['expertise_score']:.3f}")
    # print(f"Final: {scores['final_score']:.3f}")

    # Get available mentors
    mentors = matcher.get_available_mentors()
    print(f"Available mentors: {len(mentors)}")

    # Get all mentees
    mentees = matcher.get_all_mentees()
    print(f"Total mentees: {len(mentees)}")

    # TODO: Uncomment on Day 4
    # num_matches = matcher.execute_matching(algorithm_name='Gale-Shapley')
    # print(f"Created {num_matches} matches")

    # Cleanup
    matcher.close()
