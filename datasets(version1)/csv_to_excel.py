import pandas as pd

df=pd.read_csv('personality_type.csv')
df.to_excel('personality_type.xlsx')