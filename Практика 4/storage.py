import csv
import json
from pathlib import Path
from models import Account


DATA_FILE = Path(__file__).parent / "data" / "accounts.json"
CSV_FILE = DATA_FILE.with_suffix(".csv")


def load_json(path=DATA_FILE):
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    if not isinstance(data, list):
        raise ValueError("В JSON должен находиться список счетов")
    try:
        return [Account.from_dict(item) for item in data]
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise ValueError("Некорректные данные счёта в JSON") from error


def save_json(accounts, path=DATA_FILE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Сначала записываем временный файл, затем заменяем основной.
    temporary = path.with_suffix(".tmp")
    with open(temporary, "w", encoding="utf-8") as file:
        json.dump([account.to_dict() for account in accounts], file,
                  ensure_ascii=False, indent=2, allow_nan=False)
    temporary.replace(path)


def export_csv(accounts, path=CSV_FILE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["number", "owner", "balance", "account_type"])
        writer.writeheader()
        writer.writerows(account.to_dict() for account in accounts)
