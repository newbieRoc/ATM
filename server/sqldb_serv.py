import pymysql
from code_flag import dbop_code
#from log import mylog

#serv_log = mylog(file = "servlog.log")
class sqldb_ops(object):

    def __init__(self, db_host, db_user, db_passwd, db_name, port = 3306):
        #connect()连接数据库
        self.dbconnect = pymysql.connect(db_host, db_user, db_passwd, db_name, port)
        #连接的对象的游标cursor属性操作数据库
        self.dbcursor =  self.dbconnect.cursor()

    def check_login(self, user_account, user_passwd):
        #查询账户是否再数据库中
        #查询账户的sql语句
        sql_stmt = "select account,passwd from accountinfo where account = %d" %(user_account)
        try:
            self.dbcursor.execute(sql_stmt)
            acct_data = self.dbcursor.fetchone()
            if acct_data is None:
                return dbop_code.ACCOUNT_NOT_EXIST
        except:
            return dbop_code.ERROR
        
        if acct_data[1] != user_passwd:
            return dbop_code.PASSWD_ERROR
        else:
            return dbop_code.SUCCESS
    
    #查询余额
    def check_balance(self, user_account):
        #查询余额的sql语句
        sql_stmt = "select balance from accountinfo where account = %d" %(user_account)
        
        self.dbcursor.execute(sql_stmt)
        balance_data = self.dbcursor.fetchone()
        return balance_data[0]

    def update_balance(self, user_account, user_balance):
        sql_stmt = "update accountinfo set balance = %f where account = %d" %(user_balance,user_account)
        try:
            self.dbcursor.execute(sql_stmt)
            self.dbconnect.commit()
            #serv_log.info_log("update useraccount:userbalance %d:%f" %(user_account, user_balance))
            return dbop_code.SUCCESS
        except:
            #self.dbconnect.rollback()
            return dbop_code.ERROR
    #减钱
    def decrease_money(self, user_account, money):
        user_balance = float(self.check_balance(user_account))
        new_balance = user_balance - float(money)

        #新余额小于0
        if new_balance < 0:
            return dbop_code.BALANCE_NOT_ENOUGH
        else:
            #更新账户余额
            return self.update_balance(user_account, new_balance)
    

    #加钱
    def increase_money(self, user_account, money):
        status = self.check_account(user_account)

        #账户不存在
        if status != dbop_code.SUCCESS:
            return status
        #账户存在更新余额
        else:
            user_balance = float(self.check_balance(user_account))
            new_balance = user_balance + float(money)
            #更新账户余额
            return self.update_balance(user_account, new_balance)
            

    #检查账户是否存在
    def check_account(self, user_account):
        
        sql_stmt = "select account from accountinfo where account = %d" %(user_account)
        try:
            self.dbcursor.execute(sql_stmt)
            acct_data = self.dbcursor.fetchone()
            if acct_data is None:
                return dbop_code.ACCOUNT_NOT_EXIST
            else:
                return dbop_code.SUCCESS
        except:
            return dbop_code.ERROR 
    