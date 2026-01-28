"""
Enhanced config-based experiment runner
Supports multiple algorithms defined in YAML
"""

import sys
from pathlib import Path

# Add project root to path so we can import from root directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import yaml
import mlflow
import numpy as np
import pandas as pd
from typing import Dict, List
from mentor_matching_system import MentorMatchingSystem
from test_utilities import TestDatabaseHelper


# =====================================================
# ALGORITHM IMPLEMENTATIONS
# =====================================================

def greedy_algorithm(matcher: MentorMatchingSystem, params: Dict) -> List[Dict]:
    """Standard greedy matching with configurable weights."""
    # Override weights if provided
    if 'semantic_weight' in params or 'expertise_weight' in params:
        sem_weight = params.get('semantic_weight', 0.7)
        exp_weight = params.get('expertise_weight', 0.3)

        # Temporarily override the calculation method
        original_calc = matcher.calculate_combined_score
        matcher.calculate_combined_score = lambda s, e: (sem_weight * s) + (exp_weight * e)
        matches = matcher.generate_matches()
        matcher.calculate_combined_score = original_calc
    else:
        matches = matcher.generate_matches()

    return matches


def random_matching(matcher: MentorMatchingSystem, params: Dict) -> List[Dict]:
    """Random matching with capacity constraints (baseline)."""
    import random

    random.seed(params.get('random_seed', 42))

    mentors = matcher.get_all_mentors()
    mentees = matcher.get_all_mentees()

    random.shuffle(mentees)

    matches = []
    mentor_capacity = {m['mentor_profile_id']: 
                      m['max_mentee_capacity'] - m['current_mentee_count'] 
                      for m in mentors}

    for mentee in mentees:
        available = [m for m in mentors if mentor_capacity.get(m['mentor_profile_id'], 0) > 0]

        if not available:
            continue

        mentor = random.choice(available)

        semantic = matcher.calculate_semantic_similarity(
            mentee['embedding_vector'],
            mentor['embedding_vector']
        )
        expertise = matcher.calculate_expertise_score(
            mentee['main_interest_level'],
            mentor['expertise_level']
        )
        combined = matcher.calculate_combined_score(semantic, expertise)

        matches.append({
            'mentee_id': mentee['mentee_profile_id'],
            'mentor_id': mentor['mentor_profile_id'],
            'semantic_score': semantic,
            'expertise_score': expertise,
            'final_score': combined
        })

        mentor_capacity[mentor['mentor_profile_id']] -= 1

    return matches


def weighted_random_matching(matcher: MentorMatchingSystem, params: Dict) -> List[Dict]:
    """Probabilistic matching weighted by similarity scores."""
    import random

    random.seed(params.get('random_seed', 42))

    mentors = matcher.get_all_mentors()
    mentees = matcher.get_all_mentees()

    matches = []
    mentor_capacity = {m['mentor_profile_id']: 
                      m['max_mentee_capacity'] - m['current_mentee_count'] 
                      for m in mentors}

    for mentee in mentees:
        available = [m for m in mentors if mentor_capacity.get(m['mentor_profile_id'], 0) > 0]

        if not available:
            continue

        scores = []
        for mentor in available:
            semantic = matcher.calculate_semantic_similarity(
                mentee['embedding_vector'],
                mentor['embedding_vector']
            )
            expertise = matcher.calculate_expertise_score(
                mentee['main_interest_level'],
                mentor['expertise_level']
            )
            combined = matcher.calculate_combined_score(semantic, expertise)
            scores.append(combined)

        # Sample with probability proportional to score
        probabilities = np.array(scores) / sum(scores)
        chosen_idx = np.random.choice(len(available), p=probabilities)
        chosen_mentor = available[chosen_idx]

        semantic = matcher.calculate_semantic_similarity(
            mentee['embedding_vector'],
            chosen_mentor['embedding_vector']
        )
        expertise = matcher.calculate_expertise_score(
            mentee['main_interest_level'],
            chosen_mentor['expertise_level']
        )

        matches.append({
            'mentee_id': mentee['mentee_profile_id'],
            'mentor_id': chosen_mentor['mentor_profile_id'],
            'semantic_score': semantic,
            'expertise_score': expertise,
            'final_score': scores[chosen_idx]
        })

        mentor_capacity[chosen_mentor['mentor_profile_id']] -= 1

    return matches


