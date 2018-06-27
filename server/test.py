import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.0.1",10086))


#bytes(string, encoding="utf-8")
#str.encode(string)
while 1:
    in1 = input()
    #in1.encode('utf-8')
    in1 = bytes(in1, encoding='utf-8')
    s.send(in1)
    r = s.recv(1024)
    str(r,encoding = 'utf-8')
    print(r)
#print(string)


