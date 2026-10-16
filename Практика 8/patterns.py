from dataclasses import dataclass, field
from models import Job, Diagnosis, Maintenance, Repair, Command
from services import GarageService


class JobFactory:
    types = {"1": Diagnosis, "2": Maintenance, "3": Repair}

    @classmethod
    def create(cls, kind: str, job_id: int, car: str, cost: float) -> Job:
        if kind not in cls.types:
            raise ValueError("Неизвестный тип работы")
        return cls.types[kind](job_id, car, cost)


# Учебные коэффициенты: в методичке их численные значения не заданы.
class StandardPricing:
    def calculate(self, amount: float) -> float:
        return round(amount, 2)


class UrgentPricing:
    def calculate(self, amount: float) -> float:
        return round(amount * 1.5, 2)


class CorporatePricing:
    def calculate(self, amount: float) -> float:
        return round(amount * 0.9, 2)


@dataclass
class CreateCommand:
    service: GarageService
    job: Job

    def execute(self) -> str:
        self.service.create(self.job)
        return f"Создан заказ №{self.job.id}: {self.job.kind}"


@dataclass
class FinishCommand:
    service: GarageService
    job_id: int

    def execute(self) -> str:
        self.service.finish(self.job_id)
        return f"Завершён заказ №{self.job_id}"


@dataclass
class DeleteCommand:
    service: GarageService
    job_id: int

    def execute(self) -> str:
        self.service.delete(self.job_id)
        return f"Удалён заказ №{self.job_id}"


@dataclass
class CommandHistory:
    commands: list[Command] = field(default_factory=list)

    def run(self, command: Command) -> str:
        result = command.execute()
        self.commands.append(command)
        return result
