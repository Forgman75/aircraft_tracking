import pytest
from unittest.mock import patch, MagicMock
from src.opensky_api import OpenSkyAPI


@patch("src.opensky_api.get")
def test_get_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "states": [
            [
                "id",
                "AFL101",
                "Russia",
                0,
                0,
                0,
                0,
                0,
                0,
                250.0,
                0,
                0,
                0,
                10000.0,
            ]
        ]
    }
    mock_get.return_value = mock_response

    api = OpenSkyAPI()
    result = api.get_data(boundingbox=["50.0", "55.0", "30.0", "40.0"])

    assert len(result) == 1
    assert result[0][1] == "AFL101"


@patch("src.opensky_api.get")
def test_get_data_empty_states(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"states": None}
    mock_get.return_value = mock_response

    api = OpenSkyAPI()
    result = api.get_data(boundingbox=["50.0", "55.0", "30.0", "40.0"])

    assert result == []


@patch("src.opensky_api.get")
def test_get_data_rate_limit(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    api = OpenSkyAPI()
    with pytest.raises(RuntimeError, match="Превышен лимит запросов"):
        api.get_data(boundingbox=["50.0", "55.0", "30.0", "40.0"])
