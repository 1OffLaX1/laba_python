from math import isfinite
from models import Job, Status, Repository, Pricing


class GarageService:
    def __init__(self, repository: Repository, pricing: Pricing) -> None:
        self.repository = repository
        self.pricing = pricing

    def create(self, job: Job) -> None:
        self.repository.add(job)

    def set_pricing(self, pricing: Pricing) -> None:
        self.pricing = pricing

    def price(self, job_id: int) -> float:
        amount = self.pricing.calculate(self.repository.get(job_id).base_cost)
        if not isfinite(amount) or amount < 0:
            raise ValueError("Недопустимая итоговая стоимость")
        return amount

    def finish(self, job_id: int) -> None:
        job = self.repository.get(job_id)
        if job.status != Status.OPEN:
            raise ValueError("Заказ уже завершён")
        job.status = Status.DONE

    def delete(self, job_id: int) -> None:
        self.repository.delete(job_id)
