import requests
from src.nominatim_api import NominatimAPI
from src.opensky_api import OpenSkyAPI
from src.aircraft import Aircraft
from src.json_storage import JSONStorage

nominatim = NominatimAPI()
opensky = OpenSkyAPI()

country = "Canada"

boundingbox = nominatim.get_data(country)
aircraftes_data = opensky.get_data(boundingbox)
aircraftes = Aircraft.cast_to_object_list(aircraftes_data)


print("Координаты страны:", boundingbox)
print("Данные о самолетах:", aircraftes)

# Создаем хранилище
storage = JSONStorage("planes.json")

# Создаем самолеты
plane1 = Aircraft("Russia", "AFL101", 250.0, 10000.0)
plane2 = Aircraft("Germany", "DLH404", 230.0, 9500.0)
plane3 = Aircraft("Russia", "AFL202", 270.0, 11000.0)

# Добавляем
storage.add_aircraft(plane1)
storage.add_aircraft(plane2)
storage.add_aircraft(plane3)

# Ищем все японские самолеты
russian = storage.get_aircraft(country="ger")
print(f"Найдено немецких: {len(russian)}")  # 2

# Ищем высокоскоростные
fast = storage.get_aircraft(speed=270.0)
print(f"Найдено быстрых: {len(fast)}")

# Удаляем все канадские
storage.delete_aircraft(country="Russia")

# Проверяем, что осталось
all_planes = storage.get_aircraft()
print(f"Всего осталось: {len(all_planes)}")


