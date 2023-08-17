import openai
import pandas as pd
import numpy as np 
from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import cosine_similarity
from pyrebase import pyrebase
from flask import Flask
from flask import jsonify
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
import os

# from db import getData
def configure():
    load_dotenv()


#Config api keys to use embeddings 
# configure()
# openai.api_key = os.getenv('OPENAI_API_KEY')

#config for Database
config = {
  'apiKey': os.getenv('FIREBASE_API_KEY'),
  'authDomain': "cie-air.firebaseapp.com",
  'databaseURL': "https://cie-air-default-rtdb.firebaseio.com",
  'projectId': "cie-air",
  'storageBucket': "cie-air.appspot.com",
  'messagingSenderId': "510902931789",
  'appId': "1:510902931789:web:15cfe0e60f3c3344aa6704"
}

# get data from database and conert into a local db to calculate multpile searches
# this enables us to conduct search at the expense of memory but provides a very
# fast search result time.
def getData():
  data = {'name':[],
          'embeddings':[],
          'interests':[],
          'similarities':[]}

  firebase = pyrebase.initialize_app(config)
  db = firebase.database()
  records = db.child().get()

  j=0
  for people in records.each():
      name = db.child(j).child("name").get()
      embedding = db.child(j).child("embedding").get()
      interests = db.child(j).child("research").child("Research Interests:").get()
      temp = []
      k = 0
      for embed_val in embedding.each():
          temp.append(embed_val.val())
          k+=1
      data['name'].append(name.val())
      data['embeddings'].append(temp)
      data['interests'].append(interests.val())
      data['similarities'].append(0)
      j+=1
  
  df = pd.DataFrame.from_dict(data)
  df['interests'] = df['interests'].fillna('')
  
  return df

# A way to build our buffer result
def addToResult(index,names, result):
    for i in range(len(index)):
        element = {"index": index[i],"name":names[i]}
        result.append(element)
        
    return result

#this generates trigrams
def generate_trigrams(text):
    words = text.split()
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words) - 2)]
    return trigrams

df = getData()

# The following cleans up the data so we can perform our exact match, partial match and trigram match searches


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def hello_world():
    print(df['interests'])
    return "hello"

#localhost/search?query=searchValue
@app.route("/search/<search_term>")
@cross_origin()
def search(search_term):
    #Here we are standardizing all the string to lowercase
    df['interests'] = df['interests'].fillna('')
    df['interests'] = df['interests'].str.lower()
    search_term = search_term.lower()


    #result with key value pair of index and name
    result = []

    #this is where the exact match happens for the entire search term.
    matches = df[df['interests'].str.contains(search_term, case=False)]

    index = matches.index.tolist()
    names = matches['name'].tolist()
    
    addToResult(index,names,result)
    
    #this is where the exact match happens for the Trigrams
    trigrams = generate_trigrams(search_term)
    for trigram in trigrams:
        matches = df[df['interests'].str.contains(trigram, case=False)]

        index = matches.index.tolist()
        names = matches['name'].tolist()

        addToResult(index,names,result)

    #This is where the semantic search algorithm takes place.
    search_term_vector = get_embedding(search_term,engine='text-embedding-ada-002')
    df['similarities'] = df['embeddings'].apply(lambda x: cosine_similarity(x,search_term_vector))
    ranking = df.sort_values("similarities", ascending=False).head(9)
   
    #indicies refering to the names
    keys = ranking.index.tolist()

    #names
    values = []
    
    #add names to values
    for hit in ranking['name']:
        values.append(hit)
    
    
    
    for i in range(len(keys)):
        element = {"index": keys[i],"name": values[i]}
        result.append(element)

    return jsonify(result)
