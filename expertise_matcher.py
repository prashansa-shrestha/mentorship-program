

from similarity_engine_functions import mentors_expertise_matrix, mentees_expertise_matrix, n_mentors, n_mentees
from expertise_matcher_functions import *

expertise_differences,expertise_difference_mask=calculate_expertise_differences(
    mentors_expertise_matrix,
    mentees_expertise_matrix
    )

