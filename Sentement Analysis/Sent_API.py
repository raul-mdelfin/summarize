########### Python 2.7 #############
import httplib, urllib, base64

headers = {
    # Request headers. Replace the placeholder key below with your subscription key.
    'Ocp-Apim-Subscription-Key': 'a7e293ab6ac74245b9a9a87c4bd67677',
    'Content-Type': 'application/json',
    'Accept': ' application/json'
}

params = urllib.urlencode({
})

# Replace the example URL below with the URL of the image you want to analyze.
text = "{ 'text': 'This is a sentece that is pretty good.' }"

try:
    # NOTE: You must use the same region in your REST call as you used to obtain your subscription keys.
    #   For example, if you obtained your subscription keys from westcentralus, replace "westus" in the 
    #   URL below with "westcentralus".
    conn = httplib.HTTPSConnection(' POST https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment')
    conn.request("POST", "/emotion/v1.0/recognize?%s" % params, text, headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno] {1}".format(e.strerror))
