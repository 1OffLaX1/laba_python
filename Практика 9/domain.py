from dataclasses import dataclass, asdict, replace
from threading import RLock


class NotFoundError(Exception):
    pass


def integer(value: int, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"Требуется целое число не меньше {minimum}")


@dataclass
class Item:
    id: int
    name: str
    quantity: int
    minimum: int
    unit: str = "шт."

    def __post_init__(self) -> None:
        integer(self.id, 1)
        integer(self.quantity)
        integer(self.minimum)
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Название не должно быть пустым")
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise ValueError("Единица измерения не должна быть пустой")
        self.name = self.name.strip()
        self.unit = self.unit.strip()


class ItemRepository:
    def __init__(self) -> None:
        self.items: dict[int, Item] = {}
        self.next_id = 1

    def add(self, item: Item) -> None:
        if item.id in self.items:
            raise ValueError("ID уже существует")
        self.items[item.id] = item
        self.next_id = max(self.next_id, item.id + 1)

    def get(self, item_id: int) -> Item:
        integer(item_id, 1)
        if item_id not in self.items:
            raise NotFoundError("Товар не найден")
        return self.items[item_id]

    def get_all(self) -> list[Item]:
        return list(self.items.values())

    def update(self, item: Item) -> None:
        self.get(item.id)
        self.items[item.id] = item

    def delete(self, item_id: int) -> None:
        self.get(item_id)
        del self.items[item_id]


class WarehouseService:
    def __init__(self, repository: ItemRepository) -> None:
        self.repository = repository
        self.lock = RLock()

    def execute(self, command: str, data: dict) -> dict | list:
        # Защищена вся операция: проверка, изменение и создание ответа.
        with self.lock:
            return self._execute(command, data)

    def _execute(self, command: str, data: dict) -> dict | list:
        if not isinstance(command, str) or not isinstance(data, dict):
            raise ValueError("command должен быть строкой, data — объектом")
        if command == "list":
            return [asdict(item) for item in self.repository.get_all()]
        if command == "create":
            item = Item(self.repository.next_id, **data)
            self.repository.add(item)
            return asdict(item)
        if command == "get":
            return asdict(self.repository.get(data["id"]))
        if command == "update":
            item = self.repository.get(data["id"])
            changes = {key: value for key, value in data.items() if key != "id"}
            if not changes:
                raise ValueError("Не указаны изменения")
            updated = replace(item, **changes)
            self.repository.update(updated)
            return asdict(updated)
        if command == "delete":
            self.repository.delete(data["id"])
            return {"deleted": data["id"]}
        if command == "check_stock":
            items = ([self.repository.get(data["id"])] if "id" in data
                     else self.repository.get_all())
            return [{"id": item.id, "name": item.name, "quantity": item.quantity,
                     "minimum": item.minimum, "unit": item.unit,
                     "enough": item.quantity >= item.minimum,
                     "shortage": max(0, item.minimum - item.quantity)} for item in items]
        if command == "stats":
            items = self.repository.get_all()
            return {"items": len(items),
                    "low_stock": sum(item.quantity < item.minimum for item in items)}
        raise ValueError("Неизвестная команда")
