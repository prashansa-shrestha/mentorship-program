-- =====================================================
-- MINIMAL SCHEMA FOR MENTORSHIP MATCHING PROTOTYPE
-- Week 1 Implementation - 5 Core Tables Only
-- Embedding Model: all-MiniLM-L6-v2 (384 dimensions)
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE 1: USERS
-- =====================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('mentor', 'mentee', 'both')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

COMMENT ON TABLE users IS 'Core user table - stores basic identity information';
COMMENT ON COLUMN users.role IS 'User role: mentor, mentee, or both';

-- =====================================================
-- TABLE 2: MENTOR PROFILES
-- =====================================================

CREATE TABLE mentor_profiles (
    mentor_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,

    -- Expertise information
    expertise_area TEXT NOT NULL,
    expertise_level INTEGER NOT NULL CHECK (expertise_level BETWEEN 1 AND 5),

    -- Capacity management
    max_mentee_capacity INTEGER DEFAULT 3 CHECK (max_mentee_capacity > 0),
    current_mentee_count INTEGER DEFAULT 0 CHECK (current_mentee_count >= 0),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure capacity constraint
    CONSTRAINT chk_capacity CHECK (current_mentee_count <= max_mentee_capacity)
);

CREATE INDEX idx_mentor_user ON mentor_profiles(user_id);
CREATE INDEX idx_mentor_capacity ON mentor_profiles(current_mentee_count, max_mentee_capacity);
CREATE INDEX idx_mentor_expertise ON mentor_profiles(expertise_area, expertise_level);

COMMENT ON TABLE mentor_profiles IS 'Mentor-specific profile data with expertise and capacity tracking';
COMMENT ON COLUMN mentor_profiles.expertise_level IS '1=Beginner, 2=Intermediate, 3=Advanced, 4=Expert, 5=Master';
COMMENT ON COLUMN mentor_profiles.max_mentee_capacity IS 'Maximum number of mentees this mentor can handle';
COMMENT ON COLUMN mentor_profiles.current_mentee_count IS 'Current number of active mentees';

-- =====================================================
-- TABLE 3: MENTEE PROFILES
-- =====================================================

CREATE TABLE mentee_profiles (
    mentee_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,

    -- Interest information
    main_interest TEXT NOT NULL,
    current_expertise_level INTEGER NOT NULL CHECK (current_expertise_level BETWEEN 1 AND 5),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mentee_user ON mentee_profiles(user_id);
CREATE INDEX idx_mentee_interest ON mentee_profiles(main_interest, current_expertise_level);

COMMENT ON TABLE mentee_profiles IS 'Mentee-specific profile data with learning interests';
COMMENT ON COLUMN mentee_profiles.current_expertise_level IS '1=Novice, 2=Beginner, 3=Intermediate, 4=Advanced, 5=Expert';

-- =====================================================
-- TABLE 4: EMBEDDINGS
-- =====================================================

CREATE TABLE embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys (mutually exclusive)
    mentor_profile_id UUID REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_profile_id UUID REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,

    -- Embedding metadata
    embedding_type VARCHAR(50) NOT NULL CHECK (embedding_type IN ('main_interest', 'expertise', 'combined')),
    embedding_vector vector(384) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure exactly one profile type is set
    CONSTRAINT chk_profile_exclusivity CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);

CREATE INDEX idx_embeddings_mentor ON embeddings(mentor_profile_id);
CREATE INDEX idx_embeddings_mentee ON embeddings(mentee_profile_id);
CREATE INDEX idx_embeddings_type ON embeddings(embedding_type);

-- Vector similarity index for fast nearest neighbor search
CREATE INDEX idx_embeddings_vector_cosine ON embeddings 
USING ivfflat (embedding_vector vector_cosine_ops) 
WITH (lists = 100);

COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic similarity matching using all-MiniLM-L6-v2 model';
COMMENT ON COLUMN embeddings.embedding_vector IS 'CRITICAL: 384-dimensional vector from all-MiniLM-L6-v2 model';
COMMENT ON COLUMN embeddings.embedding_type IS 'Type of embedding: main_interest, expertise, or combined';
COMMENT ON CONSTRAINT chk_profile_exclusivity ON embeddings IS 'Embedding must belong to either mentor OR mentee, not both';

-- =====================================================
-- TABLE 5: MATCHES
-- =====================================================

CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Pairing information
    mentor_id UUID NOT NULL REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_id UUID NOT NULL REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,

    -- Algorithm metadata
    algorithm_name VARCHAR(100) NOT NULL,

    -- Scoring breakdown
    semantic_score FLOAT CHECK (semantic_score BETWEEN 0 AND 1),
    expertise_score FLOAT CHECK (expertise_score BETWEEN 0 AND 1),
    final_score FLOAT NOT NULL CHECK (final_score BETWEEN 0 AND 1),

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'declined')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique mentor-mentee pairs
    CONSTRAINT uq_mentor_mentee_pair UNIQUE (mentor_id, mentee_id)
);

