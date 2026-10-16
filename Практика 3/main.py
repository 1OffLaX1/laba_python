from abc import ABC, abstractmethod


class Media(ABC):
    def __init__(self, title):
        self.title = title
        self.watched = False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Название не должно быть пустым")
        self._title = value.strip()

    def rename(self, title):
        self.title = title

    def mark_watched(self):
        self.watched = True

    @abstractmethod
    def get_volume(self):
        pass

    def get_info(self):
        state = "просмотрено" if self.watched else "не просмотрено"
        return f"{self.title}: {self.get_volume()}, {state}"

    def __str__(self):
        return self.get_info()


class Movie(Media):
    def __init__(self, title, duration):
        super().__init__(title)
        if not isinstance(duration, (int, float)) or not 0 < duration < float("inf"):
            raise ValueError("Длительность должна быть положительной")
        self.duration = duration

    def get_volume(self):
        return f"{self.duration:g} мин."


class Series(Media):
    def __init__(self, title, seasons):
        super().__init__(title)
        if type(seasons) is not int or seasons <= 0:
            raise ValueError("Количество сезонов должно быть положительным целым")
        self.seasons = seasons

    def get_volume(self):
        return f"{self.seasons} сез."


class MediaLibrary:
    def __init__(self):
        self.items = []

    def add(self, media):
        self.items.append(media)

    def find(self, title):
        return [item for item in self.items if title.casefold() in item.title.casefold()]

    def remove(self, media):
        self.items.remove(media)


def main():
    library = MediaLibrary()
    library.add(Movie("Учебный фильм", 90))
    library.add(Series("Учебный сериал", 3))
    library.add(Movie("Документальный фильм", 55))
    print("Фильмотека:")
    for item in library.items:
        print(item)
    movie = library.items[0]
    movie.rename("Основы Python")
    movie.mark_watched()
    print("После изменения:", movie)
    print("Поиск:", "; ".join(str(item) for item in library.find("Python")))
    try:
        movie.title = " "
    except ValueError as error:
        print("Проверка свойства:", error)
    library.remove(library.items[-1])
    print("После удаления объектов:", len(library.items))


if __name__ == "__main__":
    main()
