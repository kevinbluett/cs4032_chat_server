import asyncore, sys, socket
from async.server import *
from threaded.server import *
from helpers import *
from chat_server import *

chat = ChatServer()

def lab2_handler(server, (sock, addr)):
    sock.setblocking(True)
    if not sock in chat.clients:
        chat.client_join(sock)
        Thread(target=chat.message_looper, args=[sock]).start()

    # if data == "KILL_SERVICE\n":
    #     if server is not None:
    #         Thread(target=server.shutdown, args=[False]).start()
    # else:
    #     sock.send("%s\nStudentID:11311101" % (data))

    # Kill the socket
    #sock.close()
    #server.count.decr()

def start_server():
    # Start the server in thread pool mode
    LithiumAsyncServer('localhost', int(sys.argv[1]), lab2_handler)
    asyncore.loop()

if __name__ == '__main__':
    start_server()