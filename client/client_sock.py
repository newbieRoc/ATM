import socket


class client_sock(object):
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("127.0.0.1",10086))

    def client_recv(self, size = 1024):
        self.data = self.s.recv(size)
        self.data = str(self.data, encoding = 'utf-8')
        return self.data
    
    def client_send(self,dat):
        dat = bytes(dat, encoding = 'utf-8')
        self.s.sendall(dat)

    def client_close(self):
        self.s.close()

    def settimeout(self, time):
        self.s.settimeout(time)

