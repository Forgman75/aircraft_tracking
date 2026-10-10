from abc import ABC, abstractmethod
from src.aircraft import Aircraft


class APIAdapter(ABC):
    """Абстрактный класс для работы с API."""

    @abstractmethod
    def get_data(self, **kwargs):
        """Получение данных из API."""
        pass


class BaseStorage(ABC):
    """Абстрактный класс для хранения данных о самолетах."""

    @abstractmethod
    def add_aircraft(self, aircraft: Aircraft):
        pass

    @abstractmethod
    def save_aircraft(self, aircraft_list: list[Aircraft]):
        pass

    @abstractmethod
    def load_aircraft(self) -> list[Aircraft]:
        pass
    
    @abstractmethod
    def get_aircraft(self, **criteria) -> list:
        pass

    @abstractmethod
    def delete_aircraft(self, **criteria):
        pass

