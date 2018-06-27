

class printdoc(object):
    def __init__(self):
        self.current_account = ""
        self.current_balance = ""
        self.current_deposit = ""
        self.current_withdraw = ""
        self.current_2account = ""
        
    def account(self,account):
        self.current_account = "账户：" + account +"\n"
    def check(self, balance):
        self.current_balance = "余额：" + balance + "\n"
    def deposit(self, amount):
        self.current_deposit = "存款金额：" + amount + "\n"
    def withdraw(self, amount):
        self.current_withdraw = "取款金额：" + amount + "\n"
    def transfer(self, to_account, amount):
        self.current_2account = "转账账户：" + to_account + " 转账金额：" + amount + "\n"

    def print(self):
        return self.current_account + self.current_balance +self.current_deposit +self.current_withdraw+self.current_2account
    
