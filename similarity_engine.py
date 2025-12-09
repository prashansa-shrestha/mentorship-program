from similarity_engine_functions import *
from concatenator import mentors_feature_matrices_dict,mentees_feature_matrices_dict

mbti_weight=0.1

#dictionary containing the cosine similarity between each mentee and mentor area
similarity_matrices=build_similarity_matrices(
    mentees_feature_matrices_dict,
    mentors_feature_matrices_dict
)



mbti_matrix, has_mbti_mask=calculate_mbti_matrices()


similarity_matrix=get_similarity_matrix(cosine_similarity_matrix, mbti_matrix,has_mbti_mask, mbti_weight)



from similarity_engine_functions import mentors_expertise_matrix, mentees_expertise_matrix, n_mentors, n_mentees

#dimension: [mentor_popn, mentee_popn, expertise level]
#           depth of cube, length of cube, breadth of cube
mentor_expertise_3d=mentors_expertise_matrix[None,:,:]
mentee_expertise_3d=mentees_expertise_matrix[:,None,:]

expertise_difference=mentor_expertise_3d-mentee_expertise_3d

expertise_difference_mask=np.isclose(expertise_difference,0.2)|np,isclose(expertise_difference,0.4)












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