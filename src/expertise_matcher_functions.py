from typing import Tuple, Dict
import pandas as pd
import numpy as np

def extract_expertise_column(expertise_matrix: np.ndarray, area: int) -> np.ndarray:
    """
    Extract a specific expertise area column from the matrix.
    
    Parameters:
    -----------
    expertise_matrix : np.ndarray
        Shape (n, 3) - expertise matrix
    area : int
        Area number (0,1, or 2)
    
    Returns:
    --------
    np.ndarray
        Column vector of shape (n,)
    """
    return expertise_matrix[:, area]


def compute_difference_matrix(mentee_col: np.ndarray, mentor_col: np.ndarray) -> np.ndarray:
    """
    Compute pairwise differences between mentor and mentee expertise levels.
    
    Parameters:
    -----------
    mentee_col : np.ndarray
        Shape (n,) - mentee expertise values
    mentor_col : np.ndarray
        Shape (m,) - mentor expertise values
    
    Returns:
    --------
    np.ndarray
        Shape (n, m) - matrix where element [i,j] = mentor[j] - mentee[i]
    """
    return mentor_col[None, :] - mentee_col[:, None]


def create_expertise_mask(difference_matrix: np.ndarray, 
                          target_differences: Tuple[float, ...] = (0.2, 0.4)) -> np.ndarray:
    """
    Create boolean mask for differences close to target values.
    
    Parameters:
    -----------
    difference_matrix : np.ndarray
        Shape (n, m) - matrix of expertise differences
    target_differences : tuple of float
        Target difference values to match (default: 0.2 and 0.4)
    
    Returns:
    --------
    np.ndarray
        Shape (n, m) - boolean matrix, True where difference matches any target
    """
    mask = np.zeros_like(difference_matrix, dtype=bool)
    for target in target_differences:
        mask |= np.isclose(difference_matrix, target)
    return mask


def generate_area_combination_key(mentee_area: int, mentor_area: int) -> str:
    """
    Generate standardized key for mentee-mentor area combination.
    
    Parameters:
    -----------
    mentee_area : int
        Mentee expertise area (1, 2, or 3)
    mentor_area : int
        Mentor expertise area (1, 2, or 3)
    
    Returns:
    --------
    str
        Key in format "mentee_area{X}_to_mentor_area{Y}"
    """
    return f"mentee_area{mentee_area}_to_mentor_area{mentor_area}"


def calculate_expertise_differences(
    mentors_expertise_matrix: np.ndarray,
    mentees_expertise_matrix: np.ndarray
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:    
    """
    Calculate expertise differences between mentees and mentors across all area combinations.
    
    Parameters:
    -----------
    mentees_expertise_matrix : np.ndarray
        Shape (n, 3) - n mentees, 3 expertise areas
    mentors_expertise_matrix : np.ndarray
        Shape (m, 3) - m mentors, 3 expertise areas
    
    Returns:
    --------
    expertise_differences : dict
        Dictionary with 9 keys, each containing an (n, m) matrix of differences
    expertise_difference_mask : dict
        Dictionary with 9 keys, each containing an (n, m) boolean matrix
        True where differences are close to 0.2 or 0.4
    """
    expertise_differences = {}
    expertise_difference_mask = {}
    
    for mentee_area in range(0, 3):
        for mentor_area in range(0, 3):
            # Generate key for this combination
            key = generate_area_combination_key(mentee_area, mentor_area)
            
            # Extract columns for this area combination
            mentee_col = extract_expertise_column(mentees_expertise_matrix, mentee_area)
            mentor_col = extract_expertise_column(mentors_expertise_matrix, mentor_area)
            
            # Compute difference matrix
            difference_matrix = compute_difference_matrix(mentee_col, mentor_col)
            expertise_differences[key] = difference_matrix
            
            # Create mask for target differences
            mask = create_expertise_mask(difference_matrix)
            expertise_difference_mask[key] = mask
    
    return expertise_differences, expertise_difference_mask