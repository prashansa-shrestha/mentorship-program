import pandas as pd
import numpy as np

#this list contains the columns that contain rating of expertise from 1-5
expertise_cols=[
    'current_level_of_expertise_technical1',
    'current_level_of_expertise_technical2',
    'current_level_of_expertise_nontechnical',
    'current_expertise_1',
    'current_expertise_2',
    'current_expertise_3'
]

#this dictionary contains the columns that are to be one hot encoded for mentors and mentees
one_hot_encoding_col={
    'mentors':['engineering_stream'],
    'mentees':['faculty']
}

def make_lowercase(col):
    if col.dtype=="object":
        return col.str.lower()
    else:
        return col
    
def normalize_expertise(df,cols):
    for col in cols:
        if col in df.columns:
            df[col]=pd.to_numeric(df[col],errors='coerce')
            df[col]=(df[col]-1)/4
    return df

def normalize_string(df):
    #normalizing column headers
    df.columns=(df.columns
                .str.lower()
                .str.strip()
                .str.replace(' ','_')
                .str.replace(r'[^A-Za-z0-9_]','',regex=True)
                )

    #lowercasing dataset
    df.apply(make_lowercase)

    #convereted all empty strings into nan
    df=df.replace(r'^\s*$',np.nan,regex=True)

    return df


def split_df_by_role(df, role_column='role'):
    """
    splits the datagrame into mentors_df and mentees_df
    based on the value of the role_column.

    Returns:
        mentors_df, mentees_df
    """
    mentors_df=df[df[role_column].str.lower()=='mentor'].copy()
    mentees_df=df[df[role_column].str.lower()=='mentee'].copy()

    return mentors_df,mentees_df

def drop_empty_cols(df):
    """
    Drops the columns where all values are NaN.
    Equivalent to df.dropna(axis=1,how='all')
    """
    return df.dropna(axis=1,how='all')

def one_hot_encode(df,col: list):
    #one-hot-encoding the faculties
    return pd.get_dummies(df, columns=col)

def print_df_col_names(df):
    print(df.columns,'\n\n')