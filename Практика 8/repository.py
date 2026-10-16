from models import Job


class NotFoundError(Exception):
    pass


class MemoryRepository:
    def __init__(self) -> None:
        self.jobs: dict[int, Job] = {}

    def add(self, job: Job) -> None:
        if job.id in self.jobs:
            raise ValueError("ID уже существует")
        self.jobs[job.id] = job

    def get(self, job_id: int) -> Job:
        if job_id not in self.jobs:
            raise NotFoundError("Заказ не найден")
        return self.jobs[job_id]

    def get_all(self) -> list[Job]:
        return list(self.jobs.values())

    def delete(self, job_id: int) -> None:
        self.get(job_id)
        del self.jobs[job_id]