def print_welcome():
    """Выводит приветственное сообщение."""
    print("=" * 60)
    print(" ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
    print("=" * 60)


def get_country_name() -> str | None:
    """Запрашивает у пользователя название страны."""
    country_name = input(
        "\nВведите название страны для поиска самолетов "
        "(например, Germany, France, Russia): "
    ).strip()

    if not country_name:
        print("Ошибка: Название страны не может быть пустым.")
        return None

    return country_name


def load_aircraft_from_api(
    nominatim_api: NominatimAPI, opensky_api: OpenSkyAPI, country_name: str
) -> list[Aircraft]:
    """Получает самолеты в воздушном пространстве страны."""

    print(
        f"\n[1/3] Запрос координат для " f"'{country_name}' через Nominatim..."
    )

    boundingbox = nominatim_api.get_data(country_name)

    print("   Координаты страны успешно получены.")

    print("[2/3] Запрос данных о самолетах " "через OpenSky Network...")
    print("   (Это может занять несколько секунд, " "лимиты API строгие)")

    states = opensky_api.get_data(boundingbox)

    aircraft_list = Aircraft.cast_to_object_list(states)

    print(
        f"   Найдено самолетов в воздушном пространстве: "
        f"{len(aircraft_list)}"
    )

    return aircraft_list


def save_aircraft(storage: JSONStorage, aircraft_list: list[Aircraft]) -> None:
    """Сохраняет список самолетов в хранилище."""
    print(
        "[3/3] Сохранение полученных данных " "в локальное хранилище (JSON)..."
    )

    count = storage.save_aircraft(aircraft_list)

    print(f"   Успешно сохранено {count} самолетов!")


def show_menu():
    """Выводит главное меню."""
    print("\n" + "-" * 60)
    print("МЕНЮ:")
    print("1. Получить топ N самолетов по высоте полета")
    print("2. Получить самолеты по стране их регистрации")
    print("3. Показать все сохраненные самолеты")
    print("4. Фильтрация самолетов по диапазону высот")
    print("5. Фильтрация самолетов по диапазону скоростей")
    print("6. Удалить самолет по позывному")
    print("7. Выход")
    print("-" * 60)


def get_menu_choice() -> str:
    """Получает выбор пользователя."""
    return input("Выберите действие (1-7): ").strip()


def show_top_aircraft(storage: JSONStorage) -> None:
    """Показывает топ N самолетов по высоте."""
    try:
        n = int(
            input("Введите количество самолетов " "для топа (N): ").strip()
        )

        if n <= 0:
            print("Число должно быть больше нуля.")
            return

    except ValueError:
        print("Ошибка: Введите корректное целое число.")
        return

    all_aircraft = storage.get_aircraft()

    top_aircraft = sorted(all_aircraft, reverse=True)[:n]

    print(f"\n ТОП-{n} самолетов по высоте:")

    if not top_aircraft:
        print("   Нет данных для отображения.")
        return

    for number, aircraft in enumerate(top_aircraft, 1):
        print(f"   {number}. {aircraft}")


def show_aircraft_by_country(storage: JSONStorage) -> None:
    """Показывает самолеты по стране регистрации."""
    search_country = input("Введите страну регистрации для поиска: ").strip()

    if not search_country:
        print("Ошибка: Страна не может быть пустой.")
        return

    found_aircraft = storage.get_aircraft(country=search_country)

    print(f"\n Самолеты, зарегистрированные " f"в '{search_country}':")

    if not found_aircraft:
        print("   Самолеты не найдены.")
        return

    for aircraft in found_aircraft:
        print(f"   - {aircraft}")


def show_all_aircraft(storage: JSONStorage) -> None:
    """Показывает все сохраненные самолеты."""
    all_aircraft = storage.get_aircraft()

    print(f"\n Все сохраненные самолеты " f"({len(all_aircraft)} шт.):")

    if not all_aircraft:
        print("   Хранилище пусто.")
        return

    for aircraft in all_aircraft:
        print(f"   - {aircraft}")


def get_numeric_range(
    parameter_name: str, unit: str
) -> tuple[float, float] | None:
    """Запрашивает минимальное и максимальное значения диапазона."""
    try:
        minimum = float(
            input(
                f"Введите минимальное значение {parameter_name} ({unit}): "
            ).strip()
        )
        maximum = float(
            input(
                f"Введите максимальное значение {parameter_name} ({unit}): "
            ).strip()
        )

        if minimum < 0 or maximum < 0:
            print("Значения не могут быть отрицательными.")
            return None

        if minimum > maximum:
            print("Минимальное значение не может быть больше максимального.")
            return None

        return minimum, maximum

    except ValueError:
        print("Ошибка: введите корректные числовые значения.")
        return None


def show_aircraft_by_speed(storage: JSONStorage) -> None:
    """Показывает самолеты в заданном диапазоне скоростей."""
    speed_range = get_numeric_range("скорость", "м/с")

    if speed_range is None:
        return

    minimum, maximum = speed_range

    aircraft_list = [
        aircraft
        for aircraft in storage.get_aircraft()
        if minimum <= aircraft.speed <= maximum
    ]

    print(f"\n Самолеты со скоростью от {minimum:g} " f"до {maximum:g} м/с:")

    if not aircraft_list:
        print("   Самолеты в заданном диапазоне не найдены.")
        return

    # Сортируем по скорости, используя is_faster_than().
    aircraft_list.sort(key=lambda aircraft: aircraft.speed)

    for aircraft in aircraft_list:
        print(f"   - {aircraft}")


def show_aircraft_by_altitude(storage: JSONStorage) -> None:
    """Выводит самолеты в заданном диапазоне высот."""
    aircraft_list = storage.get_aircraft()

    if not aircraft_list:
        print("Список самолетов пуст.")
        return

    altitude_range = get_numeric_range("высоты", "м")

    if altitude_range is None:
        return

    minimum, maximum = altitude_range

    filtered_aircraft = [
        aircraft
        for aircraft in aircraft_list
        if minimum <= aircraft.altitude <= maximum
    ]

    if not filtered_aircraft:
        print("Самолеты в заданном диапазоне высот не найдены.")
        return

    # Благодаря __lt__ самолеты сортируются по высоте.
    filtered_aircraft.sort()

    for aircraft in filtered_aircraft:
        print(aircraft)


def delete_aircraft_by_callsign(storage: JSONStorage) -> None:
    """Удаляет самолет по позывному."""
    callsign = input("Введите позывной самолета для удаления: ").strip()

    if not callsign:
        print("Ошибка: позывной не может быть пустым.")
        return

    # Проверяем, существует ли самолет с таким позывным
    found_aircraft = storage.get_aircraft(callsign=callsign)

    # Учитываем, что get_aircraft может искать подстроку
    exact_match = [
        aircraft
        for aircraft in found_aircraft
        if aircraft.callsign.casefold() == callsign.casefold()
    ]

    if not exact_match:
        print(f"Самолет с позывным '{callsign}' не найден.")
        return

    storage.delete_aircraft(callsign=callsign)

    print(f"Самолет с позывным '{callsign}' успешно удален.")


def handle_menu_choice(choice: str, storage: JSONStorage) -> bool:
    """
    Обрабатывает выбор пользователя.

    Возвращает False, если нужно завершить программу.
    """
    if choice == "1":
        show_top_aircraft(storage)

    elif choice == "2":
        show_aircraft_by_country(storage)

    elif choice == "3":
        show_all_aircraft(storage)

    elif choice == "4":
        show_aircraft_by_altitude(storage)

    elif choice == "5":
        show_aircraft_by_speed(storage)

    elif choice == "6":
        delete_aircraft_by_callsign(storage)

    elif choice == "7":
        print("Выход из программы. До свидания!")
        return False

    else:
        print("Неверный выбор. " "Пожалуйста, введите число от 1 до 7.")

    return True


def run_interactive_cli():
    """Запускает консольный интерфейс программы."""

    nominatim_api = NominatimAPI()
    opensky_api = OpenSkyAPI()
    storage = JSONStorage()

    print_welcome()

    country_name = get_country_name()

    if country_name is None:
        return

    try:
        aircraft_list = load_aircraft_from_api(
            nominatim_api, opensky_api, country_name
        )

        save_aircraft(storage, aircraft_list)

    except requests.exceptions.RequestException as e:
        print(f"\n Ошибка сети: {e}")
        return

    except RuntimeError as e:
        print(f"\n Ошибка API: {e}")
        return

    except ValueError as e:
        print(f"\n Ошибка данных: {e}")
        return

    except Exception as e:
        print(f"\n Ошибка: {e}")
        return

    while True:
        show_menu()

        choice = get_menu_choice()

        if not handle_menu_choice(choice, storage):
            break


if __name__ == "__main__":
    run_interactive_cli()
