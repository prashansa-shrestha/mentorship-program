import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np
import sys
sys.path.append('../src')  # Access src modules

from preprocessor import mentors_df, mentees_df
from embedder import mentors_embedded_df, mentees_embedded_df
from concatenator import (
    mentors_feature_matrices_dict,
    mentees_feature_matrices_dict
)

# ===== CONFIGURATION =====
WEIGHTS = {
    'area1': 0.5,  # Primary interest area
    'area2': 0.3,  # Secondary interest area
    'area3': 0.2   # Tertiary interest area
}

conn = psycopg2.connect("postgresql://user:password@localhost:5432/mentor_db")
cursor = conn.cursor()

def create_combined_embedding(area1_emb, area2_emb, area3_emb):
    """
    Creates weighted combined embedding instead of simple average
    
    Parameters:
        area1_emb, area2_emb, area3_emb: np.ndarray
            Individual area embeddings (384-dimensional)
    
    Returns:
        combined_emb: np.ndarray
            Weighted combined embedding (384-dimensional)
    """
    combined_emb = (
        WEIGHTS['area1'] * area1_emb +
        WEIGHTS['area2'] * area2_emb +
        WEIGHTS['area3'] * area3_emb
    )
    
    # Normalize to unit length (important for cosine similarity)
    norm = np.linalg.norm(combined_emb)
    if norm > 0:
        combined_emb = combined_emb / norm
    
    return combined_emb


# ===== 1. INSERT USERS & PROFILES =====
print("Inserting mentors...")

