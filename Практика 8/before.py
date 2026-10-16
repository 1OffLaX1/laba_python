"""Наивная версия: создание, расчёт и команды объединены в одном классе."""


class SimpleGarage:
    def __init__(self):
        self.jobs = {}

    def execute(self, command, job_id, kind="1", car="Авто", cost=0):
        if command == "create":
            if kind == "1":
                title = "диагностика"
            elif kind == "2":
                title = "техническое обслуживание"
            elif kind == "3":
                title = "ремонт"
            else:
                raise ValueError("Неизвестный тип")
            self.jobs[job_id] = dict(kind=title, car=car, cost=cost, done=False)
        elif command == "finish":
            self.jobs[job_id]["done"] = True
        elif command == "delete":
            del self.jobs[job_id]
        else:
            raise ValueError("Неизвестная команда")

    def price(self, job_id, tariff):
        amount = self.jobs[job_id]["cost"]
        if tariff == "standard":
            return round(amount, 2)
        if tariff == "urgent":
            return round(amount * 1.5, 2)
        if tariff == "corporate":
            return round(amount * 0.9, 2)
        raise ValueError("Неизвестный тариф")


if __name__ == "__main__":
    garage = SimpleGarage()
    garage.execute("create", 1, "3", "А111АА", 2000)
    for tariff in ["standard", "urgent", "corporate"]:
        print(tariff, garage.price(1, tariff))
    garage.execute("finish", 1)
    print("Завершён:", garage.jobs[1]["done"])
