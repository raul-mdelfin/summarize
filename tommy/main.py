import httplib, urllib, base64
import json
from flask import Flask, render_template, request, jsonify
from werkzeug import secure_filename
import os

app = Flask(__name__)


@app.route('/')
def start():
    return render_template('upload.html')

@app.route('/result', methods=['POST','GET'])
def result():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        filename = secure_filename(f.filename)
        output = call_emotion_api(filename)
        # os.remove(filename)
        return render_template('result.html', output=json.dumps(output, indent=2))

def call_emotion_api(filename):
    with open(filename,'rb') as image:
        f = image.read()
        b = bytearray(f)
        json_result = emotion_api(b)
    return json_result

def emotion_api(bytestream):
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '3b685049edab4b31ab3f71ca5d91b699',
    }

    params = urllib.urlencode({})

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, bytestream, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        json_data = json.loads(data)
        return json_data
    except Exception as e:
        return []

if __name__ == '__main__':
    app.run(debug = True, threaded=True)
