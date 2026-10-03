from abc import ABC, abstractmethod


class APIAdapter(ABC):
    """Абстрактный класс для работы с API."""

    @abstractmethod
    def get_data(self, **kwargs):
        """Получение данных из API."""
        pass
