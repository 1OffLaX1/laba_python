from exceptions import InsufficientFundsError
from models import Account
from services import Bank
from storage import load_json, save_json, export_csv


def main():
    try:
        bank = Bank(load_json())
    except (OSError, ValueError) as error:
        print("Не удалось загрузить данные:", error)
        print("Исправьте data/accounts.json. Файл не был изменён.")
        return
    print("Загружено счетов:", len(bank.accounts))
    while True:
        print("\n1. Открыть счёт  2. Все счета  3. Пополнить  4. Снять")
        print("5. Найти / баланс  6. Сохранить  7. Загрузить  8. CSV  0. Выход")
        choice = input("Выбор: ").strip()
        try:
            if choice == "1":
                bank.add(Account(input("Номер: "), input("Владелец: "),
                                 input("Баланс: ").replace(",", "."), input("Тип счёта: ")))
                print("Счёт открыт")
            elif choice == "2":
                for account in bank.accounts:
                    print(account)
                if not bank.accounts:
                    print("Счетов нет")
            elif choice in ("3", "4"):
                number = input("Номер: ")
                amount = input("Сумма: ").replace(",", ".")
                if choice == "3":
                    bank.deposit(number, amount)
                else:
                    bank.withdraw(number, amount)
                print(bank.find(number))
            elif choice == "5":
                print(bank.find(input("Номер: ")))
            elif choice in ("6", "0"):
                save_json(bank.accounts)
                print("Сохранено в data/accounts.json")
                if choice == "0":
                    return
            elif choice == "7":
                bank = Bank(load_json())
                print("Загружено счетов:", len(bank.accounts))
            elif choice == "8":
                export_csv(bank.accounts)
                print("Экспортировано в data/accounts.csv")
            else:
                print("Неизвестный пункт меню")
        except (ValueError, OSError, InsufficientFundsError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
