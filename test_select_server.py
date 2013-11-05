"""
Tests for socketserver
"""

import unittest
from socketserver import ChatServer, Room, Client, get_listener
import threading
import socket

class TestChatServer(unittest.TestCase):
    def test_server(self):
        addr = ('127.0.0.1', 8000)
        server = ChatServer(addr)
        self.assertTrue(True)

    def test_server_start_with_clients(self):
        addr = ('127.0.0.1', 8001)
        server = ChatServer(addr)
        t = threading.Thread(target = server.start)
        t.daemon = True
        t.start()

        client1 = socket.socket()
        client1.connect(server.listener.getsockname())
        server.select_loop()
        self.assertEqual(len(server.clients), 1)

        client2 = socket.socket()
        client2.connect(server.listener.getsockname())
        server.select_loop()
        self.assertEqual(len(server.clients), 2)

        # import time
        # time.sleep(2)
        print(server.clients)

        client1.sendall('Hello?\n')
        server.select_loop()
        server.select_loop()
        received = client2.recv(10)
        self.assertEqual('Hello?\n', received)

if __name__ == '__main__':
    unittest.main()