import pytest
from src.aircraft import Aircraft


def test_valid_creation():
    aircraft = Aircraft("Russia", "AFL101", 250.0, 10000.0)
    assert aircraft.country == "Russia"
    assert aircraft.callsign == "AFL101"
    assert aircraft.speed == 250.0
    assert aircraft.altitude == 10000.0


@pytest.mark.parametrize("country, callsign, speed, altitude", [
    ("", "AFL101", 250.0, 10000.0),               # Пустая страна
    ("Russia", "   ", 250.0, 10000.0),             # Пустой позывной
    ("Russia", "AFL101", -10.0, 10000.0),          # Отрицательная скорость
    ("Russia", "AFL101", 250.0, -500.0),           # Отрицательная высота
    ("Russia", "AFL101", "fast", 10000.0),         # Неверный тип скорости
])
def test_invalid_creation_raises_value_error(country, callsign, speed, altitude):
    with pytest.raises(ValueError):
        Aircraft(country, callsign, speed, altitude)


def test_none_values_converted_to_zero():
    # OpenSky часто возвращает None
    aircraft = Aircraft("Russia", "AFL101", None, None)
    assert aircraft.speed == 0.0
    assert aircraft.altitude == 0.0


def test_comparison_methods():
    plane1 = Aircraft("Russia", "AFL101", 200.0, 10000.0)
    plane2 = Aircraft("Germany", "DLH404", 250.0, 12000.0)
    plane3 = Aircraft("France", "AFR123", 250.0, 12000.0) # Такая же высота и скорость

    assert plane1 < plane2       # __lt__
    assert plane2 > plane1       # __gt__
    assert plane2 == plane3      # __eq__
    assert plane2.is_faster_than(plane1) # is_faster_than

    # Проверяем, что сравнение с неподходящим типом вызывает TypeError
    with pytest.raises(TypeError):
        _ = plane1 < "string"
        
    with pytest.raises(TypeError):
        _ = plane1 > 123
        
    with pytest.raises(TypeError):
        plane1.is_faster_than("string")


def test_dict_conversion():
    plane = Aircraft("Russia", "AFL101", 250.0, 10000.0)
    data = plane.to_dict()
    assert data == {"country": "Russia", "callsign": "AFL101", "speed": 250.0, "altitude": 10000.0}
        
    restored_plane = Aircraft.from_dict(data)
    assert restored_plane.callsign == plane.callsign


def test_cast_to_object_list_valid_and_invalid():
    raw_data = [
        ["id0", "AFL101", "Russia", None, None, None, None, None, None, 250.0, None, None, None, 10000.0], # Валидный (индексы 1, 2, 9, 13)
        ["id1", "DLH404", "Germany"], # Слишком короткий (len < 14)
        ["id2", "AFR123", "France", None, None, None, None, None, None, "N/A", None, None, None, 8000.0], # Некорректная скорость
    ]
        
    result = Aircraft.cast_to_object_list(raw_data)
        
    assert len(result) == 1 # Должен пройти только первый
    assert result[0].callsign == "AFL101"
    assert result[0].country == "Russia"


def test_cast_to_object_list_wrong_type():
    # Передача не-list должна вернуть пустой список, а не упасть
    assert Aircraft.cast_to_object_list(None) == []
    assert Aircraft.cast_to_object_list("not a list") == []





