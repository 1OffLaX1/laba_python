from helpers import Reportable, inspect_object, show_report, transaction
from models import Car, Part, Repair, Status
from services import Garage, NotFoundError


def add_object(garage: Garage) -> None:
    kind = input("Тип: 1 — автомобиль, 2 — запчасть, 3 — ремонт: ")
    item_id = int(input("ID: "))
    name = input("Название: ")
    if kind == "1":
        item = Car(item_id, name, input("Номер автомобиля: "))
    elif kind == "2":
        item = Part(item_id, name, float(input("Цена: ")))
    elif kind == "3":
        car = garage.find(int(input("ID автомобиля: ")))
        item = Repair(item_id, name, car, float(input("Стоимость работ: ")))
    else:
        raise ValueError("Неизвестный тип")
    garage.add(item)
    show_report(item)


def demonstration() -> None:
    garage = Garage()
    car = Car(1, "Учебный автомобиль", "А111АА")
    part = Part(2, "Фильтр", 500)
    repair = Repair(3, "Замена фильтра", car, 1000)
    for item in [car, part, repair]:
        garage.add(item)
    with transaction(garage):
        repair.change_status(Status.DIAGNOSING)
        repair.change_status(Status.REPAIRING)
        repair.add_part(part)
    report: Reportable = repair
    show_report(report)
    print(garage.statistics())
    print("Частота замены:", garage.popular_parts())
    print(inspect_object(part))


def main() -> None:
    garage = Garage()
    while True:
        print("\n1. Добавить  2. Удалить  3. Найти  4. Все объекты  5. Статус")
        print("6. Добавить запчасть в ремонт  7. Статистика  8. Интроспекция")
        print("9. Демонстрация  10. Контекст / откат  11. Частота замены  0. Выход")
        choice = input("Выбор: ")
        try:
            if choice == "0":
                return
            if choice == "1":
                add_object(garage)
            elif choice == "2":
                garage.remove(int(input("ID: ")))
                print("Удалено")
            elif choice == "3":
                show_report(garage.find(int(input("ID: "))))
            elif choice == "4":
                for item in garage.items:
                    show_report(item)
                if not garage.items:
                    print("Объектов нет")
            elif choice == "5":
                repair = garage.get_repair(int(input("ID ремонта: ")))
                for number, status in enumerate(Status, 1):
                    print(number, status.value)
                number = int(input("Новый статус: "))
                if not 1 <= number <= len(Status):
                    raise ValueError("Неизвестный статус")
                repair.change_status(list(Status)[number - 1])
                show_report(repair)
            elif choice == "6":
                repair = garage.get_repair(int(input("ID ремонта: ")))
                part = garage.find(int(input("ID запчасти: ")))
                repair.add_part(part)
                show_report(repair)
            elif choice == "7":
                print(garage.statistics())
            elif choice == "8":
                print(inspect_object(garage.find(int(input("ID: ")))))
            elif choice == "9":
                demonstration()
            elif choice == "10":
                with transaction(garage):
                    garage.items.clear()
                    raise ValueError("Учебная ошибка: проверяем восстановление коллекции")
            elif choice == "11":
                print("Частота замены деталей:", garage.popular_parts())
            else:
                print("Неизвестный пункт меню")
        except (ValueError, NotFoundError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
