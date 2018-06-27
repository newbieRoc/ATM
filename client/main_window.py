import sys
from PyQt4 import QtCore, QtGui, uic
from client_sock import client_sock
from code_flag import sem_flags, func_code
import socket
from log import mylog
import threading
from printdoc import printdoc
client_log = mylog(file = "clientlog.log")
pt = printdoc()

"""
#2秒内收不到信号就停止
class timeout2(object):
    def __init__(self, sock, t):
        
        self.t = threading.Timer(t,self.process2)
        self.t.start()
        self.s = sock
        self.fault_window = faultui(self.s)
        
    def timecancel(self):
        self.t.cancel()
        
    def process2(self):
        #self.s.client_close()
        self.fault_window.exec()
        """
mainwinFile = "main_window.ui"
depositFile = "deposit.ui"
transferFile = "transfer.ui"
withdrawFile = "withdraw.ui"
faultFile = "fault.ui"
accterrFile = "acct_error.ui"
balanceerrFile = "balance_error.ui"
passwderrFile = "passwd_error.ui"
successFile = "success.ui"
#加载窗口文件
Ui_mainwin, QtBaseClass1 = uic.loadUiType(mainwinFile)
Ui_deposit, QtBaseClass2 = uic.loadUiType(depositFile)
Ui_withdraw, QtBaseClass3 = uic.loadUiType(withdrawFile)
Ui_transfer, QtBaseClass4 = uic.loadUiType(transferFile)
Ui_fault, QtBaseClass5 = uic.loadUiType(faultFile)
Ui_accterr, QtBaseClass6 = uic.loadUiType(accterrFile)
Ui_balanceerr, QtBaseClass7 = uic.loadUiType(balanceerrFile)
Ui_passwderr, QtBaseClass8 = uic.loadUiType(passwderrFile)
Ui_success, QtBaseClass9 = uic.loadUiType(successFile)

loginFile = "login.ui" # Enter file here.

Ui_login, QtBaseClass = uic.loadUiType(loginFile)


#创建一个对象，该对象就是整个窗体
class loginui(QtGui.QDialog, Ui_login):
    #窗口时会话框，设置为QtGui.QDialog窗口类型
    def __init__(self, sock):
        QtGui.QDialog.__init__(self)
        Ui_login.__init__(self)  
        self.setupUi(self)
        self.login_button.clicked.connect(self.login_button_clicked)
        self.passwd_edit.setEchoMode(QtGui.QLineEdit.Password)
        self.s = sock
        
        #实例化主窗口
        self.mainwin = main_windowui(self.s)
        #密码错误窗口
        self.passwd_errwin = passwd_errui()
        #账户不存在窗口
        self.acct_errwin = acct_errui()
        #故障窗口
        self.faultwin = faultui(self.s)
    def login_button_clicked(self):
        account = self.acct_edit.text()
        passwd = self.passwd_edit.text()
        
        sendinfo = "%s:%s" %(account, passwd)
        #print(type(sendinfo.encode('utf-8')))
        self.s.client_send(sendinfo)
        self.s.settimeout(2)
        try:
            ret_code = self.s.client_recv()
            ret_code = int(ret_code)
        except socket.timeout:
            self.s.client_close()
            self.faultwin.exec()

        if ret_code == sem_flags.SUCCESS:
            client_log.info_log("login: account:%s" %(account))
            client_log.info_log("accountlogin succeed")
            ##########
            pt.account(account)
            


            self.mainwin.exec()
        elif ret_code == sem_flags.PASSWORD_ERROR:
            client_log.error_log("login: password error")
            self.passwd_errwin.exec()
            self.s.client_close()
        elif ret_code == sem_flags.ACCOUNT_NOT_EXIST:
            client_log.error_log("login: account not exist")
            self.acct_errwin.exec()
            self.s.client_close()
            exit(1)
        else:
            self.faultwin.exec()
            self.s.client_close()






