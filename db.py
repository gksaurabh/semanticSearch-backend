from pyrebase import pyrebase
import pandas as pd
import numpy as np 
# from search import createEmbeddings

config = {
  'apiKey': "AIzaSyCQ-ptwgriECFfZwHLEMz2wRX9LQOlQwW8",
  'authDomain': "cie-air.firebaseapp.com",
  'databaseURL': "https://cie-air-default-rtdb.firebaseio.com",
  'projectId': "cie-air",
  'storageBucket': "cie-air.appspot.com",
  'messagingSenderId': "510902931789",
  'appId': "1:510902931789:web:15cfe0e60f3c3344aa6704"
}


# def pushEmbeddings(csvFile):
#     df = pd.read_csv('accData.csv')

#     createEmbeddings(df)

#     i = 0
#     for embedding in df['embedding']:
#         data = {"embedding": embedding}
#         db.child(i).child("embedding").set(embedding)
#         i+=1

# def getNamesIntoDataframe(dataframe):
#     for i in
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





   



