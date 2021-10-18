#!/usr/bin/env python
# coding: utf-8
import firebase_admin
from firebase_admin import credentials
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from firebase_admin import db
from firebase_admin import firestore
import pandas as pd

cred = credentials.Certificate('konnect-72976-firebase-adminsdk-m1xs2-8e5e7f5ec9.json')
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://konnect-72976-default-rtdb.firebaseio.com/'
})

# Get a database reference to our posts
ref = db.reference('/')
# Read the data at the posts reference (this is a blocking operation)
df = pd.DataFrame.from_dict(ref.get())
important_features = []
#Create a list of important columns for the recommendation engine
columns = ['Location', 'Place', 'Artist', 'Genre', 'Day', 'Time of day', 'Organizer']
#Combine imported featured in to important_featured column
def get_important_features(data):
    for i in range(0, data.shape[0]):
        important_features.append(data['Genre'][i]+','+data['Place'][i]+','+data['Artist'][i]+','+data['Location'][i]+','+data['Day'][i]+','+data['Time of day'][i]+','+data['Organizer'][i])
    return important_features
df['important_features'] = get_important_features(df)
cm = CountVectorizer().fit_transform(df['important_features'])
#Get the cosine similarity matrix from the count matrix
cs = cosine_similarity(cm)
scores = list(enumerate(cs[0]))
sorted_score = sorted(scores, key = lambda x:x[1], reverse = True)
sorted_score = sorted_score[1:]

k = 0
itemValue=0.999999
value=0.0000
print("{:<10} {:<15} {:<10}".format("EVENT_ID","| SIMILARITY","|VARIENCE"))
print("-----------------------------------------")
for item in sorted_score:
    refZERO = db.reference(str(item[0]))
    dataZERO=refZERO.get()
    value=value+item[1]
    if item[1]>=value :
        highestValue=item[1]
    itemValue=item[1]+itemValue
    varience=1-item[1]
    print("{:<10} {:<15} {:<10}".format(str(item[0]),"|"+format((item[1])*100,".2f")+"%","|"+format(varience*100,".2f")+"%"))
    itemValue=item[1]+itemValue
    k = k+1
    if k>10:
        break
AverageSimilarity=format((itemValue*100/k),".2f")
AverageVarience=format((100-(itemValue*100/k)),".2f")
print("-----------------------------------------")
print("Average Similarity :"+AverageSimilarity+"%")
print("Average Varience   :"+(AverageVarience)+"%")
print("Highest Similarity :"+str(highestValue*100)+"%")



