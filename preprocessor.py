import pandas as pd 
import numpy as np

from preprocessor_functions import make_lowercase
#loading dataset
df=pd.read_excel('dataset.xlsx')

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

# new df with rows that meet condition=original_dataframe[condition]
mentors_df=df[df['role']=='Mentor']
mentees_df=df[df['role']=='Mentee']

mentors_df=mentors_df.dropna(axis=1,how='all')
mentees_df=mentees_df.dropna(axis=1,how='all')

print("\n Mentor Headers\n")
print(list(mentors_df.columns))

print("\n Mentees Headers\n")
print(list(mentees_df.columns))

mentors_df.to_excel('mentors.xlsx')
mentees_df.to_excel('mentees.xlsx')


