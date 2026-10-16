"""Рабочий учебный пример ДО рефакторинга. Намеренные нарушения SOLID."""


class Storage:
    def __init__(self):
        self.cars = {}
        self.orders = {}


class BadGarage:
    def __init__(self):
        self.storage = Storage()  # DIP: жёсткая зависимость.

    def register_car(self, car_id, plate, owner):
        self.storage.cars[car_id] = (plate, owner)

    def create_order(self, order_id, car_id):
        self.storage.orders[order_id] = dict(car=self.storage.cars[car_id], works=[], done=False)

    def add_work(self, order_id, kind, value, rate=1):
        self.storage.orders[order_id]["works"].append((kind, value, rate))

    def total(self, order_id):
        total = 0
        for kind, value, rate in self.storage.orders[order_id]["works"]:
            # OCP: для нового вида работы придётся менять этот метод.
            if kind == "hourly":
                total += value * rate
            elif kind == "fixed":
                total += value
            else:
                raise ValueError("Неизвестная работа")
        return total

    def finish(self, order_id):
        self.storage.orders[order_id]["done"] = True
        # SRP: здесь одновременно состояние, расчёт и вывод отчёта.
        print("Ремонт завершён. Стоимость:", self.total(order_id))


class AllInOneWork:
    # ISP: все работы обязаны одновременно считать, хранить и уведомлять.
    def cost(self):
        return 0

    def save(self):
        return "Сохранено"

    def notify(self):
        return "Уведомление отправлено"


class LocalInspection(AllInOneWork):
    def notify(self):
        # LSP: подтип не выполняет обещание родительского класса.
        raise NotImplementedError("У локальной диагностики нет уведомлений")


def main():
    garage = BadGarage()
    garage.register_car(1, "А111АА", "Анна")
    garage.create_order(1, 1)
    garage.add_work(1, "hourly", 2, 1000)
    garage.add_work(1, "fixed", 500)
    garage.finish(1)
    try:
        LocalInspection().notify()
    except NotImplementedError as error:
        print("Демонстрация нарушения LSP:", error)


if __name__ == "__main__":
    main()
