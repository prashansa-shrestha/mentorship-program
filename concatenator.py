from embedder import mentors_emb_cols, mentees_emb_cols
from preprocessor import (
    mentors_one_hot_cols,
    mentees_one_hot_cols,
    mentors_numeric_cols,
    mentees_numeric_cols,
)
from concatenator_functions import *

#Key assumption:


if (len(mentors_emb_cols)!=len(mentees_emb_cols)):
    raise ValueError(
        f"Embedding dimension mismatch:\n"
        "Mentors have {len(mentors_emb_cols)} embedding columns\n"
        "Mentees have {len(mentees_emb_cols)} embedding columns"
    )

#all the embedded columns represented as key value pairs in dictionary
mentors_embedding_matrices_dict = build_emb_matrices(mentors_df, mentors_emb_cols)
mentees_embedding_matrices_dict = build_emb_matrices(mentees_df, mentees_emb_cols)


#all the embedded columns represented as a single 2D numpy array
mentors_concatenated_embedding_matrices = concatenate_matrices_from_dict(
    mentors_embedding_matrices_dict
)
mentees_concatenated_embedding_matrices = concatenate_matrices_from_dict(
    mentees_embedding_matrices_dict
)

if (len(mentors_one_hot_cols)!=len(mentees_one_hot_cols)):
    raise ValueError(
        f"One hot columns dimension mismatch:\n"
        "Mentors have {len(mentors_one_hot_cols)} one hot columns"
        "Mentees have {len(mentees_one_hot_cols)} one hot columns"
    )

#one hot columns represented as a single 2D numpy array
mentors_one_hot_matrix = build_numeric_matrices(mentors_df, mentors_one_hot_cols)
mentees_one_hot_matrix = build_numeric_matrices(mentees_df, mentees_one_hot_cols)


if (len(mentors_numeric_cols)!=len(mentees_numeric_cols)):
    raise ValueError(
        f"Numeric columns dimension mismatch:\n"
        "Mentors have {len(mentors_numeric_cols)} numeric columns"
        "Mentees have {len(mentees_numeric_cols)} numeric columns"
    )


#all the numeric columns represented as a single 2D numpy array
mentors_expertise_matrix = build_numeric_matrices(mentors_df, mentors_numeric_cols)
mentees_expertise_matrix = build_numeric_matrices(mentees_df, mentees_numeric_cols)


if ((mentors_numeric_matrix.shape[1])!=(mentees_numeric_matrix.shape[1])):
    raise ValueError(
        f"Numeric matrices dimension mismatch:\n"
        "Mentors have {mentors_numeric_matrix.shape[1]} columns"
        "Mentees have {mentees_numeric_matrix.shape[1]} columns"
    )


#list of all features
mentors_matrix_list = [
    mentors_concatenated_embedding_matrices,
    mentors_one_hot_matrix
]

mentees_matrix_list = [
    mentees_concatenated_embedding_matrices,
    mentees_one_hot_matrix
]

#dict representing all features
feature_matrix = {
    "mentors":concatenate_matrices(mentors_matrix_list),
    "mentees":concatenate_matrices(mentees_matrix_list)
}