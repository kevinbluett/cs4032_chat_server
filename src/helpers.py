from collections import OrderedDict

__author__ = 'kevin'
import socket
from threading import Lock

class LithiumHelper(object):
    @staticmethod
    def recv_all(sock):
        read = ''
        try:
            data = sock.recv(1024)
            read += data
        except socket.error, e:
            if isinstance(e.args, tuple):
                if e[0] == socket.errno.EPIPE:
                   print "Detected remote disconnect"
                   raise e
            else:
                print "socket error ", e
        return read

    @staticmethod
    def message_dict(msg):
        map = dict()
        head = msg.split(":")[0]
        for line in msg.split("\n"):
            split = line.split(":")
            if len(split) >= 2:
                map[split[0]] = split[1]
        return (head, map)

    @staticmethod
    def revc_msg_dict(sock, count):
        return LithiumHelper.message_dict(LithiumHelper.recv_line_num(sock, count))

    @staticmethod
    def recv_line_num(sock, count):
        out = '';
        while count > 0:
            out += LithiumHelper.recv_line(sock)
            count -= 1
        return out

    @staticmethod
    def recv_text(sock):
        read = ''
        try:
            chars = []
            lst_char = ''
            while True:
                a = sock.recv(1)
                if a != "\r":
                    if (a == "\n" and lst_char == "\n") or a == "":
                        return "".join(chars)
                    else:
                        chars.append(a)
                    lst_char = a
        except socket.error, e:
            if isinstance(e.args, tuple):
                if e[0] == socket.errno.EPIPE:
                   print "Detected remote disconnect"
                   raise e
            else:
                print "socket error ", e
        return read

    @staticmethod
    def recv_line(sock):
        read = ''
        try:
            chars = []
            while True:
                a = sock.recv(1)
                if a != "\r":
                    chars.append(a)
                if a == "\n" or a == "":
                    return "".join(chars)
        except socket.error, e:
            if isinstance(e.args, tuple):
                if e[0] == socket.errno.EPIPE:
                   print "Detected remote disconnect"
                   raise e
            else:
                print "socket error ", e
        return read

    @staticmethod
    def to_message_dict(dict):
        if dict is None or len(dict) == 0:
            return ""
        out = ""
        for key, value in OrderedDict(dict).iteritems():
            out += "%s:%s\n" % (str(key), str(value))
        out += "\n"
        print out
        return out

class AtomicCount(object):
    def __init__(self):
        self.count = 0
        self.lock = Lock()

    def incr(self):
        self._add_count(1)

    def decr(self):
        self._add_count(-1)

    def _add_count(self, value):
        self.lock.acquire()
        self.count += value
        self.lock.release()
