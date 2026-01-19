from embedder_functions import *
from preprocessor import mentors_df, mentees_df

mentors_embedded_df=mentors_df.copy() #intializing dataframe to integrate embeddings
mentees_embedded_df=mentees_df.copy()

    
mentors_embedded_df, mentors_embedded_col_headers= embed_df(
    mentors_embedded_df, mentors_areas
)

    
mentees_embedded_df, mentees_embedded_col_headers= embed_df(
    mentees_embedded_df, mentees_areas
)


mentors_embedded_df.to_pickle("mentors_with_embeddings.pkl")
mentees_embedded_df.to_pickle("mentees_with_embeddings.pkl")