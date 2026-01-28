-- migration_add_mlflow.sql
-- Run this to add MLflow integration to existing schema

-- Add MLflow column to matches
ALTER TABLE matches 
ADD COLUMN mlflow_run_id VARCHAR(255);

CREATE INDEX idx_matches_mlflow ON matches(mlflow_run_id);

-- Create matching_rounds table
CREATE TABLE matching_rounds (
    matching_round_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_name VARCHAR(255),
    mlflow_run_id VARCHAR(255) UNIQUE,
    mlflow_experiment_name VARCHAR(255),
    algorithm_used VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_matches INTEGER,
    avg_match_score FLOAT,
    random_seed INTEGER
);

-- Link matches to rounds
ALTER TABLE matches 
ADD COLUMN matching_round_id UUID REFERENCES matching_rounds(matching_round_id);

-- Create outcomes table
CREATE TABLE match_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID REFERENCES matches(match_id) ON DELETE CASCADE,
    mlflow_run_id VARCHAR(255),
    is_successful BOOLEAN,
    satisfaction_score FLOAT CHECK (satisfaction_score BETWEEN 0 AND 10),
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(match_id, evaluation_date)
);

CREATE INDEX idx_outcome_mlflow ON match_outcomes(mlflow_run_id);
