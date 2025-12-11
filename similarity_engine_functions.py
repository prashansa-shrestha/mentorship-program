import numpy as np
import pandas as pd
from preprocessor import mentors_mbti, mentees_mbti, n_mentors, n_mentees
from concatenator import mentors_expertise_matrix, mentees_expertise_matrix

mbti_types = [
    "ENFJ",
    "ENFP",
    "ENTJ",
    "ENTP",
    "ESFJ",
    "ESFP",
    "ESTJ",
    "ESTP",
    "INFJ",
    "INFP",
    "INTJ",
    "INTP",
    "ISFJ",
    "ISFP",
    "ISTJ",
    "ISTP",
]


def normalize(matrix: np.ndarray):
    """
    Normalizes the rows of the matrix passed

    Parameters:
        matrix(numpy.ndarray):
            A 2D numpy array where each row represents a feature vector

    Returns:
        normalized_matrix(numpy.ndarray):
            A row-normalized 2D numpy array
    """
    row_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    row_norms[row_norms == 0] = 1
    normalized_matrix = matrix / row_norms
    return normalized_matrix


def cosine_similarity_matrix(mentors: np.ndarray, mentees: np.ndarray):
    """
    Calculates similarity score between n mentees and m mentors

    Parameters:
        mentors(numpy.ndarray):
            A 2D numpy array representing feature vectors of mentors
        mentees(numpy.ndarray):
            A 2D numpy array representing feature vectors of mentees


    Returns:
        similarity_matrix(numpy.ndarray):
            A 2D numpy array, where each row represents the similarity scores of a mentee with all mentors

    Example:
        Output matrix format (rows=mentees(m), columns=mentors(M))
    [
       [sim(m0,M0),sim(m0,M1),sim(m0,M2),..]
       [sim(m1,M0),sim(m1,M1),sim(m1,M2),..]
        ...
    ]
    """
    mentor_normalized = normalize(mentors)
    mentee_normalized = normalize(mentees)

    cosine_similarity_matrix = mentee_normalized @ mentor_normalized.T

    return cosine_similarity_matrix


def get_mbti_compatiblity_data(file_path:str="datasets/mbti_compatibility.csv"): 
    """
    Returns MBTI compatibility data based from the csv in the provided path

    Returns:
        mbti_compatibility_data(numpy.ndarray):
            2D arrary containing compatibility data
        
    Parameters:
        file_path(str):
            File where the compatibility data is stored
    """
    mbti_df = pd.read_csv(file_path, index_col=0)
    mbti_compatibility_data = mbti_df.to_numpy()
    return mbti_compatibility_data

def get_mbti_indices_dict():
    """
    Returns a dictionary providing indices to MBTI types

    Returns:
        mbti_dict(dict):
            Dictionary in the form:
                {
                    "type1":0
                    "type2":1
                    ...
                }
    """
    mbti_dict={mbti: i for i, mbti in enumerate(mbti_types)}
    return mbti_dict


def initialize_zero_matrix(rows:int, cols:int):
    """
    Initializes a zero matrix based on the provided dimensions (r,c)

    Returns:
        zero_matrix(numpy.ndarray):
            A 2D zero matrix of provided dimensions

    Paramteters:
        rows(int):
            Number of rows in matrix(mentees)
        
        cols(int):
            Number of columns in matrix(mentees)
    """
    zero_matrix = np.zeroes((rows, cols))
    return zero_matrix


def initialize_masking_matrix(rows:int, cols:int):
    """
    Initializes a zero matrix based on the provided dimensions (r,c)

    Returns:
        mask_matrix(numpy.ndarray):
            A 2D matrix of provided dimensions with all entires False

    Paramteters:
        rows(int):
            Number of rows in matrix(mentees)
        
        cols(int):
            Number of columns in matrix(mentees)
    """
    mask_matrix = np.zeroes((rows, cols), dtype=bool)
    return mask_matrix


def process_each_pair(type1:str,type2:str):
    """
    Calculates compatibility between two provided MBTI personality types 

    Returns:
        compatibility(float):
            Given MBTI types' compatibility score

    Parameters:
        personality_idx1(str):
            Personality type of mentee

        personality_idx2(str):
            Personality type of mentor
    """
    mbti_index=get_mbti_indices_dict()
    mbti_compatibility=get_mbti_compatiblity_data()

    # assign indices based on the MBTI type
    personality_idx1 = mbti_index[type1]
    personality_idx2 = mbti_index[type2]

    compatibility= mbti_compatibility[personality_idx1, personality_idx2]

    return compatibility


