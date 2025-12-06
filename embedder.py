from embedder_functions import *
from preprocessor import mentors_df, mentees_df


mentors_df_emb,mentors_emb_cols=embed_text_cols(
    mentors_df,
    mentors_text_cols
    )

mentees_df_emb,mentees_emb_cols=embed_text_cols(
    mentees_df,
    mentees_text_cols
    )


mentors_df_emb.to_pickle("mentors_with_embeddings.pkl")
mentees_df_emb.to_pickle("mentees_with_embeddings.pkl")