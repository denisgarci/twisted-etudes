"""
Chat server with only select.
"""

import select, socket

class ChatServer(object):
    def __init__(self, addr):
        self.addr = addr
        self.listener = None
        self.clients = set() # set of clients (without the listener)

    def create_listener(self):
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.setblocking(0)
        listener.bind(self.addr)
        listener.listen(5)
        return listener

    @property
    def readers(self):
        return self.clients.union({self.listener})

    @property
    def writers(self):
        return [client for client in self.clients if client.wqueue]

    def start(self):
        self.listener = self.create_listener()
        while True:
            self.select_loop()

    def select_loop(self):
        rlist, wlist, _ = select.select(self.readers, self.writers, [])

        for rclient in rlist:
            if rclient is self.listener:
                self.handle_listener()  # Listener received connection request
            else:
                self.recv_msg(rclient)

        for wclient in wlist:
            self.send_msg(wclient)

    def send_msg(self, client):
        msg = client.wqueue[0]
        amt_sent = client.sock.send(msg)
        if amt_sent == len(msg):
            client.wqueue.pop(0)
        else:
            client.wqueue[0] = msg[amt_sent:]


    def recv_msg(self, client):
        # SHOULD WE DECODE HERE? msg.decode()? no if we don't have the whole bytes of a utf8 char
        msg = client.sock.recv(10)
        if not msg:
            self.clients.remove(client)
        else:
            print('Server received {0} from {1}'.format(msg, client.name))
            # Check if we actually received an entire message. An entire message is just a message finishing with an
            msg = ''.join((client.rqueue, msg))
            if msg.endswith("\n"):
                self.handle_msg(client, msg)
            else:
                self.client.rqueue = msg

    def handle_msg(self, sender, msg):
        for client in self.clients:
            if client is not sender:
                client.wqueue.append(msg)

    def handle_listener(self):
        sock, addr = self.listener.accept()
        client = Client(sock, addr)
        self.clients.add(client)
        print('{} has connected.'.format(client.name))
        client.wqueue.append('Welcome {0}. This is your address {1}.'.format(client.name, addr))




    #def send_msg_to_room(self, sender, msg):
        ##this if else if only for testing purposes
        #if sender.room:
            #clients = sender.room.clients
        #else:
            #clients = self.clients



    def remove(self, client):
        client.sock.close()
        self.clients.remove(client)


class Client(object):

    counter = 0

    def __init__(self, sock, addr, name=None):
        self.client_id = Client.counter
        Client.counter += 1
        self.sock = sock
        self.addr = addr
        if name == None:
            name = 'client{}'.format(self.client_id)
        self.name = name

        self.rqueue = ''
        self.wqueue = []

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
