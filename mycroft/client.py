import asyncore, socket

class MycroftClient(asynccore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_connect(self):
        pass

    def handle_read(self):
        pass

    def handle_close(self):
        pass