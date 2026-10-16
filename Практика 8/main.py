from patterns import (JobFactory, StandardPricing, UrgentPricing, CorporatePricing,
                      CreateCommand, FinishCommand, DeleteCommand, CommandHistory)
from repository import MemoryRepository, NotFoundError
from services import GarageService


def main() -> None:
    service = GarageService(MemoryRepository(), StandardPricing())
    history = CommandHistory()
    tariffs = {"1": StandardPricing, "2": UrgentPricing, "3": CorporatePricing}
    while True:
        print("\n1. Создать заказ  2. Все заказы / стоимость  3. Тариф")
        print("4. Завершить  5. Удалить  6. История команд  0. Выход")
        choice = input("Выбор: ")
        try:
            if choice == "0":
                return
            if choice == "1":
                kind = input("1 — диагностика, 2 — ТО, 3 — ремонт: ")
                job = JobFactory.create(kind, int(input("ID: ")), input("Автомобиль: "),
                                        float(input("Базовая стоимость: ")))
                print(history.run(CreateCommand(service, job)))
            elif choice == "2":
                print("Тариф:", type(service.pricing).__name__)
                for job in service.repository.get_all():
                    print(f"№{job.id}, {job.car}, {job.kind}, {job.status.value}, "
                          f"{service.price(job.id):.2f} руб.")
            elif choice == "3":
                kind = input("1 — стандартный, 2 — срочный (+50%), 3 — корпоративный (-10%): ")
                if kind not in tariffs:
                    raise ValueError("Неизвестный тариф")
                service.set_pricing(tariffs[kind]())
                print("Тариф изменён")
            elif choice == "4":
                print(history.run(FinishCommand(service, int(input("ID: ")))))
            elif choice == "5":
                print(history.run(DeleteCommand(service, int(input("ID: ")))))
            elif choice == "6":
                for number, command in enumerate(history.commands, 1):
                    print(number, type(command).__name__)
            else:
                print("Неизвестный пункт меню")
        except (ValueError, NotFoundError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