class main_windowui(QtGui.QDialog, Ui_mainwin):
    def __init__(self, sock):
        QtGui.QDialog.__init__(self)
        Ui_mainwin.__init__(self)
        self.setupUi(self)
        self.s = sock
        #设置事件连接
        self.check_balance_button.clicked.connect(self.check_balance_clicked)
        self.deposit_button.clicked.connect(self.deposit_button_clicked)
        self.withdraw_button.clicked.connect(self.withdraw_button_clicked)
        self.transfer_button.clicked.connect(self.transfer_button_clicked)
        self.quit_button.clicked.connect(self.quit_button_clicked)
        self.print_button.clicked.connect(self.print_button_clicked)
        #实例化窗口
        self.deposit_window = depositui(self.s)
        self.withdraw_window = withdrawui(self.s)
        self.transfer_window = transferui(self.s)
        self.fault_window = faultui(self.s)
        self.accterr_window = acct_errui()
        self.balanceerr_window = balance_errui()
    #查询余额按钮事件
    def check_balance_clicked(self):
      
        #清除框中内容
        
        self.text_browser.clear()
        self.s.client_send(str(func_code.CHECK_BALANCE))
        ret = self.s.client_recv()

        pt.check(ret)    

        client_log.info_log("check balance: %s" %(ret))
        
        
        
        #在框中显示
        self.text_browser.insertPlainText(ret)

    #存款按钮事件
    def deposit_button_clicked(self):
        self.s.client_send(str(func_code.DEPOSIT))
        client_log.info_log("send deposit")
        self.s.settimeout(2)
        try:
            
            ret = self.s.client_recv()
            if ret == str(sem_flags.NORMAL_CONNECTION):
                client_log.info_log("deposit: normal connection")
                self.deposit_window.exec()
                self.deposit_window.damount_edit.clear()
                
                #print("deposit finished:")
            else:
                self.s.close()
                client_log.error_log("deposit error")
                self.fault_window.exec()
        except socket.timeout:
            client_log.error_log("deposit: timeout")
            self.fault_window.exec()
            

    #取款按钮事件
    def withdraw_button_clicked(self):

        self.s.client_send(str(func_code.WITHDROW))
        #wt = timeout2(self.s, 3)
        client_log.info_log("send withdraw")
        try:

            self.s.settimeout(2)
            ret = self.s.client_recv()

            if ret == str(sem_flags.NORMAL_CONNECTION):
                #wt.timecancel()
                client_log.info_log("withdraw: normal connection")
                self.withdraw_window.exec()
                self.withdraw_window.wamount_edit.clear()
                
                #print("withdraw finished:")
                
            else:
                self.s.close()
                client_log.error_log("withdraw: error")
                self.fault_window.exec()
        except socket.timeout:
            client_log.error_log("withdraw: timeout")
            self.fault_window.exec()
            
        
    #转账按钮事件
    def transfer_button_clicked(self):
        self.s.client_send(str(func_code.TRANSFER))
        #tt = timeout2(self.s, 3)

        try:

            self.s.settimeout(2)
            ret = self.s.client_recv()

            if ret == str(sem_flags.NORMAL_CONNECTION):
                #tt.timecancel()
                client_log.info_log("transfer: normal connection")
                self.transfer_window.exec()
                self.transfer_window.amount_edit.clear()
                self.transfer_window.toacct_edit.clear()
                
                #print("transfer: finished")
            else:
                self.s.close()
                client_log.error_log("transfer: error")
                self.fault_window.exec()
        except socket.timeout:
            client_log.error_log("transfer: timeout")
            self.fault_window.exec()


        
    #打印按钮事件
    def print_button_clicked(self):
        #self.transfer_window.exec()
        #elf.transfer_window.amount_edit.clear()
        self.s.client_send(str(func_code.CHECK_BALANCE))
        ret = self.s.client_recv()

        pt.check(ret)

        self.text_browser.clear()
        printmsg = pt.print()
        self.text_browser.insertPlainText(printmsg)
        #print("print finished:")
        #xd.print()
    #退出按钮事件
    def quit_button_clicked(self):
        self.s.client_close()
        client_log.info_log("quit")
        self.close()
        exit(1)
class depositui(QtGui.QDialog, Ui_deposit):
    def __init__(self, sock):
        QtGui.QDialog.__init__(self)
        Ui_deposit.__init__(self)
        self.setupUi(self)
        self.damount_edit.clear()
        self.verify_button.clicked.connect(self.verify_button_clicked)
        self.s = sock
        self.success_window = successui()
        self.fault_window = faultui(self.s)
    def verify_button_clicked(self):
        deposit_amount = self.damount_edit.text()
        sendinfo = str(func_code.DEPOSIT)+":"+deposit_amount
        client_log.info_log("deposit: balance:%s" %(deposit_amount))
        #print("存款金额："+sendinfo)
        self.s.client_send(sendinfo)
        
        #dt = timeout2(self.s, 4)
        try:
            self.s.settimeout(10)
            ret = self.s.client_recv()
            if ret == str(sem_flags.SUCCESS):
                #dt.timecancel()
                self.s.client_send(str(sem_flags.SUCCESS))
                client_log.info_log("deposit: success")
                #print("deposit verify")
                
                pt.deposit(deposit_amount)
                self.success_window.exec()
            elif ret == str(sem_flags.ERROR):
                #dt.timecancel()
                self.s.client_send(str(sem_flags.SUCCESS))
                client_log.error_log("deposit: error")
                self.fault_window.exec()
            else:
                self.fault_window.exec()
        except socket.timeout:
            client_log.error_log("deposit: timeout")
            self.fault_window.exec()
            #print("timeout")
            
        

