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
configure()
openai.api_key = os.getenv('OPENAI_API_KEY')

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
          'similarities':[]}

  firebase = pyrebase.initialize_app(config)
  db = firebase.database()
  records = db.child().get()

  j=0
  for people in records.each():
      name = db.child(j).child("name").get()
      embedding = db.child(j).child("embedding").get()
      temp = []
      k = 0
      for embed_val in embedding.each():
          temp.append(embed_val.val())
          k+=1
      data['name'].append(name.val())
      data['embeddings'].append(temp)
      data['similarities'].append(0)
      j+=1
  
  df = pd.DataFrame.from_dict(data)
  return df


df = getData()


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"

#localhost/search?query=searchValue
@app.route("/search/<search_term>")
@cross_origin()
def search(search_term): 
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
    
    #result with key value pair of index and name
    result = []
    
    for i in range(len(keys)):
        element = {"index": keys[i],"name": values[i]}
        result.append(element)

    return jsonify(result)
