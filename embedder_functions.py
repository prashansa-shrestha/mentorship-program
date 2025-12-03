from sentence_transformers import SentenceTransformer

mentors_text_columns=[
     'engineering_subdomain_1','engineering_subdomain_2',
       'other_areas_of_experience']



mentees_text_columns=['areas_of_expected_guidance_priority_1',
       'areas_of_expected_guidance_priority_2', 
       'areas_of_expected_guidance_priority_3'
       'career_aspirations']


model=SentenceTransformer("all-MiniLM-L6-v2")

def mentors_embedder(mentors_df):
    for col in mentors_text_columns:
        col_list=mentors_df[col].tolist()

        print('Embedding the columns...\n')
        embeddings=model.encode(
            col_list,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        mentors_df[col+'_emb']=list(embeddings)
    return mentors_df

def mentees_embedder(mentees_df):
    for col in mentees_text_columns:
        col_list=mentees_df[col].tolist()

        print('Embedding the columns...\n')
        embeddings=model.encode(
            col_list,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        mentees_df[col+'_emb']=list(embeddings)
    return mentees_df