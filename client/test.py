import sys
from PyQt4 import QtCore, QtGui, uic
import main_window
#from  main_window import main_windowui, passwd_errui, acct_errui, faultui, mylog
from client_sock import client_sock, socket
#from code_flag import sem_flags

from main_window import loginui


if __name__ == "__main__":
    
    sock = client_sock()

    app = QtGui.QApplication(sys.argv)
    login = loginui(sock)
    
    login.exec()
    sys.exit(app.exec_())
