from collections import Counter
from decorators import log_call, timed
from models import Entity, Car, Part, Repair, Status


class NotFoundError(Exception):
    pass


class Garage:
    def __init__(self) -> None:
        self.items: list[Entity] = []

    @log_call
    def add(self, item: Entity) -> None:
        if any(existing.id == item.id for existing in self.items):
            raise ValueError("ID уже существует")
        if isinstance(item, Car) and any(
            isinstance(other, Car) and other.plate == item.plate for other in self.items
        ):
            raise ValueError("Автомобиль с таким номером уже зарегистрирован")
        if isinstance(item, Repair) and item.car not in self.items:
            raise ValueError("Сначала зарегистрируйте автомобиль")
        self.items.append(item)

    def find(self, item_id: int) -> Entity:
        for item in self.items:
            if item.id == item_id:
                return item
        raise NotFoundError("Объект не найден")

    def remove(self, item_id: int) -> None:
        item = self.find(item_id)
        for repair in self.repairs():
            if repair.car is item or any(part is item for part in repair.parts):
                raise ValueError("Объект используется в ремонте")
        self.items.remove(item)

    def repairs(self) -> list[Repair]:
        return [item for item in self.items if isinstance(item, Repair)]

    def get_repair(self, item_id: int) -> Repair:
        item = self.find(item_id)
        if not isinstance(item, Repair):
            raise ValueError("Выбранный объект не является ремонтом")
        return item

    def popular_parts(self) -> dict[str, int]:
        counts = Counter(part.name.casefold() for repair in self.repairs() for part in repair.parts)
        return dict(counts.most_common())

    @timed
    def statistics(self) -> dict:
        repairs = self.repairs()
        total = sum(repair.total() for repair in repairs)
        return {"автомобилей": sum(isinstance(x, Car) for x in self.items),
                "запчастей в каталоге": sum(isinstance(x, Part) for x in self.items),
                "ремонтов": len(repairs),
                "готовых": sum(x.status == Status.READY for x in repairs),
                "общая стоимость": round(total, 2),
                "средняя стоимость": round(total / len(repairs), 2) if repairs else 0}
