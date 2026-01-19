import pandas as pd
import numpy as np
from typing import List, Tuple, Union, Optional

# this list contain the columns that contain rating of expertise from 1-5

MENTORS_NUMERIC_COLS = [
    "current_level_of_expertise_technical1",
    "current_level_of_expertise_technical2",
    "current_level_of_expertise_nontechnical",
]

MENTEES_NUMERIC_COLS = [
    "current_expertise_1",
    "current_expertise_2",
    "current_expertise_3",
]

NUMERIC_COLS = MENTORS_NUMERIC_COLS + MENTEES_NUMERIC_COLS

# this dictionary contains the columns that are to be one hot encoded for mentors and mentees
ONE_HOT_ENCODING_COL = {"mentors": ["engineering_stream"], "mentees": ["faculty"]}

MAX_VALUE_NUMERIC = 5
MIN_VALUE_NUMERIC = 1

def read_dataset(file_path: str):
    """
    Reads an Excel dataset from the specified file path into a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        The full path to the Excel file (.xlsx or .xls).

    Returns
    -------
    pd.DataFrame
        The DataFrame containing the data from the Excel file.

    Raises
    ------
    FileNotFoundError
        If the specified `file_path` does not exist. The function prints an 
        error message and exits the program.
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError as e:
        print(f"Error: dataset.xlsx not found. Please check the file path. {e}")
        exit()


def make_lowercase(col: pd.Series) -> pd.Series:
    """
    Makes all the entries of columns in the dataframe lowercase if they are a string

    Parameters:
        col(pd.Series):
            The column whose values are to be lowercased

    Returns:
        col_lowercase (pd.Series):
            The processed column with strings lowercased

    """
    if col.dtype == "object":
        col_lowercase = col.str.lower()
        return col_lowercase
    else:
        return col


def normalize_numeric(
    df: pd.DataFrame,
    cols: List[str] = NUMERIC_COLS,
    upper_limit: int = MAX_VALUE_NUMERIC,
    lower_limit: int = MIN_VALUE_NUMERIC,
) -> pd.DataFrame:
    """
    Normalizes specific numeric columns in the dataset using Min-Max scaling.
    In this project, this is used for ratings of their skill-sets by the mentors and mentees

    Returns:
        df(pd.DataFrame):
            The dataframe with specified columns normalized between 0 and 1.
    Args:
        df (pd.DataFrame): The dataframe containing the data.
        cols (List[str]): List of column names to be normalized.
                          Defaults to the global NUMERIC_COLS list.
        min_val (int): The minimum possible value of the rating (e.g., 1).
        max_val (int): The maximum possible value of the rating (e.g., 5)."""
    for col in cols:
        if col in df.columns:
            # Coerce errors turn non-numeric garbage into NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = (df[col] - lower_limit) / (upper_limit - lower_limit)
    return df


def normalize_string(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes the dataframe's column headers and string values.

    Operations:
    1. Headers: Lowercase, strip whitespace, replace spaces with underscores,
       remove special characters.
    2. Values: Lowercase all string entries.
    3. Empty Strings: Converts whitespace-only strings to NaN.

    Args:
        df (pd.DataFrame): The raw dataframe.

    Returns:
        pd.DataFrame: The cleaned and normalized dataframe.
    """
    # normalizing column headers
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"[^A-Za-z0-9_]", "", regex=True)
    )

    # Lowercase all object columns in the dataset
    df = df.apply(make_lowercase)

    # Convert all empty or whitespace-only strings into NaN
    df = df.replace(r"^\s*$", np.nan, regex=True)

    return df


def split_df_by_role(
    df: pd.DataFrame, role_column: str = "role"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataframe into two separate dataframes based on the user role.

    Args:
        df (pd.DataFrame): The main dataframe containing mixed roles.
        role_column (str): The column name identifying the user role. Defaults to 'role'.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: 
            - mentors_df: Dataframe containing only mentors.
            - mentees_df: Dataframe containing only mentees.
    """# Ensure we handle NaN in the role column to avoid attribute errors
    if role_column not in df.columns:
        raise KeyError(f"Column '{role_column}' not found in dataframe.")
    
    mentors_df = df[df[role_column].str.lower() == "mentor"].copy()
    mentees_df = df[df[role_column].str.lower() == "mentee"].copy()

    return mentors_df, mentees_df


def drop_empty_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops columns where all values are NaN.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        pd.DataFrame: Dataframe with empty columns removed.
    """
    return df.dropna(axis=1, how="all")


def one_hot_encode(df: pd.DataFrame, col: List[str]) -> Tuple[List[str], pd.DataFrame]:
    """
    One-hot encodes the specified categorical columns using pandas get_dummies.

    Args:
        df (pd.DataFrame): Dataframe to encode.
        col (List[str]): List of column names to perform one-hot encoding on.

    Returns:
        Tuple[List[str], pd.DataFrame]:
            - ohe_cols: A list of the names of the newly created encoded columns.
            - ohe_df: The dataframe with the new one-hot encoded columns included.
    """

    # one-hot-encoding the faculties
    ohe_df = pd.get_dummies(df, columns=col, dtype=int)

    before = set(df.columns)
    after = set(ohe_df.columns)

    ohe_cols = list(after - before)
    #sort the columns alphabetically to ensure consistency
    ohe_cols.sort()

    return ohe_cols, ohe_df


def print_df_col_names(df: pd.DataFrame) -> None:
    """
    Prints all column names in the provided dataframe.

    Args:
        df (pd.DataFrame): The dataframe whose columns will be printed.

    Returns:
        None
    """
    print(df.columns, "\n\n")
    return


def get_mbti_list(df: pd.DataFrame, col_header: str = 'mbti_personality_type') -> List[Optional[str]]:
    """
    Extracts MBTI personality types from a dataframe column as a list.
    Converts NaN values into None for consistent downstream processing.

    Args:
        df (pd.DataFrame): Dataframe containing user data.
        col_header (str): Name of the column containing the MBTI type. 
                          Defaults to 'mbti_personality_type'.

    Returns:
        mbti_list(List[Optional[str]]): A list of MBTI types, where missing values are None.
    """
    if col_header not in df.columns:
        raise KeyError(f"Column '{col_header}' not found in dataframe.")

    mbti_series = df[col_header]

    #replace NaN with None
    mbti_series_cleaned = mbti_series.where(mbti_series.notna(), None)

    #convert the series to a list
    mbti_list = mbti_series_cleaned.tolist()
    return mbti_list
