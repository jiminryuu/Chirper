# Ji Min Ryu
# My personal project for designing a rest API webserver
# I will serve a website that u can post tweets on
# the first cmd line argument must be the port that it will connect too, and it will connect to local host ip or 127.0.0.1

import socket
import threading
import sys
import os
import json

#MIME dictionary
content_types = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'html': 'text/html',
    'json': 'application/json',
    'txt': 'text/plain',
    'xml': 'application/xml',
    'ico': 'image/x-icon',
    'js': 'application/javascript'
}

# where the tweets will be kept, must be in key value pairs, will be added by curr obj length + 1
database = {

}


#Creates a new socket and returns it
def create_socket() :

    port = int(sys.argv[1]) #the port will be the first argument
    host = ''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # we can reuse port

    sock.bind((host,port))
    sock.listen() # setting to empty for now so we have a bigger queue
    
    return sock

def req_manage(sock:socket):
    while True:

        conn , addr = sock.accept()
        with conn:
            try:
                print('connected by', addr)
                request_handler(conn)
            except Exception as e:
                print(e.__str__)    


#sends it to the correct request handler
def request_handler(conn:socket) :
    data = conn.recv(1024).decode("UTF-8")
    print(data)
    try :
        headers_recv = data.split('\r\n')[0] # get first line
        headers_recv = headers_recv.split(' ') # split line into tokens (format : [REQ] [PATH] [HTTP VERSION])
        api_request = "/api" in headers_recv[1] # means that this is an api request
        
        body = data.split('\r\n\r\n')[1]
        if(api_request): # send to appropriate request handler
            api_requests(conn,headers_recv,body)
        else:
            static_requests(conn,headers_recv)

    except BrokenPipeError:
        print("broken pipe")
        conn.close()

    except Exception as e :
        print(e)
        conn.close()
        
                


def static_requests(conn:socket,headers) :
    try:
        path = 'index.html' # default file to serve

        if(headers[1] != "/") : #if theyre not requesting just the default page then give them the right page

            path = headers[1].replace('/','',1) #format so the first / is taken away
            
        send = open(path,'rb') #open and read in byte mode
        send = send.read()
            
        header = build_header(send,path)
        conn.sendall(header.encode() + send) # send header and info
    except IOError :
        conn.sendall(b'HTTP/1.1 404 file not found\r\n\r\n')


def api_requests(conn:socket, headers, body) :
    try:
        if(headers[0] == "GET"):
            get_tweet(conn)
        elif(headers[0] == "POST" and "/tweet" in headers[1]): #if theres /tweet in the request we are creating a tweet
            create_tweet(conn,body)
        elif(headers[0] == "POST"): #if tweet is not in path, its just a login POST request
            login(conn,body)
        
    except Exception:
        #change this mf error code before you hand it in 
        conn.sendall(b'HTTP/1.1 500 IDK WHAT HAPPENED!\r\n\r\n')


def get_tweet(conn:socket):
    tweets = json.dumps(database) #sends it in format {"ID#": "msg1", "ID#": "msg2"} etc etc...
    header = build_header(tweets, '.txt')
    conn.sendall(header.encode() + tweets.encode())

    

def create_tweet(conn, body):
    try:

        new_tweet_id = len(database) + 1

        msg = json.loads(body) #load the msg it should be in json form
        tweet = msg["input"] #get the tweet
        username = msg["username"]
        database[new_tweet_id] = username + " says " + tweet #store it in database

        #build a response header
        status_code = 'HTTP/1.1 200 OK\r\n'
    except Exception:
        status_code = 'HTTP/1.1 500 COULD NOT ADD TWEET TO DATABASE\r\n'

    name = "Server: ECKS SERVER"
    colon = "\r\n\r\n"  

    header = status_code + name + colon
    conn.sendall(header.encode())


def login(conn, body):
    #parse the body it will have the format name:'input'\n
    username = body.split('\n')[0]
    username = username.replace("name:", '', 1)

    #build a response header with a cookie
    status_code = 'HTTP/1.1 200 OK\r\n'
    name = "Server: ECKS SERVER\r\n"
    cookie = "Set-Cookie: " + "username=" + username + "; Max-Age=900; path=/" #set time to 15 mins and path to / so the 
    colon = "\r\n\r\n"                                                         #cookie can be acessed from all parts of our webserver

    header = status_code + name + cookie + colon
    conn.sendall(header.encode())


# build response header
def build_header(to_send,path) :

    status_code = 'HTTP/1.1 200 OK\r\n'
    content_length = "Content-Length: " + str(len(to_send)) + "\r\n"
    file_sufx = "Content-Type: "

    file_type = path.split(".")[1]
    file_type = content_types[file_type] # get the MIME type

    file_type = file_type + "\n"
    name = "Server: ECKS SERVER"
    colon = "\r\n\r\n"

    header = status_code + content_length + file_sufx + file_type + name + colon   
    return header



def main():
    try:
        sock = create_socket() # our socket
        req_manage(sock)
    except KeyboardInterrupt:
        sys.exit()


main()
