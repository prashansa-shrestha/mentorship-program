import pandas as pd 

from preprocessor_functions import *

# --- 1. Data Loading and Initial String Normalization ---


#loading dataset
df=read_dataset('dataset.xlsx')

# Normalize all strings: column headers, values, and convert empty cells to NaN.
df=normalize_string(df)


# --- 2. Numerical Normalization ---


# Normalize skill ratings (1-5) to a 0-1 range for the entire dataset.
df=normalize_numeric(df)


# --- 3. Data Splitting ---

# Split the dataframe into two based on the user's role column.
mentors_df,mentees_df=split_df_by_role(df,'role')

#drop empty columns in mentor-mentee dataset
mentors_df=drop_empty_cols(mentors_df)
mentees_df=drop_empty_cols(mentees_df)

#gets the number of mentors and mentees in the dataframe
n_mentees=mentees_df.shape[0]
n_mentors=mentors_df.shape[0]
print(f"Dataset split: {n_mentors} Mentors and {n_mentees} Mentees.")

# --- 4. Extracting MBTI Personality Types ---
mentors_mbti=get_mbti_list(mentors_df)
mentees_mbti=get_mbti_list(mentees_df)

# Perform One-Hot Encoding (OHE) on categorical columns specific to each group.
# Mentors: 'engineering_stream'
# Mentees: 'faculty'
mentors_one_hot_cols, mentors_df = one_hot_encode(
    mentors_df,
    ONE_HOT_ENCODING_COL['mentors']
)
mentees_one_hot_cols, mentees_df = one_hot_encode(
    mentees_df,
    ONE_HOT_ENCODING_COL['mentees']
)