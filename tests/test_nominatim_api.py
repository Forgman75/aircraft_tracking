import pytest
from unittest.mock import patch, MagicMock
from src.nominatim_api import NominatimAPI


@patch("src.nominatim_api.get")
def test_get_data_success(mock_get):
    # Настраиваем мок ответа
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"boundingbox": ["50.0", "55.0", "30.0", "40.0"]}
    ]
    mock_get.return_value = mock_response

    api = NominatimAPI()
    result = api.get_data(country="Germany")

    assert result == ["50.0", "55.0", "30.0", "40.0"]
    mock_get.assert_called_once()


@patch("src.nominatim_api.get")
def test_get_data_country_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = []  # Пустой ответ
    mock_get.return_value = mock_response

    api = NominatimAPI()
    with pytest.raises(ValueError, match="Не удалось найти координаты страны"):
        api.get_data(country="NonExistentCountry123")
