"""
Chat server with only select.
"""

import select, socket

class ChatServer(object):
    def __init__(self, addr, name = "server"):
        self.listener = self.create_listener(addr) # listening socket
        self.name = name
        self.clients = [] # clients are Person objects (except for listener)
        self.rooms = set()

        self.wqueue = dict() # values:
        self.rqueue = dict() # values: string not ending with new line except for [-1]

    def create_listener(self, addr):
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.setblocking(0)
        listener.bind(addr)
        listener.listen(5)
        return listener

    @property
    def readers(self):
        return self.clients + [self.listener]

    @property
    def writers(self):
        return [client for client in self.wqueue if self.wqueue[client]]

    def start(self):
        while True:
            self.select_loop()

    def select_loop(self):
        rlist, wlist, _ = select.select(self.readers, self.writers, [])

        for rclient in rlist:
            if rclient is self.listener:
                # Listener received connection request
                self.handle_listener()
            else:
                self.get_msg(rclient)

        for wclient in wlist:
            for msg_list in self.rqueue:
                if msg_list:
                    msg = msg_list.pop(0)
                    self.handle_msg(rclient, msg)

            next_msg = self.wqueue[wclient].pop(0)
            amt_sent = wclient.sock.send(next_msg)
            self.wqueue[wclient].insert(0, next_msg[amt_sent:])

    def get_msg(self, client):
         # SHOULD WE DECODE HERE? msg.decode()?
        # handles parsing messages
        msg = client.sock.recv(10).decode()
        if not msg:
            self.clients.remove(client)
        else:
            print("received", msg)
            msg = "".join((self.rqueue[client], msg))
            #if msg.endswith("\n"):
                #msg_to_send = msg
            #else:
                #try:
                    #msg_to_send = msg[:msg.rindex("\n")+1]
                #except ValueError:
                    #self.rqueu[client] = msg
                    #msg_to_send = None
            self.handle_msg(client, msg)


    def handle_listener(self):
        sock, addr = self.listener.accept()
        client = Client(sock, addr)
        self.clients.append(client)
        self.wqueue[client] = []
        print("{} has connected.".format(client.name))
        # Insert welcome message.

    def handle_msg(self, sender, msg): # sender = socket
        print("Client says:", msg)
        #self.send_msg_to_room(sender, msg)
        for client in self.clients:
            if client is not sender:
                self.wqueue[client].append(msg.encode())


    #def send_msg_to_room(self, sender, msg):
        ##this if else if only for testing purposes
        #if sender.room:
            #clients = sender.room.clients
        #else:
            #clients = self.clients




    def remove(self, client):
        client.sock.close()
        self.clients.remove(client)


class Room(object):
    def __init__(self, name):
        self.name = name
        self.clients = set()

    # def add_client(self):
    #     pass

    def kick_client(self):
        pass


class Client(object):
    def __init__(self, sock, addr, name="anon"):
        self.sock = sock
        self.addr = addr
        self.name = name
        self.room = None

    def set_name(self, name):
        self.name = name

    def join_room(self, room):
        room.clients.add(self)
        self.rooms.add(room)

    def leave_room(self, room):
        room.clients.remove(self)
        self.rooms.remove(room)

    def fileno(self):
        return self.sock.fileno()



def main():
    """
    Run the server
    """
    addr = ('127.0.0.1', 8000)

    print("Listening at", addr)
    server = ChatServer(addr)
    server.start()

if __name__ == '__main__':
    main()
