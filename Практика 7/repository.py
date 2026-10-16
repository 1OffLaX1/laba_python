from typing import Any, Protocol


class NotFoundError(Exception):
    pass


class Reader(Protocol):
    def get(self, item_id: int) -> Any: ...
    def get_all(self) -> list: ...


class Writer(Protocol):
    def add(self, item: Any) -> None: ...
    def delete(self, item_id: int) -> None: ...


class Repository(Reader, Writer, Protocol):
    pass


class MemoryRepository:
    def __init__(self) -> None:
        self.items: dict[int, Any] = {}

    def add(self, item: Any) -> None:
        if item.id in self.items:
            raise ValueError("ID уже существует")
        self.items[item.id] = item

    def get(self, item_id: int) -> Any:
        if item_id not in self.items:
            raise NotFoundError("Объект не найден")
        return self.items[item_id]

    def get_all(self) -> list:
        return list(self.items.values())

    def delete(self, item_id: int) -> None:
        self.get(item_id)
        del self.items[item_id]


class ListRepository:
    def __init__(self) -> None:
        self.items: list = []

    def add(self, item: Any) -> None:
        if any(existing.id == item.id for existing in self.items):
            raise ValueError("ID уже существует")
        self.items.append(item)

    def get(self, item_id: int) -> Any:
        for item in self.items:
            if item.id == item_id:
                return item
        raise NotFoundError("Объект не найден")

    def get_all(self) -> list:
        return self.items.copy()

    def delete(self, item_id: int) -> None:
        self.items.remove(self.get(item_id))
