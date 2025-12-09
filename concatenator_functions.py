import numpy as np
import pandas as pd

#dataframes containing embeddings
mentors_df=pd.read_pickle("mentors_with_embeddings.pkl")
mentees_df=pd.read_pickle("mentees_with_embeddings.pkl")

def block_to_matrix(df,col:str):
    """
    Converts a DataFrame column of embedding vectors into a 2D numpy array
    where each row represents an entry

    Parameters: 
        df: pandas DataFrame
            the dataframe containing the embedding columns
        col: str
            name of the column whose elements are embedding vectors
    
    Returns:
        matrix: 2D np array
            (n,d) matrix containing d-dimension embeddings of n people
    
    """
    oned_nparray=df[col].to_numpy()
    matrix=np.stack(oned_nparray)
    return matrix


def build_emb_matrices(df:pd.DataFrame,emb_cols:list[str]):
    """
    For each column header in emb_cols, converts the column data into embedding
    Converts embedding columns in a DataFrame into stacked 2D numpy matrices
    If the dimension is d, then the resulting numpy array has d columns

        Returns:
        matrix: np.ndarray
            2D numpt array of shape (n,d)
                n= number of rows in dataframe
                d= embedding dimension of column

    Parameters:
        df: pandas DataFrame
            The dataframe containing embedding columns
        emb_cols: list
            List of column names where each columns contains
            an embedding vector
    
    """
    for col in emb_cols:
        key=col.removesuffix('_emb')+'_matrix'
        matrix=block_to_matrix(df, col)
    return matrix


def build_numeric_matrices(df, numeric_cols):
    """
    Convert all numeric columns into a single 2D numpy array

    Returns:
        matrix_numeric: numpy.ndarray
            contains all data of numeric columns in dataframe df
            -each column represents the numeric_cols in the provided df
            -each row represents the row in df
        
    Parameters:
        df: pandas DataFrame
            the dataframe containing the numeric rows that are to be converted to a matrix
        numeric_cols: list
            contains the column names that stores numeric values in the dataframe df
        
    """
    matrix_numeric= df[numeric_cols].to_numpy(dtype=float)
    return matrix_numeric


def concatenate_matrices_from_dict(matrices_dict:dict):
    """
    Concatenates all the matrices stored as values in a dictionary into one 2D np array

    Returns:
        concatenated_emb_matrix: numpy.ndarray
            a 2D array representing by horizontally concatenating all matrices in a dictionary
            Resulting shape (n,sum(dimension_of_features)), for n samples
    
    Parameters:
        matrices_dict(dict): 
            A dictionary where:
                each entry represents a matrix of an embedded column
                key(str): Name of the feature matrix in the format "{col_without_emb}_matrix"
                value(numpy.ndarray): 2D numpy array of shape (n,d) representing d-dimensional embeddings for n samples
    """
    concatenated_emb_matrix = np.concatenate([matrix for matrix in matrices_dict.values()], axis=1)
    return concatenated_emb_matrix


def concatenate_matrices(matrix_list: list):
    """
    Concatenates multiple 2D numpy matrices column-wise (axis=1)

    Returns:
        concatenated_matrix: numpy.ndarray
            a 2D array formed by horizontal concatenation of all matrices
            Resulting shape: n_rows x sum(dimension_of_features)
    Parameters:
        matrix_list: list
            list where each element is a 2D numpy array representing features
    """
    concatenated_matrix = np.concatenate([matrix for matrix in matrix_list], axis=1)
    return concatenated_matrix


def build_emb_dict(df:pd.DataFrame, embedded_col_headers: list[list[str]])->dict:
    """
    Generates the embeddings for each list element in embedded_col_headers

    Returns: 
        area_embedding_matrices: dict
            Key (str): area_i (eg. area_1, area_2)
            Value (np.ndarray): embedding matrix for the paricular area

    """
    area_embedding_matrices={}
    for i,col_list in enumerate(embedded_col_headers):  
        value=build_emb_matrices(df,col_list)
        key=f"area{i+1}"
        area_embedding_matrices[key]=value
    return area_embedding_matrices