def calculate_mbti_matrices():
    """
    Computes the MBTI compatibility matrix, and the masking for each mentor and mentee pair

    Returns:
        mbti_matrix(np.ndarray):
            A 2D matrix containing MBTI compatibility values for each mentor and mentee pairs

        has_mbti_mask(np.ndarray):
            A 2D matrix denoting the existence of MBTI compatibility values for each mentor and mentee pair

    Parameters:
        no parameters :P
    """
    mbti_matrix = initialize_zero_matrix(n_mentees, n_mentors)
    has_mbti_mask =initialize_masking_matrix(n_mentees, n_mentors)


    if mentors_mbti is not None and mentees_mbti is not None:
        for i, mentee_type in enumerate(mentees_mbti):
            # i: mentee index
            # mentee_type: MBTI personality type of mentee

            for j, mentor_type in enumerate(mentors_mbti):
                # j: mentor index
                #mentor_type: MBTI personality type of mentor

                # edit the value of compatibility matrix of the specific mentor-mentee pair
                mbti_matrix[i, j] = process_each_pair(mentee_type,mentor_type)

                #edit the value of masking matrix of the specific mentor-mentee pair
                has_mbti_mask[i, j] = True
            print(f'Mentee {i} done')
        
        print(f'All mentees MBTI compatibility generated')
    
    return mbti_matrix,has_mbti_mask


def get_total_similarity_matrix(cosine_similarity_matrix:np.ndarray, mbti_matrix:np.ndarray, has_mbti_mask:np.ndarray,mbti_weight=0.1):
    """
    Calculates the similarity score between each mentor and mentee
    Considers both cosine similarity & MBTI similarity

    Returns:
        similarity_matrix(np.ndarray):
            A 2D matrix containing compatibility values for each mentor and mentee pairs

    Parameters:
        cosine_similarity_matrix(np.ndarray):
            A 2D numpy array, where each row represents the similarity scores of a mentee with all mentors

        mbti_matrix(np.ndarray):
            A 2D matrix containing MBTI compatibility values for each mentor and mentee pairs

        has_mbti_mask(np.ndarray):
            A 2D matrix denoting the existence of MBTI compatibility values for each mentor and mentee pair

    """
    similarity_matrix=cosine_similarity_matrix.copy()

    similarity_matrix[has_mbti_mask]=(
        (1-mbti_weight)* cosine_similarity_matrix[has_mbti_mask]+
        mbti_weight*mbti_matrix[has_mbti_mask]
    )

    return similarity_matrix



def build_cosine_similarity_matrices(mentees_feature_matrices: dict,
                              mentors_feature_matrices: dict) -> dict:
    """
    Computes cosine similarity matrices for every combination of
    mentee-area matrix and mentor-area matrix.

    Parameters
    ----------
    mentees_feature_matrices : dict
        A dictionary where each value is a matrix of shape (n_mentees, d_k)
        for some feature area.

    mentors_feature_matrices : dict
        A dictionary where each value is a matrix of shape (n_mentors, d_k)
        for some feature area.

    Returns
    -------
    similarity_matrices : dict
        Keys are strings "{mentee_area}_to_{mentor_area}".
        Values are similarity matrices with shape (n_mentees, n_mentors).
    """

    cosine_similarity_matrices = {}

    for mentee_area, mentee_matrix in mentees_feature_matrices.items():
        for mentor_area, mentor_matrix in mentors_feature_matrices.items():

            # Compute cosine similarity
            similarity = cosine_similarity_matrix(mentee_matrix, mentor_matrix)

            # Store using descriptive key
            key = f"Mentee_{mentee_area}_to_Mentor_{mentor_area}"
            cosine_similarity_matrices[key] = similarity

    return cosine_similarity_matrices


def calculate_total_similarity_matrices(cosine_similarity_matrices: dict[str,np.ndarray], 
                                        mbti_matrix: np.ndarray, 
                                        has_mbti_mask: np.ndarray, 
                                        mbti_weight: float):
    """
    Calculates the total similarity (goals+personality type for each mentor/mentee pair)

    Returns: 
        similairty_matrices: dict
            has 9 entries
            key(str): specifies the area index of mentee and mentor
            value(np.ndarray): specifies the total_similarity score between each mentee and mentor

    Parameters:
        cosine_similarity_matrices: dict
            has 9 entries
            key(str): specifies the area index of mentee and mentor
            value(np.ndarray): specifies the cosine similarity score between each mentee and mentor
        mbti_matrix: np.ndarray
            2D matrix specifying the compatibilty between each mentor and mentee pair
        has_mbti_mask: np.ndarray
            specifies whether the mentor mentee pair have MBTI assigned or not
        mbti_weight: float
            the weight given to mbti personality types in matchmaking     
    """
    similarity_matrices={}
    
    for key_area,cosine_similarity_matrix in cosine_similarity_matrices.items():
        # Store using descriptive key
        similarity_matrices[key_area]=get_total_similarity_matrix(
            cosine_similarity_matrix,
            mbti_matrix,
            has_mbti_mask,
            mbti_weight
            )
        
    return similarity_matrices

