"""
    communication with client
"""
import sys
import socket
import threading
from log import mylog
from sqldb_serv import sqldb_ops
from code_flag import dbop_code, sem_flags, func_code
import time
serv_log = mylog(file = "servlog.log")
#连接数据库
try:
    dbop = sqldb_ops("localhost","root","ankh","abank")
    serv_log.info_log("succeed to connect the database ")
except:
    #print("longin failed\n")
    serv_log.error_log("failed to connect the database")
    sys.exit(1)



class timeout1():
    def __init__(self, sock, msg):
        
        self.s = sock
        self.t = threading.Timer(3, self.process1)
        self.t.start()
        self.msg = msg
        
        print("timeout1 start")
        
        
    def timecancel(self):    
        self.t.cancel()

    def process1(self):
        try:
            self.s.sendall(self.msg.encode('utf-8'))
            serv_log.info_log("resend ack")
            tt = timeout2(sock)
            da = self.s.recv_data()
            if da:
                tt.timecancel()
                serv_log.info_log("the second time recive ack")
        except ConnectionAbortedError:
            serv_log.error_log("fail connection")



class timeout2():
    def __init__(self, sock):
        
        self.s = sock
        self.t = threading.Timer(3, self.process2)
        self.t.start()
        #self.msg = msg
        
        print("timeout2 start")
        
        
    def timecancel(self):    
        self.t.cancel()

    def process2(self):
        self.s.close()
        serv_log.info_log("fail ack")



def recv_data(sock):
    try:
        data = sock.recv(1024)
        data = str(data, encoding = 'utf-8')
        data = data.split(":")
        return data
    except:
        serv_log.error_log("connection error")
        return
    


