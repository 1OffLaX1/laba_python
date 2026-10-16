from math import isfinite


class Account:
    account_type = "счёт"

    def __init__(self, owner, number, balance):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Владелец не должен быть пустым")
        if not isinstance(number, str) or not number.strip():
            raise ValueError("Номер не должен быть пустым")
        balance = float(balance)
        if not isfinite(balance):
            raise ValueError("Баланс должен быть конечным числом")
        self.owner = owner.strip()
        self.number = number.strip()
        self.balance = balance

    def __str__(self):
        return f"№{self.number}: {self.owner}, {self.balance:.2f}, {self.account_type}"


class CurrentAccount(Account):
    account_type = "текущий"


class SavingsAccount(Account):
    account_type = "накопительный"


def filter_objects(objects, predicate):
    return list(filter(predicate, objects))


def transform_objects(objects, operation):
    return list(map(operation, objects))


def sort_objects(objects, key_function):
    return sorted(objects, key=key_function)


def accounts_by_type(accounts, account_type):
    for account in accounts:
        if account.account_type == account_type:
            yield account


def main():
    accounts = [CurrentAccount("Анна", "1", 1000),
                SavingsAccount("Иван", "2", 5000),
                CurrentAccount("Олег", "3", -200),
                SavingsAccount("Мария", "4", 0),
                CurrentAccount("Анна", "5", 700)]
    print("Все счета:")
    for account in accounts:
        print(account)
    print("Положительный баланс:")
    for account in filter_objects(accounts, lambda account: account.balance > 0):
        print(account)
    balances = transform_objects(accounts, lambda account: account.balance)
    print("Балансы через map:", balances)
    print("Сортировка по балансу:")
    for account in sort_objects(accounts, lambda account: account.balance):
        print(account)
    print(f"Общий баланс: {sum(balances):.2f}")
    print("Есть отрицательные счета:", any(account.balance < 0 for account in accounts))
    print("Уникальные владельцы:", sorted({account.owner for account in accounts}))
    print("Генератор текущих счетов, получение через next:")
    generator = accounts_by_type(accounts, "текущий")
    while True:
        try:
            print(next(generator))
        except StopIteration:
            print("Генератор исчерпан")
            break
    # Список вычислен сразу; генератор вычисляет баланс при next().
    ready = [account.balance for account in accounts]
    lazy = (account.balance for account in accounts)
    accounts[0].balance = 1100
    print("Ранее созданный список:", ready[0])
    print("Ленивое вычисление после изменения:", next(lazy))
    try:
        CurrentAccount("Анна", "6", "ошибка")
    except ValueError:
        print("Ошибка обработана: баланс должен быть числом")


if __name__ == "__main__":
    main()
