from exceptions import InsufficientFundsError


def money(value):
    if isinstance(value, bool):
        raise ValueError("Некорректная сумма")
    value = float(value)
    if not 0 <= value < float("inf"):
        raise ValueError("Сумма должна быть конечной и неотрицательной")
    return round(value, 2)


class Account:
    def __init__(self, number, owner, balance, account_type):
        for value in (number, owner, account_type):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Номер, владелец и тип счёта не должны быть пустыми")
        self.number = number.strip()
        self.owner = owner.strip()
        self.balance = money(balance)
        self.account_type = account_type.strip()

    def deposit(self, amount):
        amount = money(amount)
        if amount == 0:
            raise ValueError("Сумма пополнения должна быть не меньше 0.01")
        self.balance = money(self.balance + amount)

    def withdraw(self, amount):
        amount = money(amount)
        if amount == 0:
            raise ValueError("Сумма снятия должна быть не меньше 0.01")
        if amount > self.balance:
            raise InsufficientFundsError("Недостаточно средств")
        self.balance = round(self.balance - amount, 2)

    def to_dict(self):
        return dict(number=self.number, owner=self.owner,
                    balance=self.balance, account_type=self.account_type)

    @classmethod
    def from_dict(cls, data):
        return cls(data["number"], data["owner"], data["balance"], data["account_type"])

    def __str__(self):
        return f"№{self.number}: {self.owner}, {self.balance:.2f} руб., {self.account_type}"
