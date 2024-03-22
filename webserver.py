import os
from socket import * #import socket

def handle_request(request):
    # need to parse the request for the file
    lines = request.split('\r\n')   #each line has \r\n,
    request_line = lines[0]         # we got the first line
    _, path, _ = request_line.split()  #split first line to path requested

    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = current_directory + path    # combine the current directory with file name
    
    if os.path.exists(file_path):   # if it is there
        with open(file_path, 'rb') as file: # open send 200 and contents
            file_content = file.read()
        response = "HTTP/1.1 200 OK\r\n\r\n".encode() + file_content
    else:   #send 404 not there
        response = "HTTP/1.1 404 Not Found\r\n\r\n404 Not Found".encode()
    
    return response

serverPort = 12000  #set port num
serverSocket = socket(AF_INET,SOCK_STREAM)  #create socket

serverSocket.bind(('localhost',serverPort))  #bind it to port number
serverSocket.listen(1)  #listen for tcp requests
print("The server is ready to receive")

while True: #inf loop
    connectionSocket, addr = serverSocket.accept()  #waits to accept inccoming request and make new socket

    request = connectionSocket.recv(4096).decode() #recieve the HTTP request max bytes if 4096
    
    response = handle_request(request)  #function to handle the HTTP request
    
    connectionSocket.send(response) #send the message back

    connectionSocket.close()