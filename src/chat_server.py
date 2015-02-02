import time
import sys

__author__ = 'kevin'
from helpers import *

class Room:
    title = ""
    room_id = ""
    # Each client is a tuple of (name, queued_msg)
    clients = dict()

    def __init__(self, title):
        self.title = title
        self.room_id = abs(hash(title))

    def send_message(self, name, message):
        for name, (join_id, client, queue) in self.clients.iteritems():
            queue.append((name, message))
            while len(queue) > 0:
                (nm, msg) = queue.pop()
                client.send(LithiumHelper.to_message_dict((
                    ("CHAT", self.room_id),
                    ("CLIENT_NAME", nm),
                    ("MESSAGE", msg)
                )))
            self.clients[name] = (join_id, client, queue)

    def join(self, client, name):
        join_id = abs(hash(name+str(time.time())))
        self.clients[name] = (join_id, client, list())
        return join_id

    def leave(self, client, name, join_id):
        if name in self.clients and self.clients[name][0] == int(join_id):
            del self.clients[name]
        else:
            print "Client does not exist"

    def __len__(self):
        return len(self.clients)

class ChatServer:

    clients = list()
    rooms = dict()
    room_ref = dict()

    def __init__(self):
        pass

    def client_join(self, client):
        self.clients.append(client)

    def message_looper(self, client):
        e_count = 0
        while (client in self.clients) and :
            try:
                (head, msg_dict) = LithiumHelper.revc_msg_dict(client, 1)
                if not self.primitive_response(client, head):
                    client.send(self.message_parsing(head, msg_dict, client))
            except Exception, e:
                return LithiumHelper.to_message_dict(self.invalid_message())

    def message_parsing(self, head, msg_dict, client):
        ops = {
          "JOIN_CHATROOM":  lambda : self.join_chatroom(client, msg_dict, 3),
          "LEAVE_CHATROOM": lambda : self.leave_chatroom(client, msg_dict, 2),
          "DISCONNECT":     lambda : self.disconnect_client(client, 2),
          "CHAT":           lambda : self.send_chat(client, msg_dict, 2)
        }

        f = ops.get(head, None)

        try:
            if f:
                return LithiumHelper.to_message_dict(f())
            else:
                return LithiumHelper.to_message_dict(self.invalid_message())
        except Exception, e:
            print "Generic error occured."

    def invalid_message(self):
        return (
            ("ERROR_CODE", 1),
            ("ERROR_DESCRIPTION", "Invalid message sent to server")
        )

    def send_chat(self, client, hdr_dict, num):
        (_, msg_dict) = LithiumHelper.revc_msg_dict(client, num)

        chat_msg = LithiumHelper.recv_text(client)[8:]

        ref = hdr_dict["CHAT"]

        if int(ref) in self.room_ref:
            room = self.rooms[self.room_ref[int(ref)]]
            room.send_message(msg_dict["CLIENT_NAME"], chat_msg)

        return {}

    def disconnect_client(self, client, num):
        (_, msg_dict) = LithiumHelper.revc_msg_dict(client, num)
        self.clients.remove(client)
        return {}

    def join_chatroom(self, client, hdr_dict, num):
        (_, msg_dict) = LithiumHelper.revc_msg_dict(client, num)

        room_title = hdr_dict["JOIN_CHATROOM"]

        if not room_title in self.rooms:
            self.rooms[room_title] = Room(room_title)
            self.room_ref[self.rooms[room_title].room_id] = room_title

        id = self.rooms[room_title].join(client, msg_dict["CLIENT_NAME"])

        client.send(LithiumHelper.to_message_dict((
            ("JOINED_CHATROOM", room_title),
            ("SERVER_IP", "0.0.0.0"),
            ("PORT", 0),
            ("ROOM_REF", self.rooms[room_title].room_id),
            ("JOIN_ID", id)
        ))

        self.rooms[room_title].send_message(msg_dict["CLIENT_NAME"], "%s has joined this chatroom." % (msg_dict["CLIENT_NAME"]))

        return ()


    def leave_chatroom(self, client, hdr_dict, num):
        (_, msg_dict) = LithiumHelper.revc_msg_dict(client, num)

        ref = hdr_dict["LEAVE_CHATROOM"]


        if int(ref) in self.room_ref:
            room = self.rooms[self.room_ref[int(ref)]]
            room.leave(client, msg_dict["CLIENT_NAME"], msg_dict["JOIN_ID"])

            # Delete the room if there are no more clients in it
            if len(room.clients) == 0:
                del self.rooms[self.room_ref[int(ref)]]
                del self.room_ref[int(ref)]

            return (
                ("LEFT_CHATROOM", ref),
                ("JOIN_ID", msg_dict["JOIN_ID"])
            )
        else:
            return self.invalid_message()

    def primitive_response(self, client, head):
        if len(head) >= 5 and head[:4] == "HELO":
            client.send("%sIP:%s\nPort:%s\nStudentID:11311101" % (head, socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0], sys.argv[1]))
            return True
        elif len(head) >= 5 and head[:12] == "KILL_SERVICE":
            self.clients.remove(client)
            client.close()
            return True
        return False
