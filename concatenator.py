from embedder import mentors_embedded_col_headers, mentees_embedded_col_headers
from preprocessor import (
    mentors_one_hot_cols,
    mentees_one_hot_cols,
    mentors_numeric_cols,
    mentees_numeric_cols,
)
from concatenator_functions import *

#Key assumption:

# ----ONE HOT COLS---
if (len(mentors_one_hot_cols)!=len(mentees_one_hot_cols)):
    raise ValueError(
        f"One hot columns dimension mismatch:\n"
        "Mentors have {len(mentors_one_hot_cols)} one hot columns"
        "Mentees have {len(mentees_one_hot_cols)} one hot columns"
    )

#one hot columns represented as a single 2D numpy array
mentors_one_hot_matrix = build_numeric_matrices(mentors_df, mentors_one_hot_cols)
mentees_one_hot_matrix = build_numeric_matrices(mentees_df, mentees_one_hot_cols)



# ----EXPERTISE NUMERIC COLS----
if (len(mentors_numeric_cols)!=len(mentees_numeric_cols)):
    raise ValueError(
        f"Numeric columns dimension mismatch:\n"
        "Mentors have {len(mentors_numeric_cols)} numeric columns"
        "Mentees have {len(mentees_numeric_cols)} numeric columns"
    )


#all the numeric columns represented as a single 2D numpy array
mentors_expertise_matrix = build_numeric_matrices(mentors_df, mentors_numeric_cols)
mentees_expertise_matrix = build_numeric_matrices(mentees_df, mentees_numeric_cols)


if ((mentors_expertise_matrix.shape[1])!=(mentees_expertise_matrix.shape[1])):
    raise ValueError(
        f"Numeric matrices dimension mismatch:\n"
        "Mentors have {mentors_numeric_matrix.shape[1]} columns"
        "Mentees have {mentees_numeric_matrix.shape[1]} columns"
    )


# ----EMBEDDING COLUMNS----

if (len(mentors_embedded_col_headers)!=len(mentees_embedded_col_headers)):
    raise ValueError(
        f"Embedding dimension mismatch:\n"
        "Mentors have {len(mentors_embedded_col_headers)} embedding columns\n"
        "Mentees have {len(mentees_embedded_col_headers)} embedding columns"
    )

#all the embedded columns represented as key value pairs in dictionary

#constructs dictionary with each feature of mentors
mentors_feature_matrices_dict=build_emb_dict(mentors_df, mentors_embedded_col_headers)

#constructs dictionary with each feature of mentees
mentees_feature_matrices_dict=build_emb_dict(mentees_df, mentees_embedded_col_headers)


#all the embedded columns represented as a single 2D numpy array
# mentors_concatenated_embedding_matrices = concatenate_matrices_from_dict(
#     mentors_area_embedding_matrices_dict
# )
# mentees_concatenated_embedding_matrices = concatenate_matrices_from_dict(
#     mentees_area_embedding_matrices_dict
# )


# #list of all features
# mentors_matrix_list = [
#     mentors_concatenated_embedding_matrices,
#     mentors_one_hot_matrix
# ]

# mentees_matrix_list = [
#     mentees_concatenated_embedding_matrices,
#     mentees_one_hot_matrix
# ]