def tcplink(sock, addr):
    #处理登陆信息
    serv_log.info_log("ready to login")
    login = recv_data(sock)

    account = int(login[0])
    password = int(login[1])
    
    status = dbop.check_login(account, password)

    if status == dbop_code.ACCOUNT_NOT_EXIST:
        sock.sendall(str(sem_flags.ACCOUNT_NOT_EXIST).encode('utf-8'))
        serv_log.error_log("login failed: account not exist")
        sock.close()
        return
    elif status == dbop_code.PASSWD_ERROR:
        sock.sendall(str(sem_flags.PASSWORD_ERROR).encode('utf-8'))
        serv_log.error_log("login failed: password error.")
        sock.close()
        return
    elif status ==dbop_code.SUCCESS:
        sock.sendall(str(sem_flags.SUCCESS).encode('utf-8'))
        serv_log.info_log("%d login succeed"%(account))
    elif status == dbop_code.ERROR:
        sock.sendall(str(sem_flags.ERROR).encode('utf-8'))
        serv_log.error_log("login failed.")
        sock.close()
        return
    
    #处理用户操作
    while True:
        
        data = recv_data(sock)
        #time.sleep(5)
        #查询余额
        if data[0] == str(func_code.CHECK_BALANCE):
            serv_log.info_log("%d: check balance operation" %(account))
            ret_balance = dbop.check_balance(account)
            sendinfo = "%.2f" %(ret_balance)
            sock.sendall(sendinfo.encode('utf-8'))
            serv_log.info_log("%d check balance finished" %(account))
        #存款
        elif data[0] == str(func_code.DEPOSIT):
            #发送已连接信号
            sock.sendall(str(sem_flags.NORMAL_CONNECTION).encode('utf-8'))
            serv_log.info_log("%d deposit: normal connection." %(account))
            #接收存款消息及金额
            
            data2 = recv_data(sock)
            
            try:
                amount = float(data2[1])
            except:
                sock.sendall(str(sem_flags.AMOUNT_ERROR).encode('utf-8'))
                serv_log.error_log("%d deposit: amount error %d."%(account,amount))
            ret_status = dbop.increase_money(account, amount)
            #time.sleep(5)
            #sock.settimeout(10)
            if ret_status == dbop_code.ERROR:
                #出错
                sock.send(str(sem_flags.ERROR).encode('utf-8'))
                serv_log.error_log("%d deposit failed" %(account))
             
                dt = timeout1(sock, str(sem_flags.ERROR))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    dt.timecancel()
                
            elif ret_status == dbop_code.SUCCESS:
                #成功
                
                sock.sendall(str(sem_flags.SUCCESS).encode('utf-8'))
                serv_log.info_log("%d deposit succeed" %(account))
                dt = timeout1(sock, str(sem_flags.SUCCESS))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    dt.timecancel()
                
        #取款
        elif data[0] == str(func_code.WITHDROW):
            #发送已成功连接信号
            sock.sendall(str(sem_flags.NORMAL_CONNECTION).encode('utf-8'))
            serv_log.info_log("%d withdraw: normal connection." %(account))
            #接收取款消息及金额
            data2 = recv_data(sock)
            
            try:
                amount = float(data2[1])
            except:
                sock.sendall(str(sem_flags.AMOUNT_ERROR).encode('utf-8'))
                serv_log.error_log("%d withdraw: amount error."%(account))
            #time.sleep(5)
            ret_status = dbop.decrease_money(account,amount)
            if ret_status == dbop_code.BALANCE_NOT_ENOUGH:
                #余额不够
                sock.sendall(str(sem_flags.BALANCE_NOT_ENOUGH).encode('utf-8'))
                serv_log.error_log("%d withdraw: balance not enough." %(account))
               
                wt = timeout1(sock, str(sem_flags.BALANCE_NOT_ENOUGH))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    wt.timecancel()

            elif ret_status != dbop_code.SUCCESS:
                #出错
                sock.sendall(str(sem_flags.ERROR).encode('utf-8'))
                serv_log.info_log("%d withdraw: error." %(account))

                wt = timeout1(sock, str(sem_flags.ERROR))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    wt.timecancel()

            else:
                #成功
                sock.sendall(str(sem_flags.SUCCESS).encode('utf-8'))
                serv_log.info_log("%d withdraw: success." %(account))

                wt = timeout1(sock, str(sem_flags.SUCCESS))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    wt.timecancel()
        #转账
        elif data[0] == str(func_code.TRANSFER):
            #发送已成功连接信号
            sock.sendall(str(sem_flags.NORMAL_CONNECTION).encode('utf-8'))
            serv_log.info_log("%d transfer: normal connection." %(account))
            #接收取款消息及金额
            data2 = recv_data(sock)
            try: 
                to_account = int(data2[1])
                amount = float(data2[2])
            except:
                sock.sendall(str(sem_flags.AMOUNT_ERROR).encode('utf-8'))
                serv_log.error_log("%d transfer: amount error."%(account))
            ret_status = dbop.decrease_money(account, amount)

            if ret_status == dbop_code.BALANCE_NOT_ENOUGH:

                sock.sendall(str(sem_flags.BALANCE_NOT_ENOUGH).encode('utf-8'))
                serv_log.info_log("%d transfer: banlance not enough." %(account))

                tt = timeout1(sock, str(sem_flags.BALANCE_NOT_ENOUGH))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    tt.timecancel()


            elif ret_status == dbop_code.ERROR:
                sock.sendall(str(sem_flags.ERROR).encode('utf-8'))
                serv_log.info_log("%d transfer: error." %(account))

                tt = timeout1(sock, str(sem_flags.ERROR))
                data3 = recv_data(sock)
                if data3:
                    serv_log.info_log("recive ack")
                    tt.timecancel()


            elif ret_status == dbop_code.SUCCESS:
                
                ret_status = dbop.increase_money(to_account, amount)
                if ret_status == dbop_code.ACCOUNT_NOT_EXIST:
                    ret_status = dbop.increase_money(account, amount)
                    serv_log.info_log("%d transfer: %d account not exist." %(account,to_account))
                    sock.sendall(str(sem_flags.ACCOUNT_NOT_EXIST).encode('utf-8'))

                    tt = timeout1(sock, str(sem_flags.ACCOUNT_NOT_EXIST))
                    data3 = recv_data(sock)
                    if data3:
                        serv_log.info_log("recive ack")
                        tt.timecancel()
                
                elif ret_status == dbop_code.ERROR:
                    ret_status = dbop.increase_money(account, amount)
                    sock.sendall(str(sem_flags.ERROR).encode('utf-8'))
                    serv_log.info_log("%d transfer: error." %(account))

                    tt = timeout1(sock, str(sem_flags.ERROR))
                    data3 = recv_data(sock)
                    if data3:
                        serv_log.info_log("recive ack")
                        tt.timecancel()
                
                elif ret_status == dbop_code.SUCCESS:
                    sock.sendall(str(sem_flags.SUCCESS).encode('utf-8'))  
                    serv_log.info_log("%d transfer: success." %(account))   
                    tt = timeout1(sock, str(sem_flags.SUCCESS))
                    data3 = recv_data(sock)
                    if data3:
                        serv_log.info_log("recive ack")
                        tt.timecancel()         
        #退出
        elif data[0] == str(func_code.QUIT):
            #发送已成功连接信号
            sock.sendall(str(sem_flags.NORMAL_CONNECTION).encode('utf-8'))
            serv_log.info_log("%d logout: normal connection." %(account))
            sock.close()
            serv_log.info_log("%d logout: success." %(account))
            return
        
        #UNKNOWUNKNOW
        #elif data[0] == str(func_code.UNKNOW):
            #if ret_status == dbop_code.SUCCESS:
           #     sock.sendall(str(sem_flags.SUCCESS).encode('utf-8'))
            #    serv_log.info_log("%d unknow: status success." %(account))
           # else:
            #    sock.sendall(str(sem_flags.ERROR).encode('utf-8'))
            #    serv_log.info_log("%d unknow: status error." %(account))
    sock.close()

port = 10086

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("127.0.0.1", 10086))
s.listen(10)

while True:
   
    sock, addr = s.accept()
   
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()

