#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[24]:


# Get a database reference to our posts
ref = db.reference('/')
# Read the data at the posts reference (this is a blocking operation)
df = pd.DataFrame.from_dict(ref.get())
important_features = []
#Create a list of important columns for the recommendation engine
columns = ['Location', 'Place', 'Artist', 'Genre', 'Day', 'Time of day', 'Organizer']
if df[columns].isnull().values.any() == True:
    print('Error in the dataset please validate')
#Combine imported featured in to important_featured column
def get_important_features(data):
    for i in range(0, data.shape[0]):
        important_features.append(data['Genre'][i]+','+data['Place'][i]+','+data['Artist'][i]+','+data['Location'][i]+','+data['Day'][i]+','+data['Time of day'][i]+','+data['Organizer'][i])
    return important_features
df['important_features'] = get_important_features(df)
if df[columns].isnull().values.any() == True:
    print('Error in dataset please validate')
cm = CountVectorizer().fit_transform(df['important_features'])
#Get the cosine similarity matrix from the count matrix
cs = cosine_similarity(cm)
scores = list(enumerate(cs[0]))
sorted_score = sorted(scores, key = lambda x:x[1], reverse = True)
sorted_score = sorted_score[1:]
listFINAL=[]
#sorted by gender and recommendation
data = []
data1 = []
data2 = []
data3 = []
data4 = []
data5 = []
k = 0
for item in sorted_score:
    refZERO = db.reference(str(item[0]))
    dataZERO=refZERO.get()
    event_recommendations=dataZERO.get("Recommendations (1 - 5 stars)")
    if event_recommendations == '5':
        data5.insert(k+1,item[0])
    elif event_recommendations == '4':
        data4.insert(k+1,item[0])
    elif event_recommendations == '3':
        data3.insert(k+1,item[0])
    elif event_recommendations == '2':
        data2.insert(k+1,item[0])
    elif event_recommendations == '1':
        data1.insert(k+1,item[0])
    else :
        print('weradi wage')
    k = k+1
    if k>10:
        break
#sorted based on recommendation
data=data5+data4+data3+data2+data1
#print(data)
refUSER = db.reference(str(0))
dataUSER=refUSER.get()
userLocation=dataUSER.get('Location')
#sorted by location with priority
locationHigh=[]
locationLow=[]
k1=0
for x in data:
    refFIRST = db.reference(str(x))
    dataFIRST=refFIRST.get()
    location=dataFIRST.get("Location")
    if userLocation == location:
        locationHigh.insert(k1,x)
    else:
        locationLow.insert(k1,x)
    k1 = k1+1
    if k1>10:
        break
final=locationHigh+locationLow
print(final)

ref0 = db.reference('/0')

user0=ref0.get()
print(user0)
updateuser=user0.update({'RData': final})
print(user0)
ref0.set(user0)
print(refUSER.get())
db2=firestore.client()
snapshots = list(db2.collection(u'USER').get())
for snapshot in snapshots:
    print(snapshot.to_dict())
db2.collection('USER').document('ACTIVE_USER').set(user0)
docs = db2.collection(u'USER').stream()
for doc in docs:
    print(f'{doc.id}')