def top_k_matching(matcher: MentorMatchingSystem, params: Dict) -> List[Dict]:
    """
    Each mentee gets matched to best mentor from top K candidates.
    Adds diversity by not always picking absolute best.
    """
    import random

    k = params.get('top_k', 3)
    random.seed(params.get('random_seed', 42))

    mentors = matcher.get_all_mentors()
    mentees = matcher.get_all_mentees()

    matches = []
    mentor_capacity = {m['mentor_profile_id']: 
                      m['max_mentee_capacity'] - m['current_mentee_count'] 
                      for m in mentors}

    for mentee in mentees:
        available = [m for m in mentors if mentor_capacity.get(m['mentor_profile_id'], 0) > 0]

        if not available:
            continue

        # Calculate scores for all available mentors
        mentor_scores = []
        for mentor in available:
            semantic = matcher.calculate_semantic_similarity(
                mentee['embedding_vector'],
                mentor['embedding_vector']
            )
            expertise = matcher.calculate_expertise_score(
                mentee['main_interest_level'],
                mentor['expertise_level']
            )
            combined = matcher.calculate_combined_score(semantic, expertise)
            mentor_scores.append((mentor, semantic, expertise, combined))

        # Sort by combined score and take top K
        mentor_scores.sort(key=lambda x: x[3], reverse=True)
        top_k_mentors = mentor_scores[:min(k, len(mentor_scores))]

        # Randomly pick from top K
        chosen = random.choice(top_k_mentors)
        mentor, semantic, expertise, combined = chosen

        matches.append({
            'mentee_id': mentee['mentee_profile_id'],
            'mentor_id': mentor['mentor_profile_id'],
            'semantic_score': semantic,
            'expertise_score': expertise,
            'final_score': combined
        })

        mentor_capacity[mentor['mentor_profile_id']] -= 1

    return matches


# Algorithm registry - maps string names to functions
ALGORITHMS = {
    'greedy': greedy_algorithm,
    'random': random_matching,
    'weighted_random': weighted_random_matching,
    'top_k': top_k_matching
}


# =====================================================
# EXPERIMENT RUNNER
# =====================================================

def run_from_config(config_file: str):
    """Run experiments from YAML config file with algorithm selection."""

    # Load config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    db_config = config['database']['connection_string']
    experiment_name = config['experiment']['name']

    mlflow.set_experiment(experiment_name)
    test_helper = TestDatabaseHelper(db_config)

    results = []

    print(f"\n🚀 Starting experiment: {experiment_name}")
    print(f"   Running {len(config['runs'])} experiments...\n")

    for run_config in config['runs']:
        run_name = run_config['name']
        params = run_config['parameters']
        algorithm_name = params.get('algorithm', 'greedy')

        # Get algorithm function
        if algorithm_name not in ALGORITHMS:
            print(f"⚠️  Unknown algorithm '{algorithm_name}', skipping {run_name}")
            continue

        algorithm_func = ALGORITHMS[algorithm_name]

        with mlflow.start_run(run_name=run_name):

            # Log all parameters
            for key, value in params.items():
                mlflow.log_param(key, value)

            # Clear matches
            test_helper.clear_matches()

            # Run selected algorithm
            matcher = MentorMatchingSystem(db_config)
            matches = algorithm_func(matcher, params)

            # Calculate metrics
            if matches:
                scores = [m['final_score'] for m in matches]
                semantic_scores = [m['semantic_score'] for m in matches]
                expertise_scores = [m['expertise_score'] for m in matches]

                mentees = matcher.get_all_mentees()

                metrics = {
                    'total_matches': len(matches),
                    'avg_final_score': np.mean(scores),
                    'std_final_score': np.std(scores),
                    'min_final_score': np.min(scores),
                    'max_final_score': np.max(scores),
                    'avg_semantic_score': np.mean(semantic_scores),
                    'avg_expertise_score': np.mean(expertise_scores),
                    'coverage_rate': len(set(m['mentee_id'] for m in matches)) / len(mentees)
                }
            else:
                metrics = {'total_matches': 0}

            # Log metrics
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

            # Save artifacts
            if matches:
                df = pd.DataFrame(matches)
                artifact_name = f"matches_{run_name}.csv"
                df.to_csv(artifact_name, index=False)
                mlflow.log_artifact(artifact_name)

                # Clean up local file
                import os
                os.remove(artifact_name)

            # Save to database
            matcher.save_matches_to_db(matches)
            matcher.close()

            print(f"✅ {run_name:30s} [{algorithm_name:15s}] avg_score={metrics.get('avg_final_score', 0):.4f}")

            results.append({**params, **metrics, 'run_name': run_name})

    test_helper.close()

    # Save comparison summary
    df = pd.DataFrame(results)
    df.to_csv("experiment_results.csv", index=False)

    print(f"\n{'='*60}")
    print("  EXPERIMENT SUMMARY")
    print(f"{'='*60}")

    if len(df) > 0 and 'avg_final_score' in df.columns:
        best_idx = df['avg_final_score'].idxmax()
        best_run = df.loc[best_idx]

        print(f"\n🏆 Best Run: {best_run['run_name']}")
        print(f"   Algorithm: {best_run.get('algorithm', 'unknown')}")
        print(f"   Score: {best_run['avg_final_score']:.4f}")
        print(f"   Coverage: {best_run.get('coverage_rate', 0):.2%}")

    print(f"\n📊 Results saved to: experiment_results.csv")
    print(f"🔍 View in MLflow: mlflow ui --port 5000")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_config_experiments.py <config_file.yaml>")
        print("\nAvailable algorithms:")
        for algo_name in ALGORITHMS.keys():
            print(f"  - {algo_name}")
        sys.exit(1)

    run_from_config(sys.argv[1])
