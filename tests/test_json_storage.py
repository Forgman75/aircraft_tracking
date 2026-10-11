import pytest
from unittest.mock import patch, MagicMock
from src.json_storage import JSONStorage
from src.aircraft import Aircraft


@pytest.fixture
def storage(tmp_path):
    """Фикстура создает изолированное хранилище в временной
     директории pytest.
    """
    # Мы патчим Path, чтобы JSONStorage использовал tmp_path
    #  вместо реальной директории data
    with patch("pathlib.Path") as MockPath:
        # Заставляем __file__.parent.parent возвращать tmp_path
        mock_file_path = MagicMock()
        mock_file_path.parent.parent = tmp_path
        MockPath.return_value = mock_file_path

        storage = JSONStorage(filename="test_data.json")
        # Принудительно устанавливаем правильный путь для теста,
        #  чтобы обойти сложность патчинга __file__
        storage.file_path = tmp_path / "test_data.json"
        storage._save_data([])  # Инициализируем пустым
        return storage


def test_add_aircraft(storage):
    plane = Aircraft("Russia", "AFL101", 250.0, 10000.0)
    storage.add_aircraft(plane)

    data = storage._load_data()
    assert len(data) == 1
    assert data[0]["callsign"] == "AFL101"


def test_add_aircraft_prevents_duplicates(storage):
    plane1 = Aircraft("Russia", "AFL101", 250.0, 10000.0)
    plane2 = Aircraft("Russia", "AFL101", 300.0, 11000.0)  # Тот же callsign

    storage.add_aircraft(plane1)
    storage.add_aircraft(plane2)

    data = storage._load_data()
    assert len(data) == 1  # Второй не должен добавиться
    assert data[0]["speed"] == 250.0  # Сохранились данные первого


def test_get_aircraft_exact_and_substring_match(storage):
    storage.add_aircraft(
        Aircraft("Russian Federation", "AFL101", 250.0, 10000.0)
    )
    storage.add_aircraft(Aircraft("Germany", "DLH404", 230.0, 9000.0))

    # Точное совпадение (регистронезависимое)
    result1 = storage.get_aircraft(country="germany")
    assert len(result1) == 1
    assert result1[0].callsign == "DLH404"

    # Поиск по подстроке
    result2 = storage.get_aircraft(country="russ")
    assert len(result2) == 1
    assert result2[0].callsign == "AFL101"

    # Отсутствие совпадений
    result3 = storage.get_aircraft(country="France")
    assert len(result3) == 0


def test_delete_aircraft(storage):
    storage.add_aircraft(Aircraft("Russia", "AFL101", 250.0, 10000.0))
    storage.add_aircraft(Aircraft("Germany", "DLH404", 230.0, 9000.0))

    # Удаляем по позывному
    storage.delete_aircraft(
        callsign="afl101"
    )  # Проверка регистронезависимости

    data = storage._load_data()
    assert len(data) == 1
    assert data[0]["country"] == "Germany"


def test_load_data_handles_corrupted_json(storage, caplog):
    # Записываем невалидный JSON напрямую в файл
    with open(storage.file_path, "w", encoding="utf-8") as f:
        f.write("{ invalid json }")

    # Метод должен вернуть пустой список и залогировать ошибку
    result = storage._load_data()
    assert result == []


def test_save_aircraft_saves_all_aircraft(
    json_storage, aircraft_list
):
    """Все новые самолеты должны сохраниться."""
    added = json_storage.save_aircraft(aircraft_list)

    assert added == 2

    saved = json_storage.get_aircraft()

    assert len(saved) == 2
    assert {a.callsign for a in saved} == {"DLH123", "AFR456"}


def test_save_aircraft_skips_duplicates(
    json_storage, aircraft_list
):
    """Повторное добавление не должно создавать дубликаты."""
    first_added = json_storage.save_aircraft(aircraft_list)
    second_added = json_storage.save_aircraft(aircraft_list)

    assert first_added == 2
    assert second_added == 0
    assert len(json_storage.get_aircraft()) == 2


def test_save_aircraft_ignores_callsign_case(
    json_storage, aircraft_list
):
    """Позывные должны сравниваться без учета регистра."""
    json_storage.save_aircraft(aircraft_list)

    duplicate = Aircraft(
        country="Germany",
        callsign="dlh123",
        speed=250.0,
        altitude=11000.0,
    )

    added = json_storage.save_aircraft([duplicate])

    assert added == 0
    assert len(json_storage.get_aircraft()) == 2


def test_save_aircraft_empty_list(json_storage):
    """Пустой список не должен изменять содержимое файла."""
    added = json_storage.save_aircraft([])

    assert added == 0
    assert json_storage.get_aircraft() == []


def test_save_aircraft_preserves_existing_data(
    json_storage, aircraft_list
):
    """Новые самолеты должны добавляться к существующим."""
    json_storage.save_aircraft(aircraft_list)

    third_aircraft = Aircraft(
        country="Netherlands",
        callsign="KLM789",
        speed=220.0,
        altitude=9000.0,
    )

    added = json_storage.save_aircraft([third_aircraft])

    assert added == 1
    assert len(json_storage.get_aircraft()) == 3


