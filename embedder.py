from embedder_functions import *
from preprocessor import mentors_df, mentees_df


mentors_df_emb=mentors_embedder(mentors_df)
mentees_df_emb=mentees_embedder(mentees_df)


mentors_df_emb.to_pickle("mentors_with_embeddings.pkl")
mentees_df_emb.to_pickle("mentees_with_embeddings.pkl")