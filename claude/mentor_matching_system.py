
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import numpy as np
from datetime import datetime
import json
from typing import List, Dict, Tuple, Optional
import uuid

class MentorMatchingSystem:
    """
    Hybrid recommendation system for mentor-mentee matching using:
    1. IVFFlat vector similarity (semantic matching)
    2. Personality compatibility scoring
    3. Hobby/interest bonus
    4. Gale-Shapley stable matching algorithm
    """

    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def create_algorithm_config(self, 
                                algorithm_name: str,
                                semantic_weight: float = 0.5,
                                personality_weight: float = 0.25,
                                hobby_weight: float = 0.15,
                                expertise_weight: float = 0.1) -> str:
        """Create algorithm configuration for reproducibility"""

        config_id = str(uuid.uuid4())
        hyperparameters = {
            'lists': 100,  # IVFFlat clusters
            'probes': 10,  # sqrt(100) for balanced speed/accuracy
            'distance_metric': 'cosine',
            'min_expertise_match': 2  # Minimum expertise level difference
        }

        self.cursor.execute("""
            INSERT INTO algorithm_configurations (
                config_id, algorithm_name, algorithm_version, algorithm_category,
                hyperparameters, semantic_weight, personality_weight, 
                hobby_weight, expertise_weight, description, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            config_id, algorithm_name, '1.0', 'hybrid',
            json.dumps(hyperparameters),
            semantic_weight, personality_weight, hobby_weight, expertise_weight,
            f'Hybrid matching: IVFFlat + {algorithm_name} with weighted scoring',
            'system'
        ))
        self.conn.commit()
        return config_id

    def create_ivfflat_indexes(self, lists: int = 100):
        """Create IVFFlat indexes for fast vector similarity search"""

        # Main interest/expertise embeddings
        self.cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_embeddings_main_ivfflat 
            ON embeddings USING ivfflat (embedding_vector vector_cosine_ops) 
            WITH (lists = {lists})
            WHERE embedding_type = 'main_interest'
        """)

        # Combined embeddings (expertise + personality + hobbies)
        self.cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_embeddings_combined_ivfflat 
            ON embeddings USING ivfflat (embedding_vector vector_cosine_ops) 
            WITH (lists = {lists})
            WHERE embedding_type = 'combined'
        """)

        # Personality embeddings
        self.cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_embeddings_personality_ivfflat 
            ON embeddings USING ivfflat (embedding_vector vector_cosine_ops) 
            WITH (lists = {lists})
            WHERE embedding_type = 'personality'
        """)

        self.conn.commit()
        print(f"Created IVFFlat indexes with {lists} clusters")

    def compute_semantic_similarity(self, mentee_id: str, probes: int = 10) -> List[Dict]:
        """
        Fast vector similarity search using IVFFlat index
        Returns top mentor matches based on semantic similarity
        """

        # Set probes for accuracy/speed tradeoff
        self.cursor.execute(f"SET ivfflat.probes = {probes}")

        # Query mentee's combined embedding
        self.cursor.execute("""
            SELECT embedding_vector 
            FROM embeddings 
            WHERE mentee_profile_id = %s 
            AND embedding_type = 'combined'
            LIMIT 1
        """, (mentee_id,))

        mentee_embedding = self.cursor.fetchone()
        if not mentee_embedding:
            return []

        # Find top 50 similar mentors using IVFFlat (fast clustering search)
        self.cursor.execute("""
            SELECT 
                e.mentor_profile_id,
                mp.expertise_area,
                mp.expertise_level,
                mp.current_mentee_count,
                mp.max_mentee_capacity,
                1 - (e.embedding_vector <=> %s) as cosine_similarity
            FROM embeddings e
            JOIN mentor_profiles mp ON e.mentor_profile_id = mp.mentor_profile_id
            WHERE e.embedding_type = 'combined'
            AND mp.current_mentee_count < mp.max_mentee_capacity
            ORDER BY e.embedding_vector <=> %s
            LIMIT 50
        """, (mentee_embedding['embedding_vector'], mentee_embedding['embedding_vector']))

        return self.cursor.fetchall()

    def compute_personality_compatibility(self, mentee_id: str, mentor_id: str) -> float:
        """Calculate personality alignment score (0-1)"""

        self.cursor.execute("""
            SELECT 
                mentee.guidance_preference,
                mentee.feedback_preference,
                mentee.communication_style,
                mentee.disagreement_handling,
                mentee.commitment_style,
                mentor.guidance_style,
                mentor.feedback_style,
                mentor.discussion_style,
                mentor.disagreement_handling as mentor_disagreement,
                mentor.commitment_style as mentor_commitment
            FROM mentee_profiles mentee
            CROSS JOIN mentor_profiles mentor
            WHERE mentee.mentee_profile_id = %s 
            AND mentor.mentor_profile_id = %s
        """, (mentee_id, mentor_id))

        result = self.cursor.fetchone()
        if not result:
            return 0.0

        # Match guidance style
        guidance_match = 1.0 if result['guidance_preference'] == result['guidance_style'] else 0.5

        # Match feedback style
        feedback_match = 1.0 if result['feedback_preference'] == result['feedback_style'] else 0.5

        # Communication compatibility
        comm_match = 1.0 if result['communication_style'] == result['discussion_style'] else 0.6

        # Conflict resolution alignment
        conflict_match = 1.0 if result['disagreement_handling'] == result['mentor_disagreement'] else 0.7

        # Commitment alignment
        commitment_match = 1.0 if result['commitment_style'] == result['mentor_commitment'] else 0.6

        # Weighted average
        personality_score = (
            guidance_match * 0.25 +
            feedback_match * 0.25 +
            comm_match * 0.20 +
            conflict_match * 0.15 +
            commitment_match * 0.15
        )

        return personality_score

    def compute_hobby_bonus(self, mentee_id: str, mentor_id: str) -> float:
        """Calculate hobby/interest overlap bonus (0-1)"""

        self.cursor.execute("""
            SELECT 
                e1.embedding_vector as mentee_hobby,
                e2.embedding_vector as mentor_hobby
            FROM embeddings e1
            CROSS JOIN embeddings e2
            WHERE e1.mentee_profile_id = %s 
            AND e2.mentor_profile_id = %s
            AND e1.embedding_type = 'text_description'
            AND e2.embedding_type = 'text_description'
        """, (mentee_id, mentor_id))

        result = self.cursor.fetchone()
        if not result:
            return 0.0

        # Cosine similarity for hobby embeddings
        hobby_similarity = 1 - self.cosine_distance(
            result['mentee_hobby'], 
            result['mentor_hobby']
        )

        return max(0.0, min(1.0, hobby_similarity))

    def compute_expertise_match(self, mentee_id: str, mentor_id: str) -> float:
        """Calculate expertise level appropriateness (0-1)"""
        
        self.cursor.execute("""
            SELECT 
                mentee.expertise_level as mentee_level,
                mentor.expertise_level as mentor_level,
                mentor.years_of_experience
            FROM mentee_profiles mentee
            CROSS JOIN mentor_profiles mentor
            WHERE mentee.mentee_profile_id = %s 
            AND mentor.mentor_profile_id = %s
        """, (mentee_id, mentor_id))
        
        result = self.cursor.fetchone()
        if not result:
            return 0.0
        
        level_gap = result['mentor_level'] - result['mentee_level']
        
        # High score ONLY for gap of 2-3 levels
        if 2 <= level_gap <= 3:
            expertise_score = 1.0
        else:
            expertise_score = 0.3  # Low score for all other gaps
        
        # Bonus for experience (optional - keep if you want)
        if result['years_of_experience'] >= 5:
            expertise_score = min(1.0, expertise_score * 1.1)
        
        return expertise_score


    def compute_combined_score(self, 
                               mentee_id: str, 
                               mentor_id: str,
                               weights: Dict[str, float]) -> Dict:
        """Calculate final weighted compatibility score"""

        semantic_score = self.compute_semantic_similarity_single(mentee_id, mentor_id)
        personality_score = self.compute_personality_compatibility(mentee_id, mentor_id)
        hobby_score = self.compute_hobby_bonus(mentee_id, mentor_id)
        expertise_score = self.compute_expertise_match(mentee_id, mentor_id)

        final_score = (
            semantic_score * weights['semantic_weight'] +
            personality_score * weights['personality_weight'] +
            hobby_score * weights['hobby_weight'] +
            expertise_score * weights['expertise_weight']
        )

        return {
            'semantic_similarity_score': semantic_score,
            'personality_compatibility_score': personality_score,
            'hobby_bonus_score': hobby_score,
            'experience_match_score': expertise_score,
            'final_combined_score': final_score,
            'score_components': json.dumps({
                'semantic': semantic_score,
                'personality': personality_score,
                'hobby': hobby_score,
                'expertise': expertise_score
            })
        }

    def compute_semantic_similarity_single(self, mentee_id: str, mentor_id: str) -> float:
        """Calculate semantic similarity between specific mentee-mentor pair"""

        self.cursor.execute("""
            SELECT 
                1 - (e1.embedding_vector <=> e2.embedding_vector) as similarity
            FROM embeddings e1
            CROSS JOIN embeddings e2
            WHERE e1.mentee_profile_id = %s 
            AND e2.mentor_profile_id = %s
            AND e1.embedding_type = 'combined'
            AND e2.embedding_type = 'combined'
        """, (mentee_id, mentor_id))

        result = self.cursor.fetchone()
        return result['similarity'] if result else 0.0

    @staticmethod
    def cosine_distance(vec1, vec2):
        """Helper for cosine distance calculation"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def generate_preference_rankings(self, 
                                     matching_round_id: str,
                                     config_id: str) -> Tuple[Dict, Dict]:
        """
        Generate preference rankings for Gale-Shapley algorithm
        Returns: (mentee_preferences, mentor_preferences)
        """

        # Get weights from config
        self.cursor.execute("""
            SELECT semantic_weight, personality_weight, hobby_weight, expertise_weight
            FROM algorithm_configurations
            WHERE config_id = %s
        """, (config_id,))

        config = self.cursor.fetchone()
        weights = {
            'semantic_weight': config['semantic_weight'],
            'personality_weight': config['personality_weight'],
            'hobby_weight': config['hobby_weight'],
            'expertise_weight': config['expertise_weight']
        }

        # Get all active mentees
        self.cursor.execute("""
            SELECT mentee_profile_id, user_id 
            FROM mentee_profiles
        """)
        mentees = self.cursor.fetchall()

        # Get available mentors
        self.cursor.execute("""
            SELECT mentor_profile_id, user_id, max_mentee_capacity, current_mentee_count
            FROM mentor_profiles
            WHERE current_mentee_count < max_mentee_capacity
        """)
        mentors = self.cursor.fetchall()

        mentee_preferences = {}
        mentor_preferences = {}

        # Generate mentee preference rankings
        for mentee in mentees:
            mentee_id = mentee['mentee_profile_id']
            scores = []

            for mentor in mentors:
                mentor_id = mentor['mentor_profile_id']
                score_data = self.compute_combined_score(mentee_id, mentor_id, weights)
                scores.append((mentor_id, score_data['final_combined_score'], score_data))

            # Sort by score descending
            scores.sort(key=lambda x: x[1], reverse=True)
            mentee_preferences[mentee_id] = scores

            # Store in preference_rankings table
            for rank, (mentor_id, score, score_data) in enumerate(scores, 1):
                self.cursor.execute("""
                    INSERT INTO preference_rankings (
                        matching_round_id, ranker_id, ranker_role, 
                        ranked_profile_id, rank_position, computed_score, score_components
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    matching_round_id, mentee['user_id'], 'mentee',
                    mentor_id, rank, score, score_data['score_components']
                ))

        # Generate mentor preference rankings (same logic reversed)
        for mentor in mentors:
            mentor_id = mentor['mentor_profile_id']
            scores = []

            for mentee in mentees:
                mentee_id = mentee['mentee_profile_id']
                score_data = self.compute_combined_score(mentee_id, mentor_id, weights)
                scores.append((mentee_id, score_data['final_combined_score'], score_data))

            scores.sort(key=lambda x: x[1], reverse=True)
            mentor_preferences[mentor_id] = scores

            for rank, (mentee_id, score, score_data) in enumerate(scores, 1):
                self.cursor.execute("""
                    INSERT INTO preference_rankings (
                        matching_round_id, ranker_id, ranker_role, 
                        ranked_profile_id, rank_position, computed_score, score_components
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    matching_round_id, mentor['user_id'], 'mentor',
                    mentee_id, rank, score, score_data['score_components']
                ))

        self.conn.commit()
        return mentee_preferences, mentor_preferences

    def gale_shapley_matching(self, 
                             mentee_preferences: Dict,
                             mentor_preferences: Dict,
                             mentor_capacities: Dict) -> List[Tuple]:
        """
        Implement Gale-Shapley stable matching algorithm with capacity constraints
        Returns: List of (mentee_id, mentor_id) pairings
        """

        free_mentees = list(mentee_preferences.keys())
        mentor_matches = {m: [] for m in mentor_preferences.keys()}
        mentee_matches = {}
        next_proposal = {mentee: 0 for mentee in mentee_preferences.keys()}

        while free_mentees:
            mentee = free_mentees.pop(0)

            if next_proposal[mentee] >= len(mentee_preferences[mentee]):
                continue  # Mentee has exhausted all options

            # Get next preferred mentor
            mentor, score, score_data = mentee_preferences[mentee][next_proposal[mentee]]
            next_proposal[mentee] += 1

            # Check mentor capacity
            if len(mentor_matches[mentor]) < mentor_capacities[mentor]:
                # Mentor has capacity, accept proposal
                mentor_matches[mentor].append((mentee, score))
                mentee_matches[mentee] = mentor
            else:
                # Mentor at capacity, check if mentee is preferred over current matches
                current_matches = mentor_matches[mentor]
                mentor_pref_list = {m_id: rank for rank, (m_id, _, _) in enumerate(mentor_preferences[mentor])}

                # Find least preferred current match
                least_preferred = max(current_matches, key=lambda x: mentor_pref_list.get(x[0], float('inf')))

                if mentor_pref_list.get(mentee, float('inf')) < mentor_pref_list.get(least_preferred[0], float('inf')):
                    # Replace least preferred with new mentee
                    mentor_matches[mentor].remove(least_preferred)
                    mentor_matches[mentor].append((mentee, score))

                    # Free the rejected mentee
                    del mentee_matches[least_preferred[0]]
                    free_mentees.append(least_preferred[0])

                    mentee_matches[mentee] = mentor
                else:
                    # Reject new proposal
                    free_mentees.append(mentee)

        # Convert to pairings list
        pairings = [(mentee, mentor) for mentee, mentor in mentee_matches.items()]
        return pairings

    def create_matching_round(self, 
                             round_name: str,
                             algorithm_name: str = 'Gale-Shapley-IVFFlat-Hybrid') -> str:
        """Initialize a new matching round"""

        # Create algorithm config
        config_id = self.create_algorithm_config(algorithm_name)

        # Create matching round
        matching_round_id = str(uuid.uuid4())

        self.cursor.execute("""
            SELECT COUNT(*) as total 
            FROM mentor_profiles 
            WHERE current_mentee_count < max_mentee_capacity
        """)
        total_mentors = self.cursor.fetchone()['total']

        self.cursor.execute("""
            SELECT COUNT(*) as total FROM mentee_profiles
        """)
        total_mentees = self.cursor.fetchone()['total']

        self.cursor.execute("""
            INSERT INTO matching_rounds (
                matching_round_id, round_name, config_id, 
                algorithm_used, algorithm_version,
                total_mentors, total_mentees,
                started_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            matching_round_id, round_name, config_id,
            algorithm_name, '1.0',
            total_mentors, total_mentees,
            datetime.now()
        ))

        self.conn.commit()
        return matching_round_id, config_id

    def execute_matching_round(self, round_name: str):
        """
        Main execution function - runs complete matching pipeline
        """

        start_time = datetime.now()
        print(f"Starting matching round: {round_name}")

        # Step 1: Create matching round and config
        matching_round_id, config_id = self.create_matching_round(round_name)
        print(f"Created matching round: {matching_round_id}")

        # Step 2: Generate preference rankings using IVFFlat + weighted scoring
        print("Generating preference rankings...")
        mentee_prefs, mentor_prefs = self.generate_preference_rankings(
            matching_round_id, config_id
        )

        # Step 3: Get mentor capacities
        self.cursor.execute("""
            SELECT mentor_profile_id, max_mentee_capacity, current_mentee_count
            FROM mentor_profiles
        """)
        mentor_data = self.cursor.fetchall()
        mentor_capacities = {
            m['mentor_profile_id']: m['max_mentee_capacity'] - m['current_mentee_count']
            for m in mentor_data
        }

        # Step 4: Run Gale-Shapley stable matching
        print("Running Gale-Shapley algorithm...")
        pairings = self.gale_shapley_matching(mentee_prefs, mentor_prefs, mentor_capacities)

        # Step 5: Store matches
        print(f"Generated {len(pairings)} matches. Storing results...")
        successful_matches = 0
        total_score = 0
        scores = []

        for mentee_id, mentor_id in pairings:
            # Get score data
            score_data = None
            for m_id, score, s_data in mentee_prefs[mentee_id]:
                if m_id == mentor_id:
                    score_data = s_data
                    break

            if not score_data:
                continue

            # Store in potential_pairings
            pairing_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO potential_pairings (
                    pairing_id, mentor_id, mentee_id, matching_round_id,
                    semantic_similarity_score, personality_compatibility_score,
                    hobby_bonus_score, experience_match_score,
                    final_combined_score, selected, score_components
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pairing_id, mentor_id, mentee_id, matching_round_id,
                score_data['semantic_similarity_score'],
                score_data['personality_compatibility_score'],
                score_data['hobby_bonus_score'],
                score_data['experience_match_score'],
                score_data['final_combined_score'],
                True,  # Selected by algorithm
                score_data['score_components']
            ))

            # Store in matches
            match_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO matches (
                    match_id, mentor_id, mentee_id, matching_round_id,
                    status, matching_algorithm, config_id,
                    semantic_similarity_score, personality_compatibility_score,
                    hobby_bonus_score, experience_match_score,
                    final_combined_score, matched_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                match_id, mentor_id, mentee_id, matching_round_id,
                'pending', 'Gale-Shapley-IVFFlat-Hybrid', config_id,
                score_data['semantic_similarity_score'],
                score_data['personality_compatibility_score'],
                score_data['hobby_bonus_score'],
                score_data['experience_match_score'],
                score_data['final_combined_score'],
                datetime.now()
            ))

            successful_matches += 1
            total_score += score_data['final_combined_score']
            scores.append(score_data['final_combined_score'])

        # Step 6: Update matching round with results
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        avg_score = total_score / successful_matches if successful_matches > 0 else 0
        median_score = np.median(scores) if scores else 0
        std_score = np.std(scores) if scores else 0

        self.cursor.execute("""
            UPDATE matching_rounds SET
                completed_at = %s,
                execution_time_seconds = %s,
                successful_matches = %s,
                avg_match_score = %s,
                median_match_score = %s,
                std_match_score = %s
            WHERE matching_round_id = %s
        """, (
            end_time, execution_time, successful_matches,
            avg_score, median_score, std_score,
            matching_round_id
        ))

        self.conn.commit()

        print(f"\n=== Matching Round Complete ===")
        print(f"Successful matches: {successful_matches}")
        print(f"Average score: {avg_score:.3f}")
        print(f"Median score: {median_score:.3f}")
        print(f"Execution time: {execution_time:.2f}s")

        return matching_round_id

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Initialize system
    matcher = MentorMatchingSystem(
        "postgresql://user:password@localhost:5432/mentor_db"
    )

    # Create IVFFlat indexes (one-time setup)
    # matcher.create_ivfflat_indexes(lists=100)

    # Run matching round
    matching_round_id = matcher.execute_matching_round(
        round_name="January_2026_Cohort_1"
    )

    # Close connection
    matcher.close()
