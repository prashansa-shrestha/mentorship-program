-- =====================================================
-- MINIMAL MENTOR-MENTEE MATCHING SCHEMA
-- Purpose: Prototype schema for hybrid recommendation system
-- Embedding Model: all-MiniLM-L6-v2 (384 dimensions)
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUID generation
CREATE EXTENSION IF NOT EXISTS vector;       -- For pgvector embeddings

-- =====================================================
-- TABLE 1: USERS (Base table for both mentors and mentees)
-- =====================================================
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('mentor', 'mentee')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast role-based queries
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

COMMENT ON TABLE users IS 'Base user table - stores common fields for mentors and mentees';
COMMENT ON COLUMN users.role IS 'User type: mentor or mentee';

-- =====================================================
-- TABLE 2: MENTOR_PROFILES
-- =====================================================
CREATE TABLE mentor_profiles (
    mentor_profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    expertise_area TEXT NOT NULL,
    expertise_level INTEGER NOT NULL CHECK (expertise_level BETWEEN 1 AND 5),
    max_mentee_capacity INTEGER DEFAULT 3 CHECK (max_mentee_capacity > 0),
    current_mentee_count INTEGER DEFAULT 0 CHECK (current_mentee_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure capacity constraint
    CONSTRAINT check_capacity CHECK (current_mentee_count <= max_mentee_capacity)
);

-- Index for finding available mentors
CREATE INDEX idx_mentor_available ON mentor_profiles(current_mentee_count, max_mentee_capacity)
    WHERE current_mentee_count < max_mentee_capacity;

COMMENT ON TABLE mentor_profiles IS 'Mentor-specific profile data';
COMMENT ON COLUMN mentor_profiles.expertise_level IS 'Expertise rating: 1=Beginner to 5=Expert';
COMMENT ON COLUMN mentor_profiles.max_mentee_capacity IS 'Maximum mentees this mentor can handle';

-- =====================================================
-- TABLE 3: MENTEE_PROFILES
-- =====================================================
CREATE TABLE mentee_profiles (
    mentee_profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    main_interest TEXT NOT NULL,
    main_interest_level INTEGER NOT NULL CHECK (main_interest_level BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for interest-based searches
CREATE INDEX idx_mentee_interest ON mentee_profiles(main_interest);

COMMENT ON TABLE mentee_profiles IS 'Mentee-specific profile data';
COMMENT ON COLUMN mentee_profiles.main_interest_level IS 'Current skill level: 1=Beginner to 5=Advanced';

-- =====================================================
-- TABLE 4: EMBEDDINGS (Vector representations)
-- =====================================================
CREATE TABLE embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentor_profile_id UUID REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_profile_id UUID REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    embedding_type VARCHAR(50) DEFAULT 'combined' NOT NULL,
    embedding_vector vector(384) NOT NULL,  -- 384 dimensions for all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure exactly ONE profile ID is set (XOR constraint)
    CONSTRAINT check_single_profile CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);

-- Indexes for fast vector similarity search
CREATE INDEX idx_embeddings_mentor ON embeddings(mentor_profile_id) WHERE mentor_profile_id IS NOT NULL;
CREATE INDEX idx_embeddings_mentee ON embeddings(mentee_profile_id) WHERE mentee_profile_id IS NOT NULL;
CREATE INDEX idx_embeddings_type ON embeddings(embedding_type);

COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic similarity matching';
COMMENT ON COLUMN embeddings.embedding_vector IS '384-dimensional vector from all-MiniLM-L6-v2 model';
COMMENT ON COLUMN embeddings.embedding_type IS 'Type: combined, main_interest, additional_interest, etc.';

-- =====================================================
-- TABLE 5: MATCHES (Final mentor-mentee pairings)
-- =====================================================
CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentor_id UUID NOT NULL REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_id UUID NOT NULL REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    semantic_score FLOAT CHECK (semantic_score BETWEEN 0 AND 1),
    expertise_score FLOAT CHECK (expertise_score BETWEEN 0 AND 1),
    final_score FLOAT CHECK (final_score BETWEEN 0 AND 1),
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate matches
    UNIQUE(mentor_id, mentee_id)
);

-- Indexes for match queries
CREATE INDEX idx_matches_mentor ON matches(mentor_id);
CREATE INDEX idx_matches_mentee ON matches(mentee_id);
CREATE INDEX idx_matches_score ON matches(final_score DESC);

COMMENT ON TABLE matches IS 'Final mentor-mentee match assignments';
COMMENT ON COLUMN matches.semantic_score IS 'Vector similarity score (0-1)';
COMMENT ON COLUMN matches.expertise_score IS 'Expertise level compatibility (0-1)';
COMMENT ON COLUMN matches.final_score IS 'Weighted combined score: 0.8*semantic + 0.2*expertise';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Count tables created
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('users', 'mentor_profiles', 'mentee_profiles', 'embeddings', 'matches');
    
    IF table_count = 5 THEN
        RAISE NOTICE '✅ Schema created successfully: 5 tables initialized';
    ELSE
        RAISE WARNING '⚠️  Expected 5 tables, found %', table_count;
    END IF;
END $$;

-- Display table summary
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE columns.table_name = tables.table_name) as column_count
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
