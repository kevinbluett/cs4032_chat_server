import select
from thread_pool import *
from helpers import *

class LithiumThreadPoolDispatcher():
    """ Dispatches opened sockets into the threadpool """

    def __init__(self, server, pair):
        server.pool.add_task(self.process_input, server, pair)

    def process_input(self, server, pair):
        try:
            server.handler(server, pair)
        except socket.error, e:
            print e
            if isinstance(e.args, tuple):
                if e[0] == socket.errno.EPIPE:
                    # remote peer disconnected
                    print "Detected remote disconnect"
                    server.count.decr()

class LithiumThreadPoolServer():

    MAX_CONNECTIONS = 2000

    def __init__(self, host, port, handler, workers=10):
        self.pool = LithiumThreadPool(workers)
        self.count = AtomicCount()
        self.handler = handler
        self.host = host
        self.port = port

    def handle_accept(self, s):
        pair = s.accept()
        if pair is not None:
            sock, addr = pair
            self.count.incr()
            print 'Incoming connection from %s, socket count %d' % (repr(addr), self.count.count)
            if self.count.count > self.MAX_CONNECTIONS:
                sock.send("503 - Service unavailable\n")
                sock.close()
                self.count.decr()
            else:
                handler = LithiumThreadPoolDispatcher(self, pair)


    def loop(self):
        self.stop_looper = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print "Starting Lithuim threaded pool server \nListening on %s:%d" % (self.host, self.port)

        while not self.stop_looper:
            try:
                read_sockets, _, _ = select.select([self.sock],[],[])
                for sock in read_sockets:
                    if sock is self.sock:
                        self.handle_accept(self.sock)
            except select.error:
                break

    def shutdown(self, safe=True):
        self.stop_looper = True
        if safe and self.pool is not None:
            self.pool.shutdown()
        self.sock.close()