class withdrawui(QtGui.QDialog, Ui_withdraw):
    def __init__(self, sock):
        QtGui.QDialog.__init__(self)
        Ui_withdraw.__init__(self)
        self.setupUi(self)
        self.s = sock
        self.wamount_edit.clear()
        self.verify_button.clicked.connect(self.verify_button_clicked)
        self.success_window = successui()
        self.balanceerr_window = balance_errui()
        self.fault_window = faultui(self.s)
    def verify_button_clicked(self):
        #deposit_amount = self.damount_edit.text()
        withdraw_amount = self.wamount_edit.text()
        sendinfo = str(func_code.WITHDROW)+":"+withdraw_amount
        client_log.info_log("withdraw: balance:%s" %(withdraw_amount))
        #print("取款金额："+sendinfo)
        self.s.client_send(sendinfo)
        try:
            self.s.settimeout(10)
            #wt = timeout2(self.s, 10)
            ret = self.s.client_recv()
            if ret == str(sem_flags.BALANCE_NOT_ENOUGH):
                #wt.timecancel()
                client_log.error_log("withdraw: balance not enough")
                self.s.client_send(str(sem_flags.SUCCESS))
                self.balanceerr_window()
                #print("withdraw verify")
            elif ret == str(sem_flags.SUCCESS):
                #wt.timecancel()
                client_log.info_log("withdraw: success")
                self.s.client_send(str(sem_flags.SUCCESS))
                
                pt.withdraw(withdraw_amount)
                self.success_window.exec()
            elif ret == str(sem_flags.ERROR):
                #wt.timecancel()
                client_log.error_log("withdraw: error")
                self.s.client_send(str(sem_flags.SUCCESS))
                self.fault_window.exec()
        except socket.timeout:
            client_log.error_log("withdraw: timeout")
            self.fault_window.exec()
            #print("timeout")
            

        

        

class transferui(QtGui.QDialog, Ui_transfer):
    def __init__(self,sock):
        QtGui.QDialog.__init__(self)
        Ui_transfer.__init__(self)
        self.setupUi(self)
        
        self.s = sock
        
        self.amount_edit.clear()
        self.toacct_edit.clear()
        
        self.verify_button.clicked.connect(self.verify_button_clicked)
        self.success_window = successui()
        self.balanceerr_window = balance_errui()
        self.fault_window = faultui(self.s)
        self.accterr_window = acct_errui()
        

    def verify_button_clicked(self):
        to_account = self.toacct_edit.text()
        transfer_amount = self.amount_edit.text()
        sendinfo = str(func_code.TRANSFER) + ":" + to_account + ":" + transfer_amount
        client_log.info_log("transfer: to_account:%s, amount:%s" %(to_account, transfer_amount))
        #print(sendinfo)
        self.s.client_send(sendinfo)

        try:
            self.s.settimeout(10)
            
            ret = self.s.client_recv()

            if ret == str(sem_flags.BALANCE_NOT_ENOUGH):
               
                client_log.error_log("transfer: balance not enough")
                self.s.client_send(str(sem_flags.SUCCESS))
                self.balanceerr_window.exec()
            elif ret == str(sem_flags.ERROR):
               
                client_log.error_log("transfer: error")
                self.s.client_send(str(sem_flags.SUCCESS))
                self.fault_window.exec()
            elif ret == str(sem_flags.ACCOUNT_NOT_EXIST):
                
                client_log.error_log("transfer: account not exist")
                self.s.client_send(str(sem_flags.SUCCESS))
                self.accterr_window.exec()
            elif ret == str(sem_flags.SUCCESS):
             
                client_log.info_log("transfer: success")
                self.s.client_send(str(sem_flags.SUCCESS))
                pt.transfer(to_account, transfer_amount)
                self.success_window.exec()
                client_log.info_log("transfer: to_account " + to_account)
                client_log.info_log("transfer: transfer amount " + transfer_amount)
                #print("账户："+to_account)
                #print("转账金额："+transfer_amount)
                #print("transfer verify")
        except socket.timeout:
            client_log.error_log("transfer: timeout")
            self.fault_window.exec()
            #print("timeout")
            

        

class faultui(QtGui.QDialog, Ui_fault):
    def __init__(self, sock):
        QtGui.QDialog.__init__(self)
        Ui_fault.__init__(self)
        self.setupUi(self)
        self.verify_button.clicked.connect(self.verify_button_clicked)
        self.s = sock
    def verify_button_clicked(self):
        self.s.client_close()
        self.close()
        exit(1)


class acct_errui(QtGui.QDialog, Ui_accterr):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_accterr.__init__(self)
        self.setupUi(self)
        self.verify_button.clicked.connect(self.verify_button_clicked)

    def verify_button_clicked(self):
        self.close()
       

class balance_errui(QtGui.QDialog, Ui_balanceerr):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_balanceerr.__init__(self)
        self.setupUi(self)
        self.verify_button.clicked.connect(self.verify_button_clicked)

    def verify_button_clicked(self):
        self.close()

class passwd_errui(QtGui.QDialog, Ui_passwderr):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_passwderr.__init__(self)
        self.setupUi(self)
        self.verify_button.clicked.connect(self.verify_button_clicked)

    def verify_button_clicked(self):
        
        self.close()

class successui(QtGui.QDialog, Ui_success):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        Ui_success.__init__(self)
        self.setupUi(self)
        self.verify_button.clicked.connect(self.verify_button_clicked)

    def verify_button_clicked(self):
        
        self.close()