-- =====================================================
-- MENTOR MATCHING SYSTEM - STREAMLINED SCHEMA
-- Optimized for MLflow integration
-- PostgreSQL + pgvector
-- =====================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =====================================================
-- CORE USER & PROFILE TABLES
-- =====================================================

-- USER table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    campus_roll_number VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(20) CHECK (role IN ('mentor', 'mentee', 'both')),
    is_alumni BOOLEAN DEFAULT FALSE,
    cv_file_path TEXT,
    linkedin_url TEXT,
    hobby TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_user_registration ON users(registration_date);


-- MENTEE_PROFILE table
CREATE TABLE mentee_profiles (
    mentee_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,

    -- Interest & Skills
    main_interest TEXT NOT NULL,
    main_interest_level INTEGER CHECK (main_interest_level BETWEEN 1 AND 5),
    additional_interest TEXT,
    additional_interest_level INTEGER CHECK (additional_interest_level BETWEEN 1 AND 5),
    non_technical_interests TEXT,
    non_technical_interest_level INTEGER CHECK (non_technical_interest_level BETWEEN 1 AND 5),
    future_aspirations TEXT,

    -- Preferences
    primary_motivation TEXT,
    goal_approach TEXT,
    guidance_style_preference TEXT,
    feedback_preference TEXT,
    stalled_progress_response TEXT,
    communication_style TEXT,
    disagreement_handling TEXT,
    commitment_style TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- MENTOR_PROFILE table
CREATE TABLE mentor_profiles (
    mentor_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE UNIQUE,

    -- Expertise & Experience
    expertise_area TEXT NOT NULL,
    expertise_level INTEGER CHECK (expertise_level BETWEEN 1 AND 5),
    additional_expertise_area TEXT,
    additional_expertise_level INTEGER CHECK (additional_expertise_level BETWEEN 1 AND 5),
    non_technical_areas TEXT,
    non_technical_expertise_level INTEGER CHECK (non_technical_expertise_level BETWEEN 1 AND 5),
    current_occupation TEXT,
    years_of_experience INTEGER,

    -- Capacity Management
    max_mentee_capacity INTEGER DEFAULT 3,
    current_mentee_count INTEGER DEFAULT 0,

    -- Mentoring Style
    primary_motivation TEXT,
    goal_approach TEXT,
    guidance_style TEXT,
    feedback_style TEXT,
    stalled_progress_response TEXT,
    discussion_style TEXT,
    disagreement_handling TEXT,
    commitment_style TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- EMBEDDING & FEATURE TABLES
-- =====================================================

-- EMBEDDING table (supports multiple embedding types)
CREATE TABLE embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_profile_id UUID REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_profile_id UUID REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    embedding_type VARCHAR(50) CHECK (embedding_type IN ('main_interest', 'additional_interest', 'aspirations', 'expertise', 'occupation', 'combined', 'personality', 'text_description')),
    embedding_vector vector(768), -- Adjust dimension based on model (768 for sentence-transformers)
    dimension INTEGER,
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);

-- Vector similarity search indexes
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_embeddings_type ON embeddings(embedding_type);


-- =====================================================
-- ALGORITHM CONFIGURATION (Minimal - MLflow handles details)
-- =====================================================

-- Lightweight algorithm registry (MLflow stores hyperparameters)
CREATE TABLE algorithm_configurations (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    algorithm_name VARCHAR(100) NOT NULL,
    algorithm_version VARCHAR(50),
    algorithm_category VARCHAR(50) CHECK (algorithm_category IN ('stable-matching', 'optimization', 'collaborative-filtering', 'hybrid')),

    -- Core weights only (MLflow logs full hyperparameters)
    semantic_weight FLOAT,
    personality_weight FLOAT,
    hobby_weight FLOAT,
    expertise_weight FLOAT,

    description TEXT,
    paper_reference TEXT,
    code_repository_url TEXT,

    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE algorithm_configurations IS 'Lightweight registry - full hyperparameters tracked in MLflow';


-- =====================================================
-- MATCHING ROUNDS (Linked to MLflow)
-- =====================================================

-- Matching rounds - now integrated with MLflow tracking
CREATE TABLE matching_rounds (
    matching_round_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_name VARCHAR(255),
    config_id UUID REFERENCES algorithm_configurations(config_id),

    -- MLflow integration
    mlflow_run_id VARCHAR(255) UNIQUE, -- Link to MLflow experiment run
    mlflow_experiment_id VARCHAR(255),
    mlflow_experiment_name VARCHAR(255),

    -- Algorithm metadata
    algorithm_used VARCHAR(100) NOT NULL,
    algorithm_version VARCHAR(50),

    -- Business-critical fields only
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),

    -- Basic counts (MLflow stores detailed metrics)
    total_mentors INTEGER,
    total_mentees INTEGER,
    successful_matches INTEGER,

    -- High-level results (MLflow has full breakdown)
    avg_match_score FLOAT,

    -- Reproducibility
    random_seed INTEGER,

    notes TEXT,
    is_baseline BOOLEAN DEFAULT FALSE,
    experiment_group VARCHAR(100)
);

CREATE INDEX idx_round_mlflow ON matching_rounds(mlflow_run_id);
CREATE INDEX idx_round_algorithm ON matching_rounds(algorithm_used);
CREATE INDEX idx_round_date ON matching_rounds(started_at);

COMMENT ON COLUMN matching_rounds.mlflow_run_id IS 'Link to MLflow for detailed metrics, parameters, and artifacts';


-- =====================================================
-- MATCHING & PAIRING TABLES
-- =====================================================

-- Matches - Final assignments with MLflow traceability
CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id),

    -- MLflow traceability
    mlflow_run_id VARCHAR(255),

    -- Match status
    status VARCHAR(20) CHECK (status IN ('pending', 'active', 'completed', 'declined', 'terminated')),

    -- Algorithm that produced this match
    algorithm_name VARCHAR(100),
    config_id UUID REFERENCES algorithm_configurations(config_id),

    -- Core compatibility scores
    semantic_similarity_score FLOAT,
    personality_compatibility_score FLOAT,
    hobby_bonus_score FLOAT,
    expertise_match_score FLOAT,
    final_combined_score FLOAT,

    -- Timestamps
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_interaction_at TIMESTAMP,
    last_interaction_at TIMESTAMP,

    notes TEXT,

    UNIQUE(mentor_id, mentee_id, matching_round_id)
);

CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_match_round ON matches(matching_round_id);
CREATE INDEX idx_match_mlflow ON matches(mlflow_run_id);
CREATE INDEX idx_match_timestamp ON matches(matched_at);

COMMENT ON COLUMN matches.mlflow_run_id IS 'Trace back to experiment that generated this match';


-- =====================================================
-- GROUND TRUTH & VALIDATION
-- =====================================================

-- Ground truth for model evaluation
CREATE TABLE ground_truth_matches (
    ground_truth_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),

    -- Success indicators
    is_successful BOOLEAN NOT NULL,
    success_score FLOAT CHECK (success_score BETWEEN 0 AND 10),
    success_factors JSONB,

    -- Data provenance
    data_source VARCHAR(100) CHECK (data_source IN ('historical', 'expert_labeled', 'survey', 'longitudinal_study')),
    labeling_confidence FLOAT CHECK (labeling_confidence BETWEEN 0 AND 1),
    labeled_by VARCHAR(255),

    -- Temporal info
    match_duration_days INTEGER,
    observation_period_days INTEGER,

    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ground_truth_success ON ground_truth_matches(is_successful);

COMMENT ON TABLE ground_truth_matches IS 'Validated matches for supervised learning - not tracked in MLflow';


-- =====================================================
-- FEEDBACK & OUTCOMES
-- =====================================================

