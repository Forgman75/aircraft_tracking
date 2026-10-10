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
print(f"Найдено российских: {len(russian)}")  # 2

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
    nominatim_api: NominatimAPI,
    opensky_api: OpenSkyAPI,
    country_name: str
) -> list[Aircraft]:
    """Получает самолеты в воздушном пространстве страны."""

    print(
        f"\n[1/3] Запрос координат для "
        f"'{country_name}' через Nominatim..."
    )

    boundingbox = nominatim_api.get_data(country_name)

    print("   Координаты страны успешно получены.")

    print(
        "[2/3] Запрос данных о самолетах "
        "через OpenSky Network..."
    )
    print(
        "   (Это может занять несколько секунд, "
        "лимиты API строгие)"
    )

    states = opensky_api.get_data(boundingbox)

    aircraft_list = Aircraft.cast_to_object_list(states)

    print(
        f"   Найдено самолетов в воздушном пространстве: "
        f"{len(aircraft_list)}"
    )

    return aircraft_list


def save_aircraft(
    storage: JSONStorage,
    aircraft_list: list[Aircraft]
) -> None:
    """Сохраняет список самолетов в хранилище."""
    print(
        "[3/3] Сохранение полученных данных "
        "в локальное хранилище (JSON)..."
    )

    for aircraft in aircraft_list:
        storage.add_aircraft(aircraft)

    print("   Данные успешно сохранены!")


def show_menu():
    """Выводит главное меню."""
    print("\n" + "-" * 60)
    print("МЕНЮ:")
    print("1. Получить топ N самолетов по высоте полета")
    print("2. Получить самолеты по стране их регистрации")
    print("3. Показать все сохраненные самолеты")
    print("4. Выход")
    print("-" * 60)


def get_menu_choice() -> str:
    """Получает выбор пользователя."""
    return input("Выберите действие (1-4): ").strip()


def show_top_aircraft(storage: JSONStorage) -> None:
    """Показывает топ N самолетов по высоте."""
    try:
        n = int(
            input(
                "Введите количество самолетов "
                "для топа (N): "
            ).strip()
        )

        if n <= 0:
            print("Число должно быть больше нуля.")
            return

    except ValueError:
        print("Ошибка: Введите корректное целое число.")
        return

    all_aircraft = storage.get_aircraft()

    top_aircraft = sorted(
        all_aircraft,
        reverse=True
    )[:n]

    print(f"\n ТОП-{n} самолетов по высоте:")

    if not top_aircraft:
        print("   Нет данных для отображения.")
        return

    for number, aircraft in enumerate(top_aircraft, 1):
        print(f"   {number}. {aircraft}")


def show_aircraft_by_country(storage: JSONStorage) -> None:
    """Показывает самолеты по стране регистрации."""
    search_country = input(
        "Введите страну регистрации для поиска: "
    ).strip()

    if not search_country:
        print("Ошибка: Страна не может быть пустой.")
        return

    found_aircraft = storage.get_aircraft(
        country=search_country
    )

    print(
        f"\n Самолеты, зарегистрированные "
        f"в '{search_country}':"
    )

    if not found_aircraft:
        print("   Самолеты не найдены.")
        return

    for aircraft in found_aircraft:
        print(f"   - {aircraft}")


def show_all_aircraft(storage: JSONStorage) -> None:
    """Показывает все сохраненные самолеты."""
    all_aircraft = storage.get_aircraft()

    print(
        f"\n📋 Все сохраненные самолеты "
        f"({len(all_aircraft)} шт.):"
    )

    if not all_aircraft:
        print("   Хранилище пусто.")
        return

    for aircraft in all_aircraft:
        print(f"   - {aircraft}")


def handle_menu_choice(
    choice: str,
    storage: JSONStorage
) -> bool:
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
        print("Выход из программы. До свидания!")
        return False

    else:
        print(
            "Неверный выбор. "
            "Пожалуйста, введите число от 1 до 4."
        )

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
            nominatim_api,
            opensky_api,
            country_name
        )

        save_aircraft(
            storage,
            aircraft_list
        )

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
