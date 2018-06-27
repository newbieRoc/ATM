
class dbop_code():
    SUCCESS = 0
    ACCOUNT_NOT_EXIST = 1
    PASSWD_ERROR = 2
    BALANCE_NOT_ENOUGH = 3
    ERROR = 4

class sem_flags():
    ERROR = 0
    SUCCESS = 1
    NORMAL_CONNECTION= 2
    ACCOUNT_NOT_EXIST = 3
    BALANCE_NOT_ENOUGH = 4
    PASSWORD_ERROR = 5
    AMOUNT_ERROR = 6
    
class func_code():
    #UNKNOW = -1
    CHECK_BALANCE = 0
    DEPOSIT = 1
    WITHDROW = 2
    TRANSFER = 3
    QUIT = 4
    