import urllib2
import urllib
import json
import time
import threading
import re


boturl="https://api.telegram.org/bot380793674:AAFwim7Y0fVEO54I5-Ji5dIBCssvC9-hasY"

command_list=["/set_url","/reset","/help"]
sites={} # url , [user1,user2 ...]
message_queue={} # userID , [message,message,..]
curr_sites_size={} # url , size
notification_sent={} # usesr , bool
minute=60
check_timeout=20*minute


def get_page_size(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return len(the_page)

def check_equal(prev,url):
    return prev == get_page_size(url)

def send_message(fromID,text):
    values = { 'chat_id': fromID,'text': text }
    data = urllib.urlencode(values)
    r = urllib2.Request(boturl+"/sendMessage?", data)
    response = urllib2.urlopen(r)


def send_sticker(fromID,sticker):
    values={'chat_id': fromID,'sticker':sticker}
    data=urllib.urlencode(values)
    r = urllib2.Request(boturl+"/sendSticker?",data)
    response= urllib2.urlopen(r)

def wrong_input_error_handler(fromID):
    send_message(fromID,"Error! wrong input dummie")

def get_updates(offset=None):
    url=boturl+"/getUpdates?"
    if offset:
        url += "&offset="+str(offset)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page_json = json.load(response)
    return the_page_json


def url_routine(fromID):
    if len(message_queue[fromID]) <= 1:
        send_message(fromID,"wrong format /seturl <url>")
        return
    url=message_queue[fromID][1]
    matchOBJ=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    if len(matchOBJ)==0:
        send_message(fromID,"wrong format /seturl <url>,valid url expected!")
    else:
        if url in sites.keys():
            if fromID not in sites[url]:
                sites[url]+=[fromID]
                send_message(fromID,"site insert successfully, and now the watch begins....")
                del message_queue[fromID][1]
                print "url insertio e gia' sottoscritto da un altro user"
        else:
            sites[url]=[fromID]
            curr_sites_size[url]=get_page_size(url)
            del message_queue[fromID][1]
            send_message(fromID,"site insert successfully, and now the watch begins....")
            print "url inserito per la prima volta"


def help_routine(fromID):
    send_message(fromID,"help!")

request_handling_function={"/set_url":url_routine}#,"/reset":reset,"/help":help_routine}


def read_and_empty_updates():
    global offset
    update=get_updates(offset)["result"]
    i=0
    if len(update) < 1:
        return
    for index in update:
        i+=1
        #print "messaggio letto (i)="+str(i)+" cont messaggio="+index["message"]["text"]
        fromID=index["message"]["from"]["id"]
        text=index["message"]["text"].split(" ")
        if fromID in message_queue.keys():
            message_queue[fromID]+=text
        else:
            message_queue[fromID]=text
    offset+=i


def read_from_message_queue():
    if len(message_queue.keys()) < 1 :
        return
    for userID in message_queue.keys():
        if len( message_queue[userID]) < 1 :
            return
        message=message_queue[userID][0]
        #print "message in read_from_message_queue=" + message
        if message in command_list:
            #print "comando trovato"
            request_handling_function[ message ](userID)
        else:
            #print "userID: "+str(userID)+" notification_sent= "
            #print notification_sent
            if userID not in notification_sent.keys() or notification_sent[userID]==False:
                #print "error input mandato"
                notification_sent[userID]=True
                wrong_input_error_handler(userID)
        del message_queue[userID][0]


def reset_notification_sent():
    for user in notification_sent.keys():
        if len(message_queue[user]) < 1:
            notification_sent[user]=False


def check_thread_routine():
    while True:
        for url in curr_sites_size.keys():
            if check_equal(curr_sites_size[url],url) == False:
                for user in sites[url]:
                    send_message(user,"hey there, something in "+url+"has changed![removed from list]")
                    del sites[url]
        time.sleep(check_timeout)



def main():
    global offset
    offset=63569119
    t1=threading.Thread(target=check_thread_routine)
    t1.setDaemon(True)
    t1.start()
    while True :
        read_and_empty_updates()
        read_from_message_queue()
        reset_notification_sent()
        time.sleep(1)



if __name__ == '__main__':
    main()

#print("aosv vs number, expected false :"+ str(check_equal(22456,"http://www.dis.uniroma1.it/~quaglia/DIDATTICA/AOSV/")))

#TODO in TODO.txt
