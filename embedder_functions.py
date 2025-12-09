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

def embed_text_cols(df,text_cols):
    """
    Generates embeddings for all specified text columns and appends
    them to the dataframe as new '{col}_emb' columns.

    Parameters:
        df: pandas.Dataframe
            original dataframe which requires text embeddings
        text_cols: list
            list which contains the column headers of the columns 
            to be embedded
    
    Returns:
        df: pandas.Dataframe
            dataframe with new embedding columns
        emb_cols (list): list containing names of created embedding columns
    """
    emb_cols=[]
    for col in text_cols:
        col_list=df[col].tolist()

        print("Embedding the columns...\n")
        embeddings=model.encode(
            col_list,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        emb_cols.append(col+'_emb')
        df[col+'_emb']=list(embeddings)
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
