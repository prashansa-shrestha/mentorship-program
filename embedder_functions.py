from sentence_transformers import SentenceTransformer

#column headers containing sentence text fields
mentors_text_cols=[
     'engineering_subdomain_1','engineering_subdomain_2',
       'other_areas_of_experience']


mentees_text_cols=['areas_of_expected_guidance_priority_1',
       'areas_of_expected_guidance_priority_2', 
       'areas_of_expected_guidance_priority_3'
       'career_aspirations']


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

