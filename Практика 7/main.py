from models import Car, HourlyWork, FixedWork
from repository import MemoryRepository, ListRepository, NotFoundError
from services import GarageService, ReportService


def demonstration() -> None:
    for repository_type in (MemoryRepository, ListRepository):
        service = GarageService(repository_type(), repository_type())
        service.register_car(Car(1, "А111АА", "Анна"))
        service.create_order(1, 1)
        service.add_work(1, HourlyWork("Ремонт", 2, 1000))
        service.add_work(1, FixedWork("Диагностика", 500))
        service.finish(1)
        print(repository_type.__name__, ReportService(service.orders).statistics())


def run(service: GarageService) -> None:
    while True:
        print("\n1. Автомобиль  2. Заказ-наряд  3. Добавить работу")
        print("4. Стоимость  5. Завершить  6. Все заказы  7. Отчёт  8. Демо SOLID  0. Выход")
        choice = input("Выбор: ")
        try:
            if choice == "0":
                return
            if choice == "1":
                service.register_car(Car(int(input("ID: ")), input("Номер: "), input("Владелец: ")))
                print("Автомобиль зарегистрирован")
            elif choice == "2":
                order = service.create_order(int(input("ID заказа: ")), int(input("ID автомобиля: ")))
                print("Создан заказ:", order.id)
            elif choice == "3":
                order_id = int(input("ID заказа: "))
                kind = input("1 — почасовая, 2 — фиксированная: ")
                name = input("Название работы: ")
                if kind == "1":
                    work = HourlyWork(name, float(input("Часы: ")), float(input("Цена часа: ")))
                elif kind == "2":
                    work = FixedWork(name, float(input("Цена: ")))
                else:
                    raise ValueError("Неизвестный тип работы")
                service.add_work(order_id, work)
                print("Работа добавлена")
            elif choice == "4":
                print(f'Стоимость: {service.calculate(int(input("ID заказа: "))):.2f} руб.')
            elif choice == "5":
                service.finish(int(input("ID заказа: ")))
                print("Ремонт завершён")
            elif choice == "6":
                for order in service.orders.get_all():
                    print(f"№{order.id}, {order.car.plate}, {order.status.value}, {order.total():.2f}")
            elif choice == "7":
                print(ReportService(service.orders).statistics())
            elif choice == "8":
                demonstration()
            else:
                print("Неизвестный пункт меню")
        except (ValueError, NotFoundError) as error:
            print("Ошибка:", error)


def main() -> None:
    run(GarageService(MemoryRepository(), MemoryRepository()))


if __name__ == "__main__":
    main()
