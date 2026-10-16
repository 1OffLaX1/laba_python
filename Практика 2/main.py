def find_client(orders, client):
    return [order for order in orders
            if order["client"].casefold() == client.strip().casefold()]


def filter_status(orders, status):
    return [order for order in orders
            if order["status"].casefold() == status.strip().casefold()]


def statistics(orders):
    total = sum(order["cost"] for order in orders)
    return len(orders), total, total / len(orders) if orders else 0


def show(orders):
    if not orders:
        print("Заказов нет")
    for order in orders:
        print(f'№{order["number"]}: {order["client"]}, '
              f'{order["cost"]:.2f} руб., {order["status"]}')


def read_orders():
    count = int(input("Количество заказов: "))
    if count < 0:
        raise ValueError("Количество не может быть отрицательным")
    orders = []
    numbers = set()
    for _ in range(count):
        number = input("Номер заказа: ").strip()
        client = input("Клиент: ").strip()
        cost = float(input("Стоимость: ").replace(",", "."))
        status = input("Статус: ").strip().lower()
        if not number or not client or not status:
            raise ValueError("Текстовые поля не должны быть пустыми")
        if number in numbers:
            raise ValueError("Номер заказа уже существует")
        if not 0 <= cost < float("inf"):
            raise ValueError("Стоимость должна быть конечной и неотрицательной")
        orders.append(dict(number=number, client=client, cost=cost, status=status))
        numbers.add(number)
    return orders


def main():
    try:
        orders = read_orders()
    except ValueError as error:
        print("Ошибка ввода:", error)
        return
    print("Все заказы:")
    show(orders)
    print("Поиск по клиенту:")
    show(find_client(orders, input("Имя клиента: ")))
    print("Фильтрация по статусу:")
    show(filter_status(orders, input("Нужный статус: ")))
    print("По возрастанию стоимости:")
    show(sorted(orders, key=lambda order: order["cost"]))
    count, total, mean = statistics(orders)
    print(f"Количество заказов: {count}")
    print(f"Общая сумма: {total:.2f} руб.")
    print(f"Средний чек: {mean:.2f} руб.")
    statuses = {order["status"] for order in orders}
    print("Уникальные статусы:", ", ".join(sorted(statuses)) or "нет")


if __name__ == "__main__":
    main()
