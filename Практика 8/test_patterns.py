from patterns import (JobFactory, StandardPricing, UrgentPricing, CorporatePricing,
                      CreateCommand, FinishCommand, DeleteCommand, CommandHistory)
import unittest
from before import SimpleGarage
from models import Diagnosis, Maintenance, Repair, Status
from repository import MemoryRepository, NotFoundError
from services import GarageService


class PatternTests(unittest.TestCase):
    def setUp(self):
        self.repo = MemoryRepository()
        self.service = GarageService(self.repo, StandardPricing())

    def test_factory(self):
        for kind, cls in [("1", Diagnosis), ("2", Maintenance), ("3", Repair)]:
            self.assertIsInstance(JobFactory.create(kind, 1, "Авто", 100), cls)
        with self.assertRaises(ValueError):
            JobFactory.create("9", 1, "Авто", 100)

    def test_repository(self):
        job = Repair(1, "Авто", 100)
        self.repo.add(job)
        self.assertIs(self.repo.get(1), job)
        self.assertEqual(len(self.repo.get_all()), 1)
        self.repo.delete(1)
        with self.assertRaises(NotFoundError):
            self.repo.get(1)

    def test_strategies(self):
        self.service.create(Repair(1, "Авто", 2000))
        for pricing, expected in [(StandardPricing(), 2000), (UrgentPricing(), 3000),
                                  (CorporatePricing(), 1800)]:
            self.service.set_pricing(pricing)
            self.assertEqual(self.service.price(1), expected)

    def test_commands_and_history(self):
        history = CommandHistory()
        history.run(CreateCommand(self.service, Repair(1, "Авто", 100)))
        history.run(FinishCommand(self.service, 1))
        self.assertEqual(self.repo.get(1).status, Status.DONE)
        with self.assertRaises(ValueError):
            history.run(FinishCommand(self.service, 1))
        self.assertEqual(len(history.commands), 2)
        history.run(DeleteCommand(self.service, 1))
        self.assertEqual(self.repo.get_all(), [])

    def test_invalid(self):
        for cost in [-1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                Repair(1, "Авто", cost)
        with self.assertRaises(ValueError):
            Repair(1, "", 100)

    def test_duplicate(self):
        self.service.create(Repair(1, "Авто", 100))
        with self.assertRaises(ValueError):
            self.service.create(Repair(1, "Другое авто", 200))

    def test_before_and_after(self):
        before = SimpleGarage()
        before.execute("create", 1, "3", "Авто", 2000)
        self.service.create(Repair(1, "Авто", 2000))
        for name, pricing in [("standard", StandardPricing()), ("urgent", UrgentPricing()),
                              ("corporate", CorporatePricing())]:
            self.service.set_pricing(pricing)
            self.assertEqual(before.price(1, name), self.service.price(1))
