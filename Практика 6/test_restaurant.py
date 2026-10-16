import io
import unittest
from contextlib import redirect_stdout
from helpers import inspect_object, show_report, transaction
from models import Car, Part, Repair, Status
from services import Garage, NotFoundError


class GarageTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.silence = redirect_stdout(self.output)
        self.silence.__enter__()
        self.addCleanup(self.silence.__exit__, None, None, None)
        self.garage = Garage()
        self.car = Car(1, "Авто", "А111АА")
        self.part = Part(2, "Фильтр", 500)
        self.repair = Repair(3, "ТО", self.car, 1000)
        for item in [self.car, self.part, self.repair]:
            self.garage.add(item)

    def test_cost_and_parts(self):
        self.repair.change_status(Status.DIAGNOSING)
        self.repair.change_status(Status.REPAIRING)
        self.repair.add_part(self.part)
        self.repair.add_part(self.part)
        self.assertEqual(self.repair.total(), 2000)
        self.assertEqual(self.garage.popular_parts(), {"фильтр": 2})

    def test_status_guard(self):
        with self.assertRaises(ValueError):
            self.repair.add_part(self.part)
        with self.assertRaises(ValueError):
            self.repair.change_status(Status.DELIVERED)
        self.assertEqual(self.repair.parts, [])

    def test_all_states(self):
        for status in list(Status)[1:]:
            self.repair.change_status(status)
        with self.assertRaises(ValueError):
            self.repair.change_status(Status.ACCEPTED)

    def test_find_remove(self):
        self.assertIs(self.garage.find(2), self.part)
        self.garage.remove(2)
        with self.assertRaises(NotFoundError):
            self.garage.find(2)
        with self.assertRaises(ValueError):
            self.garage.remove(1)

    def test_transaction(self):
        with self.assertRaises(ValueError):
            with transaction(self.garage):
                self.garage.items.clear()
                raise ValueError("тест")
        self.assertEqual(len(self.garage.items), 3)
        restored = self.garage.get_repair(3)
        self.assertIs(restored.car, self.garage.find(1))

    def test_empty_statistics(self):
        self.assertEqual(Garage().statistics()["средняя стоимость"], 0)

    def test_introspection_protocol(self):
        self.assertEqual(inspect_object(self.car)["тип"], "Car")
        show_report(self.car)
        show_report(self.part)
        self.assertIn("Фильтр", self.output.getvalue())

    def test_decorators(self):
        self.assertEqual(self.garage.add.__name__, "add")
        self.assertEqual(self.repair.add_part.__name__, "add_part")
        self.garage.statistics()
        self.assertIn("[LOG]", self.output.getvalue())
        self.assertIn("[TIME]", self.output.getvalue())

    def test_invalid(self):
        with self.assertRaises(ValueError):
            Part(5, "A", -1)
        with self.assertRaises(ValueError):
            self.garage.add(self.car)
