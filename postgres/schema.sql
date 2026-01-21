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
    
    -- Profile Completeness (for cold-start analysis)
    -- profile_completeness_score FLOAT DEFAULT 0.0,
    -- eliminated this profile_completeness because almost everyone's will be complete
    
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
    
    -- Profile Completeness
    -- profile_completeness_score FLOAT DEFAULT 0.0,
    
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
    embedding_vector vector(768), -- Adjust dimension based on model
    dimension INTEGER,
    model_used VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);

-- Feature matrix cache for faster computation
CREATE TABLE computed_features (
    feature_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_profile_id UUID REFERENCES mentor_profiles(mentor_profile_id) ON DELETE CASCADE,
    mentee_profile_id UUID REFERENCES mentee_profiles(mentee_profile_id) ON DELETE CASCADE,
    feature_vector JSONB, -- Store as JSON for flexibility
    feature_version VARCHAR(50),
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (mentor_profile_id IS NOT NULL AND mentee_profile_id IS NULL) OR
        (mentor_profile_id IS NULL AND mentee_profile_id IS NOT NULL)
    )
);

-- =====================================================
-- ALGORITHM CONFIGURATION & EXPERIMENTATION
-- =====================================================

-- Algorithm configurations for reproducibility
CREATE TABLE algorithm_configurations (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    algorithm_name VARCHAR(100) NOT NULL, -- 'Gale-Shapley', 'Hungarian', 'Neural-CF', 'Genetic', 'Thompson-Sampling'
    algorithm_version VARCHAR(50),
    algorithm_category VARCHAR(50), -- 'stable-matching', 'optimization', 'collaborative-filtering', 'hybrid'
    
    -- Hyperparameters (stored as JSON for flexibility)
    hyperparameters JSONB,
    
    -- Feature weights
    semantic_weight FLOAT, --mentorship areas
    personality_weight FLOAT, --answer to personality type 
    hobby_weight FLOAT, --about me/hobby section
    expertise_weight FLOAT, --expertise rating 
    
    -- Model-specific parameters
    embedding_dim INTEGER,
    learning_rate FLOAT,
    regularization_lambda FLOAT,
    num_iterations INTEGER,
    
    description TEXT, --description of the exact implementation of the algorithm we're performing
    paper_reference TEXT, -- Citation if implementing published algorithm
    code_repository_url TEXT, -- For reproducibility/ your exact commit version or the paper's code implementation
    
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dataset splits for proper evaluation
CREATE TABLE dataset_splits (
    split_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    split_name VARCHAR(100) NOT NULL, -- 'train', 'validation', 'test'
    split_strategy VARCHAR(100), -- 'temporal', 'random', 'leave-one-out', 'k-fold'
    split_ratio FLOAT,
    temporal_cutoff_date TIMESTAMP, -- For temporal splits
    fold_number INTEGER, -- For k-fold cross-validation
    
    -- User/profile assignments
    mentor_ids UUID[],
    mentee_ids UUID[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matching rounds (experimental runs)
CREATE TABLE matching_rounds (
    matching_round_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_name VARCHAR(255),
    config_id UUID REFERENCES algorithm_configurations(config_id),
    split_id UUID REFERENCES dataset_splits(split_id),
    
    -- Algorithm metadata
    algorithm_used VARCHAR(100) NOT NULL,
    algorithm_version VARCHAR(50),
    
    -- Execution metadata
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_seconds FLOAT,
    execution_environment JSONB, -- {cpu_cores, memory_gb, gpu_type}
    
    -- Dataset characteristics
    total_mentors INTEGER,
    total_mentees INTEGER,
    -- avg_profile_completeness FLOAT,
    
    -- Results summary
    successful_matches INTEGER,
    avg_match_score FLOAT,
    median_match_score FLOAT,
    std_match_score FLOAT,
    
    -- Algorithm-specific metrics
    convergence_iterations INTEGER,
    stability_violations INTEGER, -- For Gale-Shapley
    optimization_objective_value FLOAT, -- For Hungarian/Genetic
    
    -- Reproducibility
    random_seed INTEGER,
    algorithm_parameters JSONB,
    
    notes TEXT,
    -- Keep one is_baseline = TRUE per experiment_group
    is_baseline BOOLEAN DEFAULT FALSE,
    experiment_group VARCHAR(100) -- For grouping related experiments
);

-- =====================================================
-- PREFERENCE & RANKING TABLES (for Stable Matching)
-- =====================================================

-- Preference rankings (critical for Gale-Shapley)
CREATE TABLE preference_rankings (
    ranking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id) ON DELETE CASCADE,
    ranker_id UUID NOT NULL, -- user_id of person ranking
    ranker_role VARCHAR(10) CHECK (ranker_role IN ('mentor', 'mentee')),
    ranked_profile_id UUID NOT NULL, -- profile_id being ranked
    rank_position INTEGER NOT NULL, -- 1 = most preferred
    computed_score FLOAT, -- The score used to generate this rank
    score_components JSONB, -- Breakdown of score components
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(matching_round_id, ranker_id, rank_position)
);

CREATE INDEX idx_pref_round_ranker ON preference_rankings(matching_round_id, ranker_id);

-- =====================================================
-- MATCHING & PAIRING TABLES
-- =====================================================

-- Potential pairings (all computed candidates)
CREATE TABLE potential_pairings (
    pairing_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id) ON DELETE CASCADE,
    
    -- Similarity scores
    semantic_similarity_score FLOAT,
    personality_compatibility_score FLOAT,
    hobby_bonus_score FLOAT,
    experience_match_score FLOAT,
    
    -- Combined scores
    final_combined_score FLOAT,
    normalized_score FLOAT, -- Min-max normalized
    percentile_rank FLOAT, -- Percentile among all pairings
    
    -- Selection metadata
    selected BOOLEAN DEFAULT FALSE,
    selection_reason TEXT, -- 'algorithm', 'manual_override', 'diversity_constraint'
    rank_for_mentor INTEGER, -- Mentee's rank in mentor's preference list
    rank_for_mentee INTEGER, -- Mentor's rank in mentee's preference list
    
    -- Detailed score breakdown
    score_components JSONB,
    
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_potential_round ON potential_pairings(matching_round_id);
CREATE INDEX idx_potential_selected ON potential_pairings(matching_round_id, selected);

-- Actual matches (final assignments)
CREATE TABLE matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id),
    
    -- Match status
    status VARCHAR(20) CHECK (status IN ('pending', 'active', 'completed', 'declined', 'terminated')),
    
    -- Algorithm that produced this match
    matching_algorithm VARCHAR(100),
    config_id UUID REFERENCES algorithm_configurations(config_id),
    
    -- Compatibility scores (copied from potential_pairings)
    semantic_similarity_score FLOAT,
    personality_compatibility_score FLOAT,
    hobby_bonus_score FLOAT,
    experience_match_score FLOAT,
    final_combined_score FLOAT,
    
    -- Timestamps
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_interaction_at TIMESTAMP,
    last_interaction_at TIMESTAMP,
    
    -- Outcome tracking
    actual_satisfaction_score FLOAT, -- Ground truth from feedback
    predicted_satisfaction_score FLOAT, -- Model prediction
    prediction_error FLOAT, -- For model evaluation
    
    notes TEXT,
    
    UNIQUE(mentor_id, mentee_id, matching_round_id)
);

CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_match_round ON matches(matching_round_id);
CREATE INDEX idx_match_timestamp ON matches(matched_at);

-- =====================================================
-- STABILITY & QUALITY METRICS
-- =====================================================

-- Match stability analysis
CREATE TABLE match_stability_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(match_id) ON DELETE CASCADE,
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id),
    
    -- Stability indicators
    is_blocking_pair BOOLEAN DEFAULT FALSE,
    blocking_with_mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    blocking_with_mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),
    
    -- Preference satisfaction
    mentor_rank_of_mentee INTEGER, -- Where mentee ranked for mentor
    mentee_rank_of_mentor INTEGER, -- Where mentor ranked for mentee
    mutual_rank_product INTEGER, -- Lower is better
    
    -- Engagement & retention
    engagement_score FLOAT,
    interaction_count INTEGER DEFAULT 0,
    avg_interaction_quality FLOAT,
    retention_days INTEGER,
    is_early_termination BOOLEAN DEFAULT FALSE,
    early_termination_reason TEXT,
    
    -- Diversity metrics (for fairness analysis)
    mentor_mentee_similarity_score FLOAT,
    diversity_contribution_score FLOAT,
    
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stability_match ON match_stability_metrics(match_id);
CREATE INDEX idx_stability_blocking ON match_stability_metrics(is_blocking_pair);


