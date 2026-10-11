import pytest
import csv
from src.aircraft import Aircraft


def test_save_aircraft_creates_csv(
    csv_storage, aircraft_list
):
    """Экспорт создает файл с заголовками и данными."""
    csv_storage.save_aircraft(aircraft_list)

    assert csv_storage.file_path.exists()

    with csv_storage.file_path.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == [
        "country", "callsign", "speed", "altitude"
    ]
    assert len(rows) == 2
    assert rows[0]["callsign"] == "DLH123"
    assert rows[0]["country"] == "Germany"
    assert float(rows[0]["speed"]) == pytest.approx(230.5)
    assert float(rows[0]["altitude"]) == pytest.approx(10500.0)


def test_save_aircraft_empty_list(csv_storage):
    """При экспорте пустого списка записывается заголовок."""
    csv_storage.save_aircraft([])

    with csv_storage.file_path.open(
        encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        assert reader.fieldnames == [
            "country", "callsign", "speed", "altitude"
        ]
        assert rows == []


def test_save_aircraft_overwrites_previous_data(
    csv_storage, aircraft_list
):
    """Повторный экспорт заменяет старое содержимое файла."""
    csv_storage.save_aircraft(aircraft_list[:1])
    csv_storage.save_aircraft(aircraft_list[1:])

    loaded = csv_storage.load_aircraft()

    assert len(loaded) == 1
    assert loaded[0].callsign == "AFR456"




def test_load_aircraft_restores_objects(
    csv_storage, aircraft_list
):
    """Импорт восстанавливает объекты Aircraft."""
    csv_storage.save_aircraft(aircraft_list)

    loaded = csv_storage.load_aircraft()

    assert len(loaded) == 2
    assert all(isinstance(a, Aircraft) for a in loaded)

    assert loaded[0].country == "Germany"
    assert loaded[0].callsign == "DLH123"
    assert loaded[0].speed == pytest.approx(230.5)
    assert loaded[0].altitude == pytest.approx(10500.0)


def test_load_aircraft_skips_invalid_rows(csv_storage):
    """Некорректные строки пропускаются."""
    with csv_storage.file_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "country", "callsign", "speed", "altitude"
            ],
        )
        writer.writeheader()
        writer.writerow({
            "country": "Germany",
            "callsign": "DLH123",
            "speed": "230.5",
            "altitude": "10500",
        })
        writer.writerow({
            "country": "France",
            "callsign": "AFR456",
            "speed": "invalid",
            "altitude": "9800",
        })
        writer.writerow({
            "country": "Italy",
            "callsign": "",
            "speed": "200",
            "altitude": "9000",
        })

    loaded = csv_storage.load_aircraft()

    assert len(loaded) == 1
    assert loaded[0].callsign == "DLH123"


def test_load_aircraft_missing_file(csv_storage):
    """При отсутствии файла возникает FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        csv_storage.load_aircraft()


def test_load_aircraft_missing_columns(csv_storage):
    """Файл без необходимых столбцов не принимается."""
    csv_storage.file_path.write_text(
        "country,callsign\nGermany,DLH123\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="столбцы"):
        csv_storage.load_aircraft()


def test_load_aircraft_empty_csv(csv_storage):
    """Пустой файл не содержит обязательных заголовков."""
    csv_storage.file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="столбцы"):
        csv_storage.load_aircraft()