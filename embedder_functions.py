from sentence_transformers import SentenceTransformer
import pandas as pd

#column headers containing sentence text fields
mentors_area1=[
     'engineering_subdomain_1'
     ]
mentors_area2=[
    'engineering_subdomain_2'
    ]
mentors_area3=[
    'other_areas_of_experience'
    ]

mentors_areas=[mentors_area1,mentors_area2,mentors_area3]



mentees_area1=['areas_of_expected_guidance_priority_1',
       'career_aspirations']
mentees_area2=['areas_of_expected_guidance_priority_2', 
       'career_aspirations']
mentees_area3=['areas_of_expected_guidance_priority_3',
       'career_aspirations']


mentees_areas=[mentees_area1,mentees_area2,mentees_area3]


model=SentenceTransformer("all-MiniLM-L6-v2")

def embed_text_cols(df: pd.DataFrame, text_cols: list)->tuple[pd.DataFrame,list[str]]:
    """
    Generates embeddings for all specified text columns and appends
    them to the dataframe as new '{col}_emb' columns.

    Parameters:
        df: pandas.DataFrame
            original dataframe which requires text embeddings
        text_cols: list
            list of column specifications. Each element can be:
            - str: single column name to embed
            - list of 2 strings: two columns to embed and average (2:3 ratio)
    Returns:
        df: pandas.DataFrame
            dataframe with new embedding columns
        emb_cols: list
            list containing names of created embedding columns
    """
    emb_cols = []

    print("Embedding the columns...\n")

    for col_spec in text_cols:
        # Case 1: Single column
        if isinstance(col_spec, str):
            col_list = df[col_spec].tolist()
            embeddings = model.encode(
                col_list,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            emb_col_name = col_spec + '_emb'
            df[emb_col_name] = list(embeddings)
            emb_cols.append(emb_col_name)
        
        # Case 2: Two columns to average (2:3 ratio)
        elif isinstance(col_spec, list) and len(col_spec) == 2:
            col1, col2 = col_spec
            
            # Embed first column
            col1_list = df[col1].tolist()
            embeddings1 = model.encode(
                col1_list,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            # Embed second column
            col2_list = df[col2].tolist()
            embeddings2 = model.encode(
                col2_list,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            # Average with 3:2 ratio (60% first, 40% second)
            averaged_embeddings = (3 * embeddings1 + 2 * embeddings2) / 5
            
            emb_col_name = f"{col1}_{col2}_emb"
            df[emb_col_name] = list(averaged_embeddings)
            emb_cols.append(emb_col_name)
        
        else:
            raise ValueError(f"Invalid column specification: {col_spec}")

    return df, emb_cols


def embed_df(embedded_df:pd.DataFrame, areas: list[str])->tuple[pd.DataFrame, list[list[str]]]:
    """
    Embeds each interest area, and provides the information of column headers embedded

    Returns:
        embedded_df(pd.DataFrame):
            DataFrame with embedded columns added
        embedded_col_headers(list of lists): 
            A list where each element is a list of embedded column names created for corresponding coluns in 'areas'

    Parameters:
        embedded_df(pd.DataFrame): 
            Input dataframe containing columns to embed
        areas(list[str]):
            List of columns to embed
    """
    embedded_col_headers=[]
    for category in areas:
        embedded_df, new_cols=embed_text_cols(
            embedded_df,category
            )
        embedded_col_headers.append(new_cols)
    return embedded_df,embedded_col_headers
