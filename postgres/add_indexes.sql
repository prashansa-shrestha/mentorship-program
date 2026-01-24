-- Index FKs on mentor_profiles
CREATE INDEX IF NOT EXISTS idx_mentor_profiles_user_id
    ON mentor_profiles (user_id);

-- Index FKs on mentee_profiles
CREATE INDEX IF NOT EXISTS idx_mentee_profiles_user_id
    ON mentee_profiles (user_id);

-- Index FKs on embeddings
CREATE INDEX IF NOT EXISTS idx_embeddings_mentor_profile_id
    ON embeddings (mentor_profile_id);

CREATE INDEX IF NOT EXISTS idx_embeddings_mentee_profile_id
    ON embeddings (mentee_profile_id);

-- Index FKs on matches
CREATE INDEX IF NOT EXISTS idx_matches_mentor_profile_id
    ON matches (mentor_profile_id);

CREATE INDEX IF NOT EXISTS idx_matches_mentee_profile_id
    ON matches (mentee_profile_id);

CREATE INDEX IF NOT EXISTS idx_matches_run_id
    ON matches (run_id);
-- Optional: IVFFlat index on embeddings.embedding_vector
-- Only create this AFTER you have > 50 rows in embeddings
-- and pgvector extension installed.
-- Example:
-- CREATE INDEX IF NOT EXISTS idx_embeddings_vector_ivfflat
--   ON embeddings USING ivfflat (embedding_vector vector_l2_ops)
--   WITH (lists = 100);
