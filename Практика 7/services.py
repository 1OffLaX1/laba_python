from repository import Reader, Repository
from models import Car, RepairOrder, Work, Status, positive


class GarageService:
    def __init__(self, cars: Repository, orders: Repository) -> None:
        self.cars = cars
        self.orders = orders

    def register_car(self, car: Car) -> None:
        if any(item.plate == car.plate for item in self.cars.get_all()):
            raise ValueError("Автомобиль уже зарегистрирован")
        self.cars.add(car)

    def create_order(self, order_id: int, car_id: int) -> RepairOrder:
        if type(order_id) is not int or order_id <= 0:
            raise ValueError("ID должен быть положительным целым")
        order = RepairOrder(order_id, self.cars.get(car_id))
        self.orders.add(order)
        return order

    def add_work(self, order_id: int, work: Work) -> None:
        order = self.orders.get(order_id)
        if order.status != Status.OPEN:
            raise ValueError("Ремонт уже завершён")
        positive(work.cost())
        positive(order.total() + work.cost())
        order.works.append(work)

    def calculate(self, order_id: int) -> float:
        return self.orders.get(order_id).total()

    def finish(self, order_id: int) -> None:
        order = self.orders.get(order_id)
        if order.status != Status.OPEN:
            raise ValueError("Ремонт уже завершён")
        order.status = Status.DONE


class ReportService:
    # Для отчёта нужны только методы чтения, а не весь Repository.
    def __init__(self, orders: Reader) -> None:
        self.orders = orders

    def statistics(self) -> dict:
        orders = self.orders.get_all()
        return {"заказов": len(orders),
                "завершено": sum(x.status == Status.DONE for x in orders),
                "стоимость": round(sum(x.total() for x in orders), 2)}
