import pandas as pd
import numpy as np

#this list contain the columns that contain rating of expertise from 1-5

mentors_numeric_cols=[
    'current_level_of_expertise_technical1',
    'current_level_of_expertise_technical2',
    'current_level_of_expertise_nontechnical'
]

mentees_numeric_cols=[
    'current_expertise_1',
    'current_expertise_2',
    'current_expertise_3'
]

numeric_cols=mentors_numeric_cols+mentees_numeric_cols

#this dictionary contains the columns that are to be one hot encoded for mentors and mentees
one_hot_encoding_col={
    'mentors':['engineering_stream'],
    'mentees':['faculty']
}

max_value_numeric=5
min_value_numeric=1

def make_lowercase(col):
    """
    Makes all the entries of columns in the dataframe lowercase if they are a string

    Returns:
        col_lowercase: pandas column
            column with all values lowercased
        
    
    Parameters:
        col: pandas column
            column whose values are to be lowercased

    """
    if col.dtype=="object":
        col_lowercase= col.str.lower()
        return col_lowercase
    else:
        return col
    
def normalize_numeric(df,cols):
    """
    Normalizes all the numeric values in the dataset
    In this project, this is used for ratings of their skill-sets by the mentors and mentees

    Returns:
        df: pandas DataFrame
            dataframe with numerical columns normalized
    
    Parameters:
        df: pandas DataFrame
            dataframe with numerical columns to be normalized
        cols: list
            list containing columns names of numeric columns
    """
    for col in cols:
        if col in df.columns:
            df[col]=pd.to_numeric(df[col],errors='coerce')
            df[col]=(df[col]-min_value_numeric)/(max_value_numeric-min_value_numeric)
    return df

def normalize_string(df):
    """
    Normalizes all the strings in the dataset
        Normalizes column headers
            > turns them to lowercase
            > removes unnecessary whitespace
            > 
    """
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
    """
    return df.dropna(axis=1,how='all')

def one_hot_encode(df,col: list):
    """
    One hot encodes the given categorical columns

    Parameters:
        df: pandas.Dataframe
            Dataframe to one hot encode
        col: list
            List of column names to one hot encode
            
    Returns:
        ohe_cols:list
            Names of newly created one hot encoded columns.
        ohe_df: pandas.Dataframe
            Dataframe with added one hot encoded columns
    """
    
    #one-hot-encoding the faculties
    ohe_df=pd.get_dummies(df, columns=col)
    
    before=set(df.columns)
    after=set(ohe_df.columns)

    ohe_cols=list(after-before)

    return ohe_cols, ohe_df


def print_df_col_names(df):
    """
    Print all columns names in the provided dataframe
    """
    print(df.columns,'\n\n')