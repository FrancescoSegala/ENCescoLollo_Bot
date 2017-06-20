import urllib2
import urllib
import json
import time
import threading
import re


boturl="https://api.telegram.org/bot380793674:AAFwim7Y0fVEO54I5-Ji5dIBCssvC9-hasY"

command_list=["/set_url","/cancel","/help"]
sites={} # url , [user1,user2 ...]
message_queue={} # userID , [message,message,..]
curr_sites_size={} # url , size
notification_sent={} # usesr , bool
minute=60
check_timeout=20 #*minute
help_message='''Hi, this is a bot that look at a webpage periodically and if something changes it send you a notification.\n
                Available commands are: /set_url <url>  this command say to this bot what site to watch.
                                        /help    show this wonderful help message.
                                        /cancel <url>  this command say to this bot to forget about this site'''

jon_sticker="CAADAgADSAADFcgcBrWClE7tlxOPAg"

def get_page_size(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return len(the_page)

def check_equal(prev,url):
    return prev == get_page_size(url)


keyboard=[['Yes'],['No']]

def send_menu_callback(fromID,msg):
    reply_markup = {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    params = urllib.urlencode({
          'chat_id': str(fromID),
          'text': msg.encode('utf-8'),
          'reply_markup': reply_markup,
          'disable_web_page_preview': 'true',
    })
    resp = urllib2.urlopen(boturl + '/sendMessage', params).read()

def send_button_message(fromID,msg,url):
    keyboard= json.dumps({'inline_keyboard': [[{'text': 'go to page', 'url': url}]]})
    values = { 'chat_id': fromID,'text': msg , 'reply_markup': keyboard}
    data = urllib.urlencode(values)
    r = urllib2.Request(boturl+"/sendMessage", data)
    response = urllib2.urlopen(r)

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
    if len(message_queue[fromID].split(" ") ) <= 1:
        send_message(fromID,"wrong format /seturl <url>")
        return
    url=message_queue[fromID].split(" ")[1]
    matchOBJ=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    if len(matchOBJ)==0:
        send_message(fromID,"wrong format /set_url <url>,valid url expected!")
    else:
        if url in sites.keys():
            if fromID not in sites[url]:
                sites[url]+=[fromID]
                send_message(fromID,"site insert successfully, and now the watch begins....")
                send_sticker(fromID,jon_sticker)
                print "url insertio e gia' sottoscritto da un altro user"
            else:
                send_message(fromID,"we are already watching this site for you, let us work dude!")
        else:
            sites[url]=[fromID]
            curr_sites_size[url]=get_page_size(url)
            send_message(fromID,"site insert successfully, and now the watch begins....")
            send_sticker(fromID,jon_sticker)
            print "url inserito per la prima volta"


def help_routine(fromID):
    send_message(fromID,help_message)



def cancel_routine(fromID):
    if len(message_queue[fromID].split(" ") ) <= 1:
        send_message(fromID,"wrong format /cancel <url>")
        return
    url=message_queue[fromID].split(" ")[1]
    matchOBJ=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    if len(matchOBJ)==0:
        send_message(fromID,"wrong format /cancel <url>,valid url expected!")
    else:
        if url in sites.keys():
            if fromID in sites[url]:
                sites[url].remove(fromID)
                send_message(fromID,"ok, now is your job to check this site dude. I quit!")
                if len(sites[url])==0:
                    del sites[url]
            else:
                send_message(fromID,"ehi man you are not watching this site...")
        else:
            send_message(fromID,"ehi man this site does not exist!")



request_handling_function={"/set_url":url_routine,"/help":help_routine,"/cancel":cancel_routine}

def read_and_empty_updates():
    global offset
    update=get_updates(offset)["result"]
    i=0
    if len(update) < 1:
        return
    for index in update:
        i+=1
        if "text" not in index["message"]:
            print "skip"
        else:
            print "messaggio letto (i)="+str(i)+" cont messaggio="+index["message"]["text"]
            fromID=index["message"]["from"]["id"]
            text=index["message"]["text"]#.split(" ")
            if fromID in message_queue.keys():
                message_queue[fromID]+=text
            else:
                message_queue[fromID]=text
    print message_queue
    offset+=i


def read_from_message_queue():
    num_user=len(message_queue.keys())
    if num_user < 1 :
        return
    for userID in message_queue.keys():
        if len( message_queue[userID]) < 1  :
            continue
        message=message_queue[userID].split(" ")
        #print "message in read_from_message_queue=" + message
        if message[0] in command_list:
            print "comando trovato"
            request_handling_function[ message[0] ](userID)
        else:
            wrong_input_error_handler(userID)
        del message_queue[userID]




def check_thread_routine():
    while True:
        for url in curr_sites_size.keys():
            if check_equal(curr_sites_size[url],url) == False:
                for user in sites[url]:
                    send_button_message(user,"hey there, something in "+url+" has changed![removed from list]",url)
                    del sites[url]
        time.sleep(check_timeout)


def get_offset():
    updates=get_updates()
    if len( updates["result"]) > 0:
        return updates["result"][0]["update_id"]
    else:
        return -1

def main():
    global offset
    offset=get_offset()
    t1=threading.Thread(target=check_thread_routine)
    t1.setDaemon(True)
    t1.start()
    while True :
        print "ciclo"
        read_and_empty_updates()
        read_from_message_queue()
        time.sleep(1)



if __name__ == '__main__':
    main()

#print("aosv vs number, expected false :"+ str(check_equal(22456,"http://www.dis.uniroma1.it/~quaglia/DIDATTICA/AOSV/")))

#TODO in TODO.txt
