import inspect
from contextlib import contextmanager
from copy import deepcopy
from typing import Iterator, Protocol
from models import Entity
from services import Garage


class Reportable(Protocol):
    def get_report_data(self) -> str:
        ...


def show_report(item: Reportable) -> None:
    print(item.get_report_data())


def inspect_object(item: Entity) -> dict:
    return {"тип": type(item).__name__,
            "это Entity": isinstance(item, Entity),
            "есть name": hasattr(item, "name"),
            "название": getattr(item, "name", "нет"),
            "публичные атрибуты": [name for name in dir(item) if not name.startswith("_")],
            "сигнатура отчёта": str(inspect.signature(item.get_report_data))}


@contextmanager
def transaction(garage: Garage) -> Iterator[None]:
    backup = deepcopy(garage.items)
    print("[CONTEXT] Начало операции")
    try:
        yield
    except Exception:
        garage.items = backup
        print("[CONTEXT] Изменения отменены")
        raise
    else:
        print("[CONTEXT] Изменения приняты")
    finally:
        print("[CONTEXT] Завершение операции")
