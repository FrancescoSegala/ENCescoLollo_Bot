import urllib2
import urllib

boturl="https://api.telegram.org/bot380793674:AAFwim7Y0fVEO54I5-Ji5dIBCssvC9-hasY"


def send_crash():
    values = { 'chat_id': 55870602,'text': "[ERROR:server crash]" }
    data = urllib.urlencode(values)
    r = urllib2.Request(boturl+"/sendMessage?", data)
    response = urllib2.urlopen(r)



send_crash()
