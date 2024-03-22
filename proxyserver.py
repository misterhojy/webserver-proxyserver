import hashlib
from socket import *
import sys
from signal import *

def custom_hash(string): # hash the string to make files
    hash_object = hashlib.sha256(string.encode())
    return hash_object.hexdigest()

def write(*content, prt=False): #write content to the log
    if prt:
        if len(content[0]) < 100:
            print(*content)
        else:
            print("This message is too long not print in cmd but will store at log.txt.")
    if type(content[0]) == bytes:
        content = b" ".join(content)
    else:
        content = bytes(" ".join(content), encoding="utf-8")
    with open("log.txt", "ab") as f:
        f.write(content + b"\n")

def cache(name, data):  #cache file
    write("FILE NAME: ", name)
    with open((name + ".txt"), "ab") as f:
        f.write(data + b"\n")   # might remove new line

def signal_handler(sig, frame):
    print('Proxy is Stopped.')
    sys.exit(0)

def handle_url(url):
    http_pos = url.find("://")  #if http there skip
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos + 3):]

    if temp.find("/") == 0: # if there is a / in the beginning remove it
        temp = temp[1:]

    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    page = ""
    if webserver_pos == -1: #   find the next /
        webserver_pos = len(temp)
        page = "/"
    else:
        page = temp[webserver_pos:]

    webserver = ""
    port = -1
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]
    
    requested_page = webserver + page
    hashed = custom_hash(requested_page)    # hash it to create file names
    return webserver, port, page, requested_page, str(hashed)


def handle_client(client_socket, client_address):
    original_request = client_socket.recv(4096) # recieve data from the socket
    write(original_request)
    
    request = original_request.decode(encoding="utf-8") # decode the data to extract it
    request_lines  = request.split("\r\n")
    first_line = request_lines[0]
    if (len(first_line) == 0):
        write("EMPTY LINE")
        client_socket.close()
    else: 
        _,url,_ = first_line.split(" ")
        write(url)
        webserver, port, page, requested_page, hashed = handle_url(url) # find webserver, port, page

        write("webserver: ", str(webserver))
        write("port: ", str(port))
        write("Page: ", str(page))
        write("Requested page: ", str(requested_page))
        write("Hashed: ", hashed)

        if (webserver == "favicon.ico"):    #ignore favicon
            client_socket.close()
        else:
            try:
                with open((hashed + ".txt"), "rb") as f:    #if we can open it then it is cached
                    write("CACHED")
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        client_socket.send(chunk)

            except FileNotFoundError:   # if we cant open it it isnt cached
                write("NOT CACHED")
                server_socket = socket(AF_INET, SOCK_STREAM)
                server_socket.connect((webserver, port))    # connect to the webserver and port

                #change request data to send to webserver
                request_lines = original_request.decode(encoding="utf-8").split("\r\n")
                first_line = request_lines[0]
                method,_,protocol = first_line.split(" ")
                new_line = " ".join([method, page, protocol])   # replace url with page

                request_lines[0] = new_line
                if (port != 80):
                    request_lines[1] = "Host: " + webserver
                else:
                    request_lines[1] = "Host: " + webserver + ":" + str(port)   # change the Host: to correct one
                new_request = "\r\n".join(request_lines)

                write(new_request)
                server_socket.send(new_request.encode())    # send the new request to the webserver
                response = server_socket.recv(4096) # retrieve the response
                server_socket.close()   # close socket proxy to webserver

                client_socket.send(response)    # send it to the client
                cache(hashed, response) # cache the response
                client_socket.close()   # close client socket

        client_socket.close()

proxy_server_port = 8080    # PORT NUMBER FOR PROXY
proxy_server_host = 'localhost' # LOCAL HOST
proxy_server_socket = socket(AF_INET, SOCK_STREAM)
proxy_server_socket.bind((proxy_server_host, proxy_server_port))    # bind together
proxy_server_socket.listen(1)   # listen to 1 at a time
signal(SIGINT, signal_handler)
print("[*] Server is Ready to Receive")
print("To Stop Server (ctrl + c)")

while True:
    client_socket, client_address = proxy_server_socket.accept()    # wait for client to connect
    handle_client(client_socket, client_address)    # handle it in main functions