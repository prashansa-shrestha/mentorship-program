import numpy as np
import pandas as pd

def normalize(matrix:np.ndarray):
    """
    Normalizes the rows of the matrix passed

    Parameters:
        matrix(numpy.ndarray):
            A 2D numpy array where each row represents a feature vector
    
    Returns:
        normalized_matrix(numpy.ndarray):
            A row-normalized 2D numpy array 
    """
    row_norms=np.linalg.norm(matrix,axis=1,keepdims=True)
    row_norms[row_norms==0]=1
    normalized_matrix=matrix/row_norms
    return normalized_matrix
    
def cosine_similarity_matrix(mentors:np.ndarray,mentees: np.ndarray):
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
    mentor_normalized=normalize(mentors)
    mentee_normalized=normalize(mentees)

    similarity_matrix=mentee_normalized @ mentor_normalized.T

    return similarity_matrix

def get_mbti_compatiblity_data():
    mbti_df=pd.read_csv("datasets/mbti_compatibility.csv",index_col=0)
    mbti_compatibility_data=mbti_df.to_numpy()
    return mbti_compatibility_data


def apply_MBTI():
    mbti_compatibility=get_mbti_compatiblity_data()
    mbti_types=['ENFJ', 'ENFP', 'ENTJ', 'ENTP', 
                'ESFJ', 'ESFP', 'ESTJ', 'ESTP',
                'INFJ', 'INFP', 'INTJ', 'INTP',
                'ISFJ', 'ISFP', 'ISTJ', 'ISTP']
