class Bank:
    def __init__(self, accounts=None):
        self.accounts = []
        for account in accounts or []:
            self.add(account)

    def add(self, account):
        if any(item.number == account.number for item in self.accounts):
            raise ValueError("Счёт с таким номером уже существует")
        self.accounts.append(account)

    def find(self, number):
        for account in self.accounts:
            if account.number == number.strip():
                return account
        raise ValueError("Счёт не найден")

    def deposit(self, number, amount):
        self.find(number).deposit(amount)

    def withdraw(self, number, amount):
        self.find(number).withdraw(amount)
