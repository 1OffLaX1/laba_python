import unittest
from repository import NotFoundError
from models import Car, Work, HourlyWork, FixedWork, Status
from repository import MemoryRepository, ListRepository
from services import GarageService, ReportService
from before import BadGarage


class SolidTests(unittest.TestCase):
    def setUp(self):
        self.service = GarageService(MemoryRepository(), MemoryRepository())
        self.service.register_car(Car(1, "А111АА", "Анна"))
        self.service.create_order(1, 1)

    def test_create(self):
        self.assertEqual(self.service.orders.get(1).car.owner, "Анна")

    def test_cost(self):
        self.service.add_work(1, HourlyWork("Ремонт", 2, 1000))
        self.service.add_work(1, FixedWork("Диагностика", 500))
        self.assertEqual(self.service.calculate(1), 2500)

    def test_finish(self):
        self.service.finish(1)
        self.assertEqual(self.service.orders.get(1).status, Status.DONE)
        with self.assertRaises(ValueError):
            self.service.add_work(1, FixedWork("A", 10))
        with self.assertRaises(ValueError):
            self.service.finish(1)

    def test_repository_substitution(self):
        for repo_type in [MemoryRepository, ListRepository]:
            service = GarageService(repo_type(), repo_type())
            service.register_car(Car(1, "A", "B"))
            service.create_order(1, 1)
            service.add_work(1, FixedWork("X", 20))
            self.assertEqual(service.calculate(1), 20)
            service.orders.delete(1)
            with self.assertRaises(NotFoundError):
                service.calculate(1)

    def test_extension_without_service_changes(self):
        class FreeWork(Work):
            def cost(self):
                return 0
        self.service.add_work(1, FreeWork("Бесплатная проверка"))
        self.assertEqual(self.service.calculate(1), 0)

    def test_reader_only(self):
        class ReadOnlyOrders:
            def get(self, item_id):
                raise NotFoundError()
            def get_all(self):
                return []
        self.assertEqual(ReportService(ReadOnlyOrders()).statistics()["заказов"], 0)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            HourlyWork("A", -1, 100)
        with self.assertRaises(NotFoundError):
            self.service.create_order(2, 999)
        with self.assertRaises(ValueError):
            self.service.create_order(1, 1)

    def test_same_business_result(self):
        before = BadGarage()
        before.register_car(1, "A", "B")
        before.create_order(1, 1)
        before.add_work(1, "hourly", 2, 1000)
        before.add_work(1, "fixed", 500)
        self.service.add_work(1, HourlyWork("A", 2, 1000))
        self.service.add_work(1, FixedWork("B", 500))
        self.assertEqual(before.total(1), self.service.calculate(1))
