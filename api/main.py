import json
import pprint
from gensim.summarization import summarize
import dataset
import http.client, urllib, base64
import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
import time
import numpy as np


db = dataset.connect('sqlite:///:memory:')
conversations = db['conversations']
images = db['images']


from pymongo import MongoClient
host = "mongo:27017"
client = MongoClient(host)
db = client.api1

def insert_conversation(session_id,message) :
	ts = time.time()
	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	db.conversations.insert({"session_id":session_id,"message":message,"timestamp":timestamp})

def insert_emotion(session_id,emotion) :
	ts = time.time()
	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	db.emotions.insert({"session_id":session_id,"emotions":emotion,"timestamp":timestamp})

def insert_session(session_id,email,subject) :
	ts = time.time()
	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	db.sessions.update({"session_id":session_id},{"session_id":session_id,"email":email,"subject":subject},True)


def _send_session_summary(session_id) :
	summary = _summary(session_id)
	result = db.sessions.find({"session_id":session_id})
	for row in result:
		subject = str(row['subject'])
		email_list = str(row['email'])
	print(summary)
	print(email_list)
	print(subject)
	email(summary,email_list,subject)
	return "{'status':'success'}"


def email(summary,email_list,subject) :
	SENDGRID_KEY='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'
	sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_KEY)
	from_email = Email("tegester@crimson.ua.edu")
	to_email = Email(email_list)
	content = Content("text/plain", summary)
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())


def _summary(session_id):
	result = db.conversations.find({"session_id":session_id})
	data = ""
	for row in result:
		if str(row['message']).endswith('.') :
			data = data + str(row['message'])+' '
		else :
			data = data+str(row['message'])+". "
	print(data)
	try : 
		summary = summarize(data)
	except :
		summary = "No summary was populated because of lack of data"

	if summary is None :
		summary = "No summary was populated because of lack of data"
	return summary



def _emotions(session_id):
	fear = []
	surprise = []
	happiness = []
	disgust = []
	neutral = []
	anger = []
	contempt = []
	sadness = []
	for row in db.emotions.find({"session_id":session_id}) :
		for r in row['emotions']:
			t = r['scores']
			fear.append(t['fear'])
			surprise.append(t['surprise'])
			happiness.append(t['happiness'])
			disgust.append(t['disgust'])
			neutral.append(t['neutral'])
			anger.append(t['anger'])
			contempt.append(t['contempt'])
			sadness.append(t['sadness'])

	emotions = ['fear','surprise','disgust','neutral','anger','contempt','sadness']
	emotions_score = [np.average(fear),np.average(surprise),np.average(happiness),np.average(disgust),np.average(neutral),np.average(anger),np.average(contempt),np.average(sadness)]
	emotion = emotions[emotions_score.index(max(emotions_score))-1]
	return str(dict(zip(emotions,emotions_score)))


from flask import Flask,render_template, request, url_for
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

@app.route("/get/<session_id>")
def get_summary(session_id):
    return _summary(session_id)

@app.route("/getemotion/<session_id>")
def get_emotions(session_id):
    return _emotions(session_id)

@app.route("/email/<session_id>")
def send_email(session_id):
    return _send_session_summary(session_id)

@app.route("/put/",methods=['POST'])
def put_message():
	data = json.loads(request.data.decode("utf-8"))
	print(data)
	msg = data['message']
	s = data['id']
	insert_conversation(s,msg)
	return "{'status':'success'}"

@app.route("/emotion/",methods=['POST'])
def emotion():
	data = json.loads(request.data.decode("utf-8"))
	print(data)
	emotion = data['emotion']
	s = data['id']
	insert_emotion(s,emotion)
	return "{'status':'success'}"

@app.route("/register/",methods=['POST'])
def register():
	print(request.data)
	data = json.loads(request.data.decode("utf-8"))
	print(data)
	sjt = data['subject']
	eml = data['email']
	s = data['id']
	insert_session(s,eml,sjt)
	return "{'status':'success'}"


