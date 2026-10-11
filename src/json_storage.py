import json
import logging
from pathlib import Path
from src.base_classes import BaseStorage
from src.aircraft import Aircraft

logger = logging.getLogger("storage")
logger.setLevel(logging.DEBUG)


class JSONStorage(BaseStorage):
    """Реализация хранения данных в JSON-файле."""

    def __init__(self, filename: str = "aircraft_data.json"):

        save_dir = Path(__file__).parent.parent / "data"
        save_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = save_dir / filename

        if not self.file_path.exists():
            self._save_data([])

    def _load_data(self) -> list:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.error("JSON-файл должен содержать список.")
                return []

            return data

        except FileNotFoundError:
            logger.error(f"Файл не найден: {self.file_path}")
            return []

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return []

    def _save_data(self, data: list):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        """Добавляет самолет в JSON, если его позывной еще не сохранен.

        Возвращает True, если самолет добавлен,
        и False, если самолет с таким позывным уже существует.
        """
        if not isinstance(aircraft, Aircraft):
            raise TypeError("Можно добавлять только объекты класса Aircraft.")

        data = self._load_data()

        callsign = aircraft.callsign.strip().casefold()

        for item in data:
            if not isinstance(item, dict):
                continue

            existing_callsign = item.get("callsign")

            if (
                isinstance(existing_callsign, str)
                and existing_callsign.strip().casefold() == callsign
            ):
                logger.info(
                    "Самолет с позывным %s уже существует.",
                    aircraft.callsign,
                )

                return False

        data.append(aircraft.to_dict())
        self._save_data(data)

        logger.info(
            "Самолет %s успешно добавлен.",
            aircraft.callsign,
        )
        return True

    def save_aircraft(self, aircraft_list: list[Aircraft]) -> int:
        """Пакетно добавляет самолеты, исключая дубликаты.

        Возвращает количество добавленных самолетов.
        """
        data = self._load_data()

        # Собираем позывные уже сохраненных самолетов.
        existing_callsigns = {
            item["callsign"].strip().casefold()
            for item in data
            if isinstance(item, dict)
            and isinstance(item.get("callsign"), str)
            and item["callsign"].strip()
        }

        added = 0

        for aircraft in aircraft_list:
            if not isinstance(aircraft, Aircraft):
                continue

            callsign = aircraft.callsign.strip().casefold()

            if callsign in existing_callsigns:
                continue

            data.append(aircraft.to_dict())
            existing_callsigns.add(callsign)
            added += 1

        if added:
            self._save_data(data)

        return added

    def get_aircraft(self, **criteria) -> list:
        data = self._load_data()
        result = []
        for item in data:
            match = True
            for key, value in criteria.items():
                if key in item:
                    # Для строк делаем нечувствительный к регистру
                    #  поиск подстроки
                    if isinstance(value, str) and isinstance(item[key], str):
                        if value.lower() not in item[key].lower():
                            match = False
                            break
                    elif item[key] != value:
                        match = False
                        break
            if match:
                result.append(Aircraft.from_dict(item))
        return result

    def delete_aircraft(self, **criteria) -> None:
        data = self._load_data()
        new_data = []
        for item in data:
            match = False
            for key, value in criteria.items():
                if (
                    key in item
                    and str(item[key]).lower() == str(value).lower()
                ):
                    match = True
                    break
            if not match:
                new_data.append(item)
        self._save_data(new_data)

    def load_aircraft(self) -> list[Aircraft]:
        raise NotImplementedError()
