from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import ClassVar, Protocol


class Status(Enum):
    OPEN = "открыт"
    DONE = "завершён"


@dataclass
class Job:
    id: int
    car: str
    base_cost: float
    status: Status = Status.OPEN
    kind: ClassVar[str] = "работа"

    def __post_init__(self) -> None:
        if type(self.id) is not int or self.id <= 0:
            raise ValueError("ID должен быть положительным целым")
        if not isinstance(self.car, str) or not self.car.strip():
            raise ValueError("Укажите автомобиль")
        if not isinstance(self.base_cost, (int, float)) or not isfinite(self.base_cost) or self.base_cost < 0:
            raise ValueError("Стоимость должна быть конечной и неотрицательной")
        if not isinstance(self.status, Status):
            raise ValueError("Некорректный статус")
        self.car = self.car.strip()


class Diagnosis(Job):
    kind = "диагностика"


class Maintenance(Job):
    kind = "техническое обслуживание"


class Repair(Job):
    kind = "ремонт"


class Repository(Protocol):
    def add(self, job: Job) -> None: ...
    def get(self, job_id: int) -> Job: ...
    def get_all(self) -> list[Job]: ...
    def delete(self, job_id: int) -> None: ...


class Pricing(Protocol):
    def calculate(self, amount: float) -> float: ...


class Command(Protocol):
    def execute(self) -> str: ...
