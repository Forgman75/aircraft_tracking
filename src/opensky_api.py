from requests import get
from src.base_classes import APIAdapter


class OpenSkyAPI(APIAdapter):
    """Класс для работы с API OpenSky Network."""

    def __init__(self):
        self.url = "https://opensky-network.org/api/states/all"

    def get_data(self, boundingbox):
        params = {
            "lamin": boundingbox[0],
            "lamax": boundingbox[1],
            "lomin": boundingbox[2],
            "lomax": boundingbox[3],
        }

        response = get(
            url=self.url,
            params=params
        )

        response.raise_for_status()

        return response.json()
