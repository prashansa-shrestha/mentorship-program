"""
Mentor Matching System - Complete Implementation
Fulfills Task 1 Requirements: PostgreSQL-based mentor-mentee matching
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Tuple
import numpy as np
import uuid
from datetime import datetime


class MentorMatchingSystem:
    """
    Mentor-mentee matching system using:
    - Semantic similarity via pgvector (70% weight)
    - Expertise level matching (30% weight)
    - Capacity-constrained matching algorithm
    """

    def __init__(self, db_config: str):
        """
        Initialize database connection.

        Args:
            db_config: PostgreSQL connection string
                Format: "postgresql://user:password@host:port/database"
        """
        try:
            self.conn = psycopg2.connect(db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise

    def get_all_mentors(self) -> List[Dict]:
        """
        Fetch all mentor profiles with embeddings.

        Returns:
            List[Dict]: All mentor profiles with metadata
        """
        try:
            self.cursor.execute("""
                SELECT 
                    mp.mentor_profile_id,
                    mp.user_id,
                    mp.expertise_area,
                    mp.expertise_level,
                    mp.max_mentee_capacity,
                    mp.current_mentee_count,
                    e.embedding_vector
                FROM mentor_profiles mp
                JOIN embeddings e ON e.mentor_profile_id = mp.mentor_profile_id
                WHERE e.embedding_type = 'combined'
                ORDER BY mp.expertise_level DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching mentors: {e}")
            return []

    def get_all_mentees(self) -> List[Dict]:
        """
        Fetch all mentee profiles with embeddings.

        Returns:
            List[Dict]: All mentee profiles with metadata
        """
        try:
            self.cursor.execute("""
                SELECT 
                    mp.mentee_profile_id,
                    mp.user_id,
                    mp.main_interest,
                    mp.main_interest_level,
                    e.embedding_vector
                FROM mentee_profiles mp
                JOIN embeddings e ON e.mentee_profile_id = mp.mentee_profile_id
                WHERE e.embedding_type = 'combined'
                ORDER BY mp.main_interest_level
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching mentees: {e}")
            return []

    def calculate_semantic_similarity(self, mentee_emb: np.ndarray, mentor_emb: np.ndarray) -> float:
        """
        Calculate cosine similarity between mentor and mentee embeddings.

        Args:
            mentee_emb: Mentee embedding vector (384 dimensions)
            mentor_emb: Mentor embedding vector (384 dimensions)

        Returns:
            float: Cosine similarity score [0, 1]
        """
        try:
            # Convert to numpy arrays if needed
            if not isinstance(mentee_emb, np.ndarray):
                mentee_emb = np.array(mentee_emb)
            if not isinstance(mentor_emb, np.ndarray):
                mentor_emb = np.array(mentor_emb)

            # Compute cosine similarity
            dot_product = np.dot(mentee_emb, mentor_emb)
            norm_mentee = np.linalg.norm(mentee_emb)
            norm_mentor = np.linalg.norm(mentor_emb)

            if norm_mentee == 0 or norm_mentor == 0:
                return 0.0

            similarity = dot_product / (norm_mentee * norm_mentor)

            # Normalize to [0, 1] range (cosine similarity is [-1, 1])
            return (similarity + 1) / 2
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def calculate_expertise_score(self, mentee_level: int, mentor_level: int) -> float:
        """
        Calculate expertise compatibility score based on level gap.

        Scoring logic:
        - Gap of 1-2 levels: optimal (score = 1.0)
        - Gap of 3 levels: good (score = 0.7)
        - Gap of 0 levels: suboptimal (score = 0.4)
        - Other gaps: poor (score = 0.2)

        Args:
            mentee_level: Mentee's expertise level (1-5)
            mentor_level: Mentor's expertise level (1-5)

        Returns:
            float: Expertise match score [0, 1]
        """
        try:
            level_gap = mentor_level - mentee_level

            if 1 <= level_gap <= 2:
                return 1.0  # Optimal gap
            elif level_gap == 3:
                return 0.6  # Good gap
            elif level_gap == 0:
                return 0.3  # Same level - less mentorship value
            else:
                return 0.1  # Too large or negative gap
        except Exception as e:
            print(f"Error calculating expertise score: {e}")
            return 0.0

    def calculate_combined_score(self, semantic: float, expertise: float) -> float:
        """
        Calculate weighted combined score.

        Formula: 0.7 × semantic_similarity + 0.3 × expertise_score

        Args:
            semantic: Semantic similarity score [0, 1]
            expertise: Expertise match score [0, 1]

        Returns:
            float: Combined score [0, 1]
        """
        return (0.7 * semantic) + (0.3 * expertise)

    def generate_matches(self) -> List[Dict]:
        """
        Main matching logic - generates optimal mentor-mentee pairings.

        Algorithm:
        1. Fetch all mentors and mentees
        2. Calculate all pairwise scores
        3. Apply capacity-constrained greedy matching
        4. Return sorted matches

        Returns:
            List[Dict]: Matches with mentor_id, mentee_id, and scores
        """
        try:
            print("Starting matching process...")

            # Fetch profiles
            mentors = self.get_all_mentors()
            mentees = self.get_all_mentees()

            if not mentors or not mentees:
                print("No mentors or mentees found")
                return []

            print(f"Matching {len(mentees)} mentees with {len(mentors)} mentors")

            # Calculate all pairwise scores
            all_scores = []
            for mentee in mentees:
                for mentor in mentors:
                    # Skip if mentor at capacity
                    available_capacity = mentor['max_mentee_capacity'] - mentor['current_mentee_count']
                    if available_capacity <= 0:
                        continue

                    # Calculate scores
                    semantic = self.calculate_semantic_similarity(
                        mentee['embedding_vector'],
                        mentor['embedding_vector']
                    )
                    expertise = self.calculate_expertise_score(
                        mentee['main_interest_level'],
                        mentor['expertise_level']
                    )
                    combined = self.calculate_combined_score(semantic, expertise)

                    all_scores.append({
                        'mentee_id': mentee['mentee_profile_id'],
                        'mentor_id': mentor['mentor_profile_id'],
                        'semantic_score': semantic,
                        'expertise_score': expertise,
                        'final_score': combined
                    })

            # Sort by final score (descending)
            all_scores.sort(key=lambda x: x['final_score'], reverse=True)

            # Greedy matching with capacity constraints
            matches = []
            matched_mentees = set()
            mentor_capacity = {m['mentor_profile_id']: 
                             m['max_mentee_capacity'] - m['current_mentee_count'] 
                             for m in mentors}

            for score_entry in all_scores:
                mentee_id = score_entry['mentee_id']
                mentor_id = score_entry['mentor_id']

                # Check if mentee already matched
                if mentee_id in matched_mentees:
                    continue

                # Check mentor capacity
                if mentor_capacity.get(mentor_id, 0) <= 0:
                    continue

                # Create match
                matches.append(score_entry)
                matched_mentees.add(mentee_id)
                mentor_capacity[mentor_id] -= 1

            print(f"Generated {len(matches)} matches")
            return matches

        except Exception as e:
            print(f"Error generating matches: {e}")
            return []

    def save_matches_to_db(self, matches: List[Dict]) -> int:
        """
        Save matches to the database.

        Args:
            matches: List of match dictionaries with scores

        Returns:
            int: Number of successfully inserted matches
        """
        try:
            successful_inserts = 0

            for match in matches:
                self.cursor.execute("""
                    INSERT INTO matches (
                        match_id, 
                        mentor_id, 
                        mentee_id, 
                        algorithm_name,
                        semantic_score, 
                        expertise_score, 
                        final_score, 
                        status,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    match['mentor_id'],
                    match['mentee_id'],
                    'greedy_capacity_constrained',
                    match['semantic_score'],
                    match['expertise_score'],
                    match['final_score'],
                    'pending',
                    datetime.now()
                ))
                successful_inserts += 1

            self.conn.commit()
            print(f"✓ Saved {successful_inserts} matches to database")
            return successful_inserts

        except Exception as e:
            self.conn.rollback()
            print(f"Error saving matches: {e}")
            return 0

    def close(self):
        """Close database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("✓ Database connection closed")
        except Exception as e:
            print(f"Error closing connection: {e}")


# Usage Example
if __name__ == "__main__":
    # Database configuration
    DB_CONFIG = "postgresql://postgres:password123@localhost:5432/mentor_db"

    try:
        # Initialize system
        matcher = MentorMatchingSystem(DB_CONFIG)

        # Generate matches
        matches = matcher.generate_matches()

        if matches:
            # Display summary statistics
            avg_score = sum(m['final_score'] for m in matches) / len(matches)
            print(f"\nMatch Summary:")
            print(f"  Total matches: {len(matches)}")
            print(f"  Average score: {avg_score:.3f}")
            print(f"  Score range: [{min(m['final_score'] for m in matches):.3f}, "
                  f"{max(m['final_score'] for m in matches):.3f}]")

            # Save to database
            saved_count = matcher.save_matches_to_db(matches)
            print(f"\n✓ Matching complete: {saved_count} matches saved")
        else:
            print("No matches generated")

        # Cleanup
        matcher.close()

    except Exception as e:
        print(f"Error in main execution: {e}")
