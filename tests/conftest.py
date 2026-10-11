import pytest
from src.csv_storage import CSVStorage
from src.aircraft import Aircraft
from src.json_storage import JSONStorage


@pytest.fixture
def json_storage(tmp_path):
    """Создает JSON-хранилище во временной директории."""
    storage = JSONStorage.__new__(JSONStorage)
    storage.file_path = tmp_path / "aircraft_data.json"
    storage._save_data([])
    return storage


@pytest.fixture
def csv_storage(tmp_path):
    """Создает CSV-хранилище во временной директории."""
    storage = CSVStorage.__new__(CSVStorage)
    storage.file_path = tmp_path / "aircraft_data.csv"
    return storage


@pytest.fixture
def aircraft_list():
    """Подготавливает тестовые объекты самолетов."""
    return [
        Aircraft(
            country="Germany",
            callsign="DLH123",
            speed=230.5,
            altitude=10500.0,
        ),
        Aircraft(
            country="France",
            callsign="AFR456",
            speed=210.0,
            altitude=9800.0,
        ),
    ]