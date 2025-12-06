import pandas as pd 

from preprocessor_functions import *

#loading dataset
df=pd.read_excel('dataset.xlsx')

#normalize all the strings in the dataset
df=normalize_string(df)

#normalize expertise
df=normalize_numeric(df, numeric_cols)

# new df with rows that meet condition=original_dataframe[condition]
mentors_df,mentees_df=split_df_by_role(df,'role')

#drop empty columns in mentor-mentee dataset
mentors_df=drop_empty_cols(mentors_df)
mentees_df=drop_empty_cols(mentees_df)

#one hot encode the categories
mentors_one_hot_cols,mentors_df=one_hot_encode(
    mentors_df,
    one_hot_encoding_col['mentors']
    )
mentees_one_hot_cols,mentees_df=one_hot_encode(
    mentees_df,
    one_hot_encoding_col['mentees']
    )