-- =====================================================
-- FEEDBACK & EVALUATION
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
    
    -- Feedback timing (for temporal analysis)
    weeks_since_match INTEGER,
    feedback_round INTEGER, -- 1st feedback, 2nd feedback, etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_match ON feedbacks(match_id);
CREATE INDEX idx_feedback_role ON feedbacks(reviewer_role);


-- =====================================================
-- =====================================================

-- ESPAXI ALGORTIHMS KO PERFORMANCE, ESPAXI KK XA SCHEMA MA, MAILE BUJEKO XAINA

-- =====================================================
-- =====================================================
-- =====================================================

-- Algorithm performance summary (for Tables/Figures in paper)
CREATE TABLE algorithm_performance_summary (
    summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matching_round_id UUID REFERENCES matching_rounds(matching_round_id) ON DELETE CASCADE,
    config_id UUID REFERENCES algorithm_configurations(config_id),
    
    -- Classification metrics
    accuracy_score FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    auc_roc FLOAT,
    
    -- Ranking metrics (critical for RecSys)
    ndcg_at_5 FLOAT,
    ndcg_at_10 FLOAT,
    map_score FLOAT, -- Mean Average Precision
    mrr_score FLOAT, -- Mean Reciprocal Rank
    hit_rate_at_5 FLOAT,
    hit_rate_at_10 FLOAT,
    
    -- Satisfaction metrics
    avg_mentor_satisfaction FLOAT,
    avg_mentee_satisfaction FLOAT,
    satisfaction_std_dev FLOAT,
    satisfaction_variance FLOAT,
    
    -- Stability metrics (for stable matching algorithms)
    blocking_pairs_count INTEGER,
    stable_match_percentage FLOAT,
    avg_rank_product FLOAT,
    
    -- Diversity & fairness
    gini_coefficient FLOAT, -- Distribution fairness
    exposure_diversity_score FLOAT,
    demographic_parity_difference FLOAT,
    
    -- Efficiency metrics
    computational_time_ms FLOAT,
    memory_usage_mb FLOAT,
    scalability_factor FLOAT, -- Time per 1000 users
    
    -- Outcome metrics
    match_retention_rate_30d FLOAT,
    match_retention_rate_90d FLOAT,
    avg_interaction_frequency FLOAT,
    avg_skill_improvement_score FLOAT,
    goal_completion_rate FLOAT,
    
    -- Cold-start performance
    cold_start_accuracy FLOAT, -- Performance on users with <3 interactions
    warm_start_accuracy FLOAT,
    
    -- Statistical significance
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,
    p_value FLOAT, -- Compared to baseline
    
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_perf_round ON algorithm_performance_summary(matching_round_id);
CREATE INDEX idx_perf_config ON algorithm_performance_summary(config_id);

-- =====================================================
-- GROUND TRUTH & VALIDATION
-- =====================================================

-- Ground truth for supervised learning validation
CREATE TABLE ground_truth_matches (
    ground_truth_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID REFERENCES mentor_profiles(mentor_profile_id),
    mentee_id UUID REFERENCES mentee_profiles(mentee_profile_id),
    
    -- Success indicators
    is_successful BOOLEAN NOT NULL,
    success_score FLOAT CHECK (success_score BETWEEN 0 AND 10),
    
    -- Success factors breakdown
    success_factors JSONB, -- {skill_growth: 8, goal_achievement: 9, satisfaction: 7, retention: 6}
    
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

-- =====================================================
-- A/B TESTING & ONLINE EVALUATION
-- =====================================================

-- A/B test experiments
CREATE TABLE ab_test_experiments (
    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR(255) NOT NULL,
    
    -- Experiment design
    control_config_id UUID REFERENCES algorithm_configurations(config_id),
    treatment_config_id UUID REFERENCES algorithm_configurations(config_id),
    
    -- Traffic allocation
    traffic_split_ratio FLOAT DEFAULT 0.5, -- 50-50 split
    
    -- Timing
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    target_sample_size INTEGER,
    
    -- Primary metrics
    primary_metric VARCHAR(100), -- 'satisfaction', 'retention', 'engagement'
    secondary_metrics TEXT[],
    
    -- Results
    control_metric_value FLOAT,
    treatment_metric_value FLOAT,
    lift_percentage FLOAT,
    statistical_significance FLOAT,
    p_value FLOAT,
    confidence_level FLOAT DEFAULT 0.95,
    
    -- Status
    status VARCHAR(50) CHECK (status IN ('draft', 'running', 'completed', 'cancelled')),
    winner VARCHAR(50) CHECK (winner IN ('control', 'treatment', 'no_difference')),
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User assignment to A/B test buckets
CREATE TABLE ab_test_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES ab_test_experiments(experiment_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id),
    bucket VARCHAR(50) CHECK (bucket IN ('control', 'treatment')),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(experiment_id, user_id)
);

-- =====================================================
-- COLD START TRACKING
-- =====================================================

-- Cold start user tracking
CREATE TABLE cold_start_users (
    cold_start_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    user_role VARCHAR(10) CHECK (user_role IN ('mentor', 'mentee')),
    
    -- Cold start categorization
    interaction_count INTEGER DEFAULT 0,
    is_cold_start BOOLEAN DEFAULT TRUE, -- <3 interactions
    cold_start_category VARCHAR(50), -- 'new_user', 'new_item', 'sparse_data'
    
    -- Mitigation strategy applied
    strategy_used VARCHAR(100), -- 'content_based', 'popularity', 'hybrid', 'transfer_learning'
    
    -- Performance tracking
    match_quality_score FLOAT,
    satisfaction_score FLOAT,
    
    transitioned_to_warm_at TIMESTAMP, -- When they got >3 interactions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cold_start_user ON cold_start_users(user_id);
CREATE INDEX idx_cold_start_category ON cold_start_users(is_cold_start);

-- =====================================================
-- REPRODUCIBILITY & METADATA
-- =====================================================

-- Experiment metadata for paper reproducibility
CREATE TABLE experiment_metadata (
    metadata_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR(255) NOT NULL,
    paper_section VARCHAR(100), -- 'Section 4.2', 'Figure 3', 'Table 2'
    
    -- Associated runs
    matching_round_ids UUID[],
    
    -- Environment
    python_version VARCHAR(50),
    library_versions JSONB, -- {pandas: '1.5.0', scikit-learn: '1.2.0'}
    hardware_specs JSONB,
    
    -- Dataset info
    dataset_version VARCHAR(50),
    preprocessing_steps TEXT[],
    
    -- Code & data
    code_repository_url TEXT,
    code_commit_hash VARCHAR(255),
    dataset_doi TEXT,
    
    -- Results
    key_findings TEXT,
    figures_tables_generated TEXT[],
    
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View: Match success rate by algorithm
CREATE VIEW v_algorithm_success_rates AS
SELECT 
    mr.algorithm_used,
    mr.algorithm_version,
    COUNT(m.match_id) as total_matches,
    AVG(f.overall_rating) as avg_satisfaction,
    COUNT(CASE WHEN f.overall_rating >= 4 THEN 1 END)::FLOAT / COUNT(m.match_id) as success_rate,
    AVG(msm.retention_days) as avg_retention_days
FROM matching_rounds mr
JOIN matches m ON mr.matching_round_id = m.matching_round_id
LEFT JOIN feedbacks f ON m.match_id = f.match_id
LEFT JOIN match_stability_metrics msm ON m.match_id = msm.match_id
GROUP BY mr.algorithm_used, mr.algorithm_version;

-- View: Cold start performance comparison
CREATE VIEW v_cold_start_performance AS
SELECT 
    csu.strategy_used,
    csu.user_role,
    COUNT(*) as user_count,
    AVG(csu.match_quality_score) as avg_match_quality,
    AVG(csu.satisfaction_score) as avg_satisfaction,
    AVG(EXTRACT(EPOCH FROM (csu.transitioned_to_warm_at - csu.created_at))/86400) as avg_days_to_warm
FROM cold_start_users csu
WHERE csu.transitioned_to_warm_at IS NOT NULL
GROUP BY csu.strategy_used, csu.user_role;

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Vector similarity search indexes
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_embeddings_type ON embeddings(embedding_type);

-- User and profile indexes
CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_user_registration ON users(registration_date);
CREATE INDEX idx_mentee_completeness ON mentee_profiles(profile_completeness_score);
CREATE INDEX idx_mentor_completeness ON mentor_profiles(profile_completeness_score);

-- Matching round indexes
CREATE INDEX idx_round_algorithm ON matching_rounds(algorithm_used);
CREATE INDEX idx_round_date ON matching_rounds(started_at);
CREATE INDEX idx_round_config ON matching_rounds(config_id);

-- Performance query indexes
CREATE INDEX idx_match_round_status ON matches(matching_round_id, status);
CREATE INDEX idx_feedback_timestamp ON feedbacks(created_at);
CREATE INDEX idx_interaction_timestamp ON match_interactions(interaction_date);

-- =====================================================
-- TRIGGERS FOR AUTOMATION
-- =====================================================

-- Update profile completeness automatically
CREATE OR REPLACE FUNCTION calculate_profile_completeness()
RETURNS TRIGGER AS $$
DECLARE
    completeness FLOAT;
    filled_fields INTEGER;
    total_fields INTEGER;
BEGIN
    IF TG_TABLE_NAME = 'mentee_profiles' THEN
        total_fields := 14; -- Count of key profile fields
        filled_fields := 0;
        
        IF NEW.main_interest IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.main_interest_level IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.additional_interest IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.future_aspirations IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.primary_motivation IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.goal_approach IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.communication_style IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.feedback_preference IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        IF NEW.commitment_style IS NOT NULL THEN filled_fields := filled_fields + 1; END IF;
        
        NEW.profile_completeness_score := filled_fields::FLOAT / total_fields;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_mentee_completeness
BEFORE INSERT OR UPDATE ON mentee_profiles
FOR EACH ROW EXECUTE FUNCTION calculate_profile_completeness();

CREATE TRIGGER trg_mentor_completeness
BEFORE INSERT OR UPDATE ON mentor_profiles
FOR EACH ROW EXECUTE FUNCTION calculate_profile_completeness();

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

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE matching_rounds IS 'Each row represents one experimental run of a matching algorithm';
COMMENT ON TABLE algorithm_configurations IS 'Stores all hyperparameters for reproducibility per ACM guidelines';
COMMENT ON TABLE algorithm_performance_summary IS 'Pre-computed metrics for paper tables and figures';
COMMENT ON TABLE ground_truth_matches IS 'Validated successful matches for supervised learning evaluation';
COMMENT ON TABLE ab_test_experiments IS 'Online A/B test tracking for real-world deployment validation';
COMMENT ON COLUMN embeddings.embedding_vector IS 'Adjust dimension based on embedding model (768 for BERT, 1536 for OpenAI)';
COMMENT ON COLUMN algorithm_performance_summary.ndcg_at_10 IS 'Normalized Discounted Cumulative Gain - standard RecSys metric';
