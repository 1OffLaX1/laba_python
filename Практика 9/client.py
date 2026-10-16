import argparse
import json
import socket
from protocol import Connection, ProtocolError


def read_command(choice: str) -> tuple[str, dict]:
    if choice == "1":
        return "list", {}
    if choice == "2":
        return "get", {"id": int(input("ID: "))}
    if choice in ("3", "4"):
        data = {}
        if choice == "4":
            data["id"] = int(input("ID: "))
        data.update(name=input("Название: "), quantity=int(input("Остаток: ")),
                    minimum=int(input("Минимальный остаток: ")), unit=input("Единица: "))
        return ("create" if choice == "3" else "update"), data
    if choice == "5":
        return "delete", {"id": int(input("ID: "))}
    if choice == "6":
        item_id = input("ID товара (Enter — все): ").strip()
        return "check_stock", {"id": int(item_id)} if item_id else {}
    if choice == "7":
        return "stats", {}
    raise ValueError("Неизвестный пункт меню")


def main() -> None:
    parser = argparse.ArgumentParser(description="Клиент склада")
    parser.add_argument("--port", type=int, default=5007)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Порт должен быть от 1 до 65535")
    try:
        with socket.create_connection(("127.0.0.1", args.port), timeout=5) as sock:
            connection = Connection(sock)
            try:
                while True:
                    print("\n1. Список  2. Получить  3. Создать  4. Изменить")
                    print("5. Удалить  6. Проверка остатков  7. Статистика  0. Выход")
                    choice = input("Выбор: ")
                    if choice == "0":
                        return
                    try:
                        command, data = read_command(choice)
                    except ValueError as error:
                        print("Ошибка ввода:", error)
                        continue
                    connection.send({"command": command, "data": data})
                    response = connection.receive()
                    if response is None:
                        print("Сервер закрыл соединение")
                        return
                    print(json.dumps(response, ensure_ascii=False, indent=2))
            finally:
                connection.close()
    except (OSError, ProtocolError) as error:
        print("Ошибка сети:", error)
    except (KeyboardInterrupt, EOFError):
        print("\nКлиент закрыт")


if __name__ == "__main__":
    main()