CREATE INDEX idx_matches_mentor ON matches(mentor_id);
CREATE INDEX idx_matches_mentee ON matches(mentee_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_score ON matches(final_score DESC);
CREATE INDEX idx_matches_algorithm ON matches(algorithm_name);

COMMENT ON TABLE matches IS 'Final mentor-mentee pairings produced by matching algorithms';
COMMENT ON COLUMN matches.semantic_score IS 'Cosine similarity score from vector embeddings (0-1)';
COMMENT ON COLUMN matches.expertise_score IS 'Expertise level compatibility score (0-1)';
COMMENT ON COLUMN matches.final_score IS 'Weighted combination: 0.8*semantic + 0.2*expertise';

-- =====================================================
-- HELPER VIEWS
-- =====================================================

-- View 1: Available mentors with capacity
CREATE VIEW v_available_mentors AS
SELECT 
    m.mentor_profile_id,
    u.user_id,
    u.name,
    u.email,
    m.expertise_area,
    m.expertise_level,
    m.max_mentee_capacity,
    m.current_mentee_count,
    (m.max_mentee_capacity - m.current_mentee_count) as available_slots
FROM mentor_profiles m
JOIN users u ON m.user_id = u.user_id
WHERE m.current_mentee_count < m.max_mentee_capacity
ORDER BY available_slots DESC;

COMMENT ON VIEW v_available_mentors IS 'Mentors with available capacity for new mentees';

-- View 2: All mentees with their interests
CREATE VIEW v_mentees AS
SELECT 
    me.mentee_profile_id,
    u.user_id,
    u.name,
    u.email,
    me.main_interest,
    me.current_expertise_level
FROM mentee_profiles me
JOIN users u ON me.user_id = u.user_id
ORDER BY me.created_at DESC;

COMMENT ON VIEW v_mentees IS 'Complete mentee information with user details';

-- View 3: Match details with full information
CREATE VIEW v_match_details AS
SELECT 
    m.match_id,
    m.algorithm_name,
    m.semantic_score,
    m.expertise_score,
    m.final_score,
    m.status,
    m.created_at as matched_at,

    -- Mentor details
    mentor_user.name as mentor_name,
    mentor_user.email as mentor_email,
    mp.expertise_area as mentor_expertise,
    mp.expertise_level as mentor_level,

    -- Mentee details
    mentee_user.name as mentee_name,
    mentee_user.email as mentee_email,
    mep.main_interest as mentee_interest,
    mep.current_expertise_level as mentee_level

FROM matches m
JOIN mentor_profiles mp ON m.mentor_id = mp.mentor_profile_id
JOIN users mentor_user ON mp.user_id = mentor_user.user_id
JOIN mentee_profiles mep ON m.mentee_id = mep.mentee_profile_id
JOIN users mentee_user ON mep.user_id = mentee_user.user_id
ORDER BY m.final_score DESC;

COMMENT ON VIEW v_match_details IS 'Complete match information with mentor and mentee details';

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function: Get available mentors for matching
CREATE OR REPLACE FUNCTION get_available_mentors()
RETURNS TABLE (
    mentor_profile_id UUID,
    expertise_area TEXT,
    expertise_level INTEGER,
    available_slots INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.mentor_profile_id,
        m.expertise_area,
        m.expertise_level,
        (m.max_mentee_capacity - m.current_mentee_count) as available_slots
    FROM mentor_profiles m
    WHERE m.current_mentee_count < m.max_mentee_capacity
    ORDER BY available_slots DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_available_mentors IS 'Returns all mentors with available capacity for new matches';

-- =====================================================
-- SAMPLE QUERIES FOR TESTING
-- =====================================================

-- Query 1: Find semantic similarity between mentee and all available mentors
-- SELECT 
--     m.mentor_profile_id,
--     mp.expertise_area,
--     1 - (e_mentee.embedding_vector <=> e_mentor.embedding_vector) as cosine_similarity
-- FROM embeddings e_mentee
-- CROSS JOIN embeddings e_mentor
-- JOIN mentor_profiles mp ON e_mentor.mentor_profile_id = mp.mentor_profile_id
-- WHERE e_mentee.mentee_profile_id = 'YOUR_MENTEE_ID'
-- AND e_mentor.mentor_profile_id IS NOT NULL
-- AND e_mentee.embedding_type = 'combined'
-- AND e_mentor.embedding_type = 'combined'
-- AND mp.current_mentee_count < mp.max_mentee_capacity
-- ORDER BY cosine_similarity DESC
-- LIMIT 10;

-- Query 2: Get all matches with scores above threshold
-- SELECT * FROM v_match_details WHERE final_score > 0.7 AND status = 'pending';

-- Query 3: Check embedding vector dimension
-- SELECT 
--     embedding_id,
--     embedding_type,
--     vector_dims(embedding_vector) as dimensions
-- FROM embeddings
-- LIMIT 5;

-- =====================================================
-- VALIDATION QUERIES
-- =====================================================

-- Validate schema creation
DO $$
BEGIN
    -- Check if all 5 tables exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Table users not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'mentor_profiles') THEN
        RAISE EXCEPTION 'Table mentor_profiles not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'mentee_profiles') THEN
        RAISE EXCEPTION 'Table mentee_profiles not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'embeddings') THEN
        RAISE EXCEPTION 'Table embeddings not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'matches') THEN
        RAISE EXCEPTION 'Table matches not created';
    END IF;

    RAISE NOTICE 'Schema validation complete: All 5 core tables created successfully';
END $$;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