-- Comprehensive feedback system
CREATE TABLE feedbacks (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(match_id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(user_id),
    reviewer_role VARCHAR(10) CHECK (reviewer_role IN ('mentor', 'mentee')),

    -- Rating dimensions
    overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
    communication_quality INTEGER CHECK (communication_quality BETWEEN 1 AND 5),
    technical_help_quality INTEGER CHECK (technical_help_quality BETWEEN 1 AND 5),
    availability_rating INTEGER CHECK (availability_rating BETWEEN 1 AND 5),
    goal_alignment_rating INTEGER CHECK (goal_alignment_rating BETWEEN 1 AND 5),
    personality_fit_rating INTEGER CHECK (personality_fit_rating BETWEEN 1 AND 5),

    -- Open-ended feedback
    feedback_text TEXT,
    positive_aspects TEXT[],
    improvement_areas TEXT[],

    -- Outcome metrics
    skill_improvement_self_report INTEGER CHECK (skill_improvement_self_report BETWEEN 1 AND 10),
    goals_achieved_count INTEGER,
    would_recommend BOOLEAN,
    would_continue BOOLEAN,

    -- Feedback timing
    weeks_since_match INTEGER,
    feedback_round INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_match ON feedbacks(match_id);
CREATE INDEX idx_feedback_role ON feedbacks(reviewer_role);
CREATE INDEX idx_feedback_timestamp ON feedbacks(created_at);


-- =====================================================
-- MATCH OUTCOMES (Links to MLflow experiments)
-- =====================================================

-- Track real-world outcomes of matches from different experiments
CREATE TABLE match_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(match_id) ON DELETE CASCADE,
    mlflow_run_id VARCHAR(255), -- Which experiment produced this match

    -- Ground truth labels
    is_successful BOOLEAN,
    satisfaction_score FLOAT,
    retention_days INTEGER,
    interaction_count INTEGER,
    goal_completion_rate FLOAT,

    -- Predicted vs actual (for model evaluation)
    predicted_success_score FLOAT,
    prediction_error FLOAT,

    -- Stability metrics
    is_stable_match BOOLEAN,
    is_blocking_pair BOOLEAN,
    mentor_rank_of_mentee INTEGER,
    mentee_rank_of_mentor INTEGER,

    -- Tracking
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(match_id, evaluation_date)
);

CREATE INDEX idx_outcome_match ON match_outcomes(match_id);
CREATE INDEX idx_outcome_mlflow ON match_outcomes(mlflow_run_id);

COMMENT ON TABLE match_outcomes IS 'Real-world outcomes linked to MLflow experiments for comparison';


-- =====================================================
-- DATASET SPLITS (For reproducible train/test splits)
-- =====================================================

-- Dataset splits for proper evaluation
CREATE TABLE dataset_splits (
    split_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    split_name VARCHAR(100) NOT NULL,
    split_strategy VARCHAR(100) CHECK (split_strategy IN ('temporal', 'random', 'leave-one-out', 'k-fold')),
    split_ratio FLOAT,
    temporal_cutoff_date TIMESTAMP,
    fold_number INTEGER,

    -- User/profile assignments
    mentor_ids UUID[],
    mentee_ids UUID[],

    -- MLflow linkage
    mlflow_experiment_name VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dataset_splits IS 'Reusable train/test splits - logged as artifacts in MLflow';


-- =====================================================
-- PAPER REPRODUCIBILITY METADATA
-- =====================================================

-- Minimal metadata (MLflow stores most of this)
CREATE TABLE experiment_metadata (
    metadata_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR(255) NOT NULL,
    paper_section VARCHAR(100),

    -- MLflow links
    mlflow_experiment_id VARCHAR(255),
    mlflow_run_ids TEXT[], -- Multiple runs for same paper section

    -- Paper-specific (not in MLflow)
    dataset_doi TEXT,
    key_findings TEXT,
    figures_tables_generated TEXT[],

    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE experiment_metadata IS 'Links paper sections to MLflow experiments for reproducibility';


-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: Match success rate by algorithm (with MLflow integration)
CREATE VIEW v_algorithm_success_rates AS
SELECT 
    mr.algorithm_used,
    mr.algorithm_version,
    mr.mlflow_experiment_name,
    COUNT(m.match_id) as total_matches,
    AVG(f.overall_rating) as avg_satisfaction,
    COUNT(CASE WHEN f.overall_rating >= 4 THEN 1 END)::FLOAT / NULLIF(COUNT(m.match_id), 0) as success_rate,
    AVG(mo.retention_days) as avg_retention_days,
    mr.mlflow_run_id
FROM matching_rounds mr
JOIN matches m ON mr.matching_round_id = m.matching_round_id
LEFT JOIN feedbacks f ON m.match_id = f.match_id
LEFT JOIN match_outcomes mo ON m.match_id = mo.match_id
GROUP BY mr.algorithm_used, mr.algorithm_version, mr.mlflow_experiment_name, mr.mlflow_run_id;


-- View: MLflow experiment summary
CREATE VIEW v_mlflow_experiment_summary AS
SELECT 
    mr.mlflow_experiment_name,
    mr.mlflow_run_id,
    mr.algorithm_used,
    mr.started_at,
    mr.completed_at,
    COUNT(m.match_id) as total_matches,
    AVG(m.final_combined_score) as avg_match_score,
    AVG(mo.satisfaction_score) as avg_satisfaction,
    COUNT(mo.outcome_id) as outcomes_recorded
FROM matching_rounds mr
LEFT JOIN matches m ON mr.matching_round_id = m.matching_round_id
LEFT JOIN match_outcomes mo ON m.match_id = mo.match_id
WHERE mr.mlflow_run_id IS NOT NULL
GROUP BY mr.mlflow_experiment_name, mr.mlflow_run_id, mr.algorithm_used, mr.started_at, mr.completed_at;

COMMENT ON VIEW v_mlflow_experiment_summary IS 'Quick overview of all MLflow-tracked experiments';


-- =====================================================
-- TRIGGERS FOR AUTOMATION
-- =====================================================

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_mentee_updated_at BEFORE UPDATE ON mentee_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_mentor_updated_at BEFORE UPDATE ON mentor_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- Update match status timestamp
CREATE OR REPLACE FUNCTION update_match_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status != OLD.status THEN
        NEW.status_updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_match_status_update 
BEFORE UPDATE ON matches 
FOR EACH ROW EXECUTE FUNCTION update_match_status_timestamp();


-- =====================================================
-- DOCUMENTATION COMMENTS
-- =====================================================

COMMENT ON DATABASE mentorship_db IS 'Mentor matching system optimized for MLflow integration';
COMMENT ON TABLE matching_rounds IS 'Each row links to one MLflow experiment run - detailed metrics stored in MLflow';
COMMENT ON TABLE matches IS 'Production matches with MLflow traceability for reproducibility';
COMMENT ON TABLE match_outcomes IS 'Ground truth outcomes linked to MLflow experiments for algorithm comparison';
COMMENT ON COLUMN embeddings.embedding_vector IS 'pgvector dimension: 768 for sentence-transformers, 1536 for OpenAI';

-- =====================================================
-- END OF SCHEMA
-- =====================================================