for idx, row in mentors_df.iterrows():
    # Insert user
    cursor.execute("""
        INSERT INTO users (name, campus_roll_number, email, role, hobby)
        VALUES (%s, %s, %s, 'mentor', %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING user_id
    """, (
        row.get('name'),
        row.get('campus_roll_number'),
        row.get('email'),
        row.get('hobby')
    ))
    
    result = cursor.fetchone()
    if not result:
        # User already exists, get their ID
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (row.get('email'),))
        result = cursor.fetchone()
    
    user_id = result[0]
    
    # Insert mentor profile
    cursor.execute("""
        INSERT INTO mentor_profiles (
            user_id, expertise_area, expertise_level,
            years_of_experience, max_mentee_capacity, current_mentee_count,
            guidance_style, feedback_style, discussion_style,
            disagreement_handling, commitment_style, primary_motivation,
            goal_approach, stalled_progress_response
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (
        user_id,
        row.get('engineering_subdomain_1'),
        int(row.get('current_level_of_expertise_technical1', 0) * 4 + 1),  # Denormalize: [0,1] → [1,5]
        row.get('years_of_experience', 0),
        3,  # max_mentee_capacity
        0,  # current_mentee_count
        row.get('guidance_style'),
        row.get('feedback_style'),
        row.get('discussion_style'),
        row.get('disagreement_handling'),
        row.get('commitment_style'),
        row.get('primary_motivation'),
        row.get('goal_approach'),
        row.get('stalled_progress_response')
    ))

conn.commit()

print("Inserting mentees...")

for idx, row in mentees_df.iterrows():
    cursor.execute("""
        INSERT INTO users (name, campus_roll_number, email, role, hobby)
        VALUES (%s, %s, %s, 'mentee', %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING user_id
    """, (
        row.get('name'),
        row.get('campus_roll_number'),
        row.get('email'),
        row.get('hobby')
    ))
    
    result = cursor.fetchone()
    if not result:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (row.get('email'),))
        result = cursor.fetchone()
    
    user_id = result[0]
    
    # Insert mentee profile
    cursor.execute("""
        INSERT INTO mentee_profiles (
            user_id, main_interest, main_interest_level,
            guidance_preference, feedback_preference, communication_style,
            disagreement_handling, commitment_style, primary_motivation,
            goal_approach, stalled_progress_response
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (
        user_id,
        row.get('areas_of_expected_guidance_priority_1'),
        int(row.get('current_expertise_1', 0) * 4 + 1),
        row.get('guidance_style_preference'),
        row.get('feedback_preference'),
        row.get('communication_style'),
        row.get('disagreement_handling'),
        row.get('commitment_style'),
        row.get('primary_motivation'),
        row.get('goal_approach'),
        row.get('stalled_progress_response')
    ))

conn.commit()


# ===== 2. INSERT EMBEDDINGS =====
print("Inserting mentor embeddings...")

# Get mapping: user_id → mentor_profile_id
cursor.execute("SELECT user_id, mentor_profile_id FROM mentor_profiles")
mentor_map = {row[0]: row[1] for row in cursor.fetchall()}

# Assuming mentors_feature_matrices_dict has keys: 'area1', 'area2', 'area3'
n_mentors = mentors_feature_matrices_dict['area1'].shape[0]

for i in range(n_mentors):
    # Get corresponding user_id (you need to match this based on your data structure)
    # Assuming mentors_df index matches the embedding row index
    user_id = mentors_df.iloc[i]['user_id']  # Adjust if needed
    mentor_profile_id = mentor_map.get(user_id)
    
    if not mentor_profile_id:
        continue
    
    # Extract individual area embeddings
    area1_emb = mentors_feature_matrices_dict['area1'][i]
    area2_emb = mentors_feature_matrices_dict['area2'][i]
    area3_emb = mentors_feature_matrices_dict['area3'][i]
    
    # Insert individual area embeddings
    cursor.execute("""
        INSERT INTO embeddings (
            mentor_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'main_interest', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentor_profile_id, area1_emb.tolist(), len(area1_emb)))
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentor_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'additional_interest', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentor_profile_id, area2_emb.tolist(), len(area2_emb)))
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentor_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'aspirations', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentor_profile_id, area3_emb.tolist(), len(area3_emb)))
    
    # Create weighted combined embedding
    combined_emb = create_combined_embedding(area1_emb, area2_emb, area3_emb)
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentor_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'combined', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentor_profile_id, combined_emb.tolist(), len(combined_emb)))

conn.commit()

print("Inserting mentee embeddings...")

# Similar process for mentees
cursor.execute("SELECT user_id, mentee_profile_id FROM mentee_profiles")
mentee_map = {row[0]: row[1] for row in cursor.fetchall()}

n_mentees = mentees_feature_matrices_dict['area1'].shape[0]

for i in range(n_mentees):
    user_id = mentees_df.iloc[i]['user_id']
    mentee_profile_id = mentee_map.get(user_id)
    
    if not mentee_profile_id:
        continue
    
    area1_emb = mentees_feature_matrices_dict['area1'][i]
    area2_emb = mentees_feature_matrices_dict['area2'][i]
    area3_emb = mentees_feature_matrices_dict['area3'][i]
    
    # Insert individual areas
    cursor.execute("""
        INSERT INTO embeddings (
            mentee_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'main_interest', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentee_profile_id, area1_emb.tolist(), len(area1_emb)))
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentee_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'additional_interest', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentee_profile_id, area2_emb.tolist(), len(area2_emb)))
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentee_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'aspirations', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentee_profile_id, area3_emb.tolist(), len(area3_emb)))
    
    # Weighted combined embedding
    combined_emb = create_combined_embedding(area1_emb, area2_emb, area3_emb)
    
    cursor.execute("""
        INSERT INTO embeddings (
            mentee_profile_id, embedding_type, embedding_vector,
            dimension, model_used, model_version
        ) VALUES (%s, 'combined', %s, %s, 'all-MiniLM-L6-v2', '1.0')
    """, (mentee_profile_id, combined_emb.tolist(), len(combined_emb)))

conn.commit()
cursor.close()
conn.close()

print("✅ Database populated successfully!")
print(f"   - Mentors: {n_mentors}")
print(f"   - Mentees: {n_mentees}")
print(f"   - Embedding weights: {WEIGHTS}")
