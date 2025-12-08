from similarity_engine_functions import *
from concatenator import feature_matrix

mbti_weight=0.1

#how much their interests align
#it compares all 3 interests
cosine_similarity_matrix = cosine_similarity_matrix(
    feature_matrix["mentees"],
    feature_matrix["mentors"]
)

mbti_matrix, has_mbti_mask=calculate_mbti_matrices()


similarity_matrix=get_similarity_matrix(cosine_similarity_matrix, mbti_matrix,has_mbti_mask, mbti_weight)














#-------ROUGH--------

#dk if i'll use this function or not
def get_top_mentors(similarity_matrix:np.ndarray):
    """
    Returns mentor indices sorted by similarity for each mentee
    
    Returns:
        top_match(np.ndarray):
            A 2D numpy array (n_mentees, m_mentors) 
            where:
                each row contains mentors indices sorted in descending order of similarity scores
                Entry [i,0] is the best match for mentee i

    Parameters:
        similarity_matrix(np.ndarray):
            A 2D numpy array where each row contains similarity scores between
            a single mentee(rows), and all mentors(columns)
    """
    indices= similarity_matrix.argsort(axis=1)[:, ::-1]
    scores= np.take_along_axis(similarity_matrix,indices,axis=1)
    return indices,scores

#implementing this to avoid mentor overload while generating sufficient mentor-mentee matches
# also need to think about mentor overload, so i need to return 

def capacity_constrained_matching(similarity_matrix:np.ndarray,
                                  mentor_capacity: int,
                                  mentee_capacity:int=3):
    n_mentees,n_mentors=similarity_matrix.shape
    
    #mentee_idx: row index for every pair
    #mentor_idx: column index for every pair
    mentee_idx,mentor_idx=np.indices(n_mentees,n_mentors)
    mentee_idx=mentee_idx.ravel()
    mentor_idx=mentor_idx.ravel()
    scores=similarity_index.ravel()