from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from decorators import log_call, require_status


class Status(Enum):
    ACCEPTED = "принят"
    DIAGNOSING = "диагностируется"
    REPAIRING = "ремонтируется"
    READY = "готов"
    DELIVERED = "выдан"


def check_cost(value: float) -> None:
    if not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError("Стоимость должна быть конечной и неотрицательной")


@dataclass
class Entity:
    id: int
    name: str

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id <= 0:
            raise ValueError("ID должен быть положительным целым")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Название не должно быть пустым")
        self.name = self.name.strip()

    def get_report_data(self) -> str:
        return f"{type(self).__name__} №{self.id}: {self.name}"


@dataclass
class Car(Entity):
    plate: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.plate, str) or not self.plate.strip():
            raise ValueError("Номер автомобиля не должен быть пустым")
        self.plate = self.plate.strip().upper()

    def get_report_data(self) -> str:
        return f"Автомобиль №{self.id}: {self.name}, {self.plate}"


@dataclass
class Part(Entity):
    price: float

    def __post_init__(self) -> None:
        super().__post_init__()
        check_cost(self.price)

    def get_report_data(self) -> str:
        return f"Запчасть №{self.id}: {self.name}, {self.price:.2f} руб."


@dataclass
class Repair(Entity):
    car: Car
    labor_cost: float
    parts: list[Part] = field(default_factory=list)
    status: Status = Status.ACCEPTED

    def __post_init__(self) -> None:
        super().__post_init__()
        check_cost(self.labor_cost)
        if not isinstance(self.car, Car) or not isinstance(self.status, Status):
            raise ValueError("Некорректный автомобиль или статус")
        if not all(isinstance(part, Part) for part in self.parts):
            raise ValueError("Ожидается список запчастей")

    def change_status(self, status: Status) -> None:
        states = list(Status)
        current = states.index(self.status)
        if current + 1 >= len(states) or states[current + 1] != status:
            raise ValueError("Можно перейти только к следующему этапу ремонта")
        self.status = status

    @log_call
    @require_status(Status.REPAIRING)
    def add_part(self, part: Part) -> None:
        if not isinstance(part, Part):
            raise ValueError("Ожидается запчасть")
        self.parts.append(part)

    def total(self) -> float:
        return round(self.labor_cost + sum(part.price for part in self.parts), 2)

    def get_report_data(self) -> str:
        return (f"Ремонт №{self.id}: {self.car.plate}, {self.name}, "
                f"{self.status.value}, {self.total():.2f} руб.")
