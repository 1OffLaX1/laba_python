def average(results):
    return sum(results) / len(results) if results else 0


def winners(results):
    # При равном времени место одинаковое: например, 1, 1, 3, 4.
    ordered = sorted(enumerate(results, 1), key=lambda item: item[1])
    prize_winners = []
    place = 0
    previous = None
    for position, (number, result) in enumerate(ordered, 1):
        if result != previous:
            place = position
        if place <= 3:
            prize_winners.append((place, number, result))
        previous = result
    return prize_winners


def main():
    try:
        count = int(input("Количество спортсменов: "))
        if count <= 0:
            raise ValueError("Количество должно быть положительным")
        results = []
        for number in range(1, count + 1):
            result = float(input(f"Время спортсмена №{number}, с: ").replace(",", "."))
            if not 0 < result < float("inf"):
                raise ValueError("Время должно быть конечным положительным числом")
            results.append(result)
    except ValueError as error:
        print("Ошибка ввода:", error)
        return

    mean = average(results)
    better = 0
    for result in results:
        if result < mean:
            better += 1
    print(f"Лучший результат: {min(results):.2f} с")
    print(f"Худший результат: {max(results):.2f} с")
    print(f"Средний результат: {mean:.2f} с")
    print("Лучше среднего:", better)
    print("Призёры:")
    for place, number, result in winners(results):
        print(f"{place}-е место: спортсмен №{number}, {result:.2f} с")


if __name__ == "__main__":
    main()
