from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite


def positive(value: float) -> None:
    if not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("Число должно быть конечным и неотрицательным")


class Status(Enum):
    OPEN = "открыт"
    DONE = "завершён"


@dataclass
class Work(ABC):
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Название работы не должно быть пустым")

    @abstractmethod
    def cost(self) -> float:
        pass


@dataclass
class HourlyWork(Work):
    hours: float
    rate: float

    def __post_init__(self) -> None:
        super().__post_init__()
        positive(self.hours)
        positive(self.rate)
        positive(self.hours * self.rate)

    def cost(self) -> float:
        return round(self.hours * self.rate, 2)


@dataclass
class FixedWork(Work):
    price: float

    def __post_init__(self) -> None:
        super().__post_init__()
        positive(self.price)

    def cost(self) -> float:
        return round(self.price, 2)


@dataclass
class Car:
    id: int
    plate: str
    owner: str

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id <= 0:
            raise ValueError("ID должен быть положительным целым")
        if not self.plate.strip() or not self.owner.strip():
            raise ValueError("Заполните номер автомобиля и владельца")
        self.plate = self.plate.strip().upper()
        self.owner = self.owner.strip()


@dataclass
class RepairOrder:
    id: int
    car: Car
    works: list[Work] = field(default_factory=list)
    status: Status = Status.OPEN

    def total(self) -> float:
        return round(sum(work.cost() for work in self.works), 2)
