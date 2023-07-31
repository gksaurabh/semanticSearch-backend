import openai
import pandas as pd
import numpy as np 
from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import cosine_similarity



key = "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"
openai.api_key = key

def createEmbeddings(df):
    df['embedding'] = df['interests'].apply(lambda x: get_embedding(x,engine='text-embedding-ada-002'))

df = pd.read_csv('accData.csv')

createEmbeddings(df)

search_term = input("What would like to search for?")
#semantic search
search_term_vector = get_embedding(search_term,engine='text-embedding-ada-002')

df['similarities'] = df['embedding'].apply(lambda x: cosine_similarity(x,search_term_vector))
results = df.sort_values("similarities", ascending=False).head(5)

print(results)