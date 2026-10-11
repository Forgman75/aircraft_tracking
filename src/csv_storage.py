import csv
import logging
from pathlib import Path

from src.aircraft import Aircraft
from src.base_classes import BaseStorage

logger = logging.getLogger(__name__)


class CSVStorage(BaseStorage):
    """Класс для сохранения и чтения самолетов в CSV."""

    FIELDNAMES = ["country", "callsign", "speed", "altitude"]

    def __init__(self, filename: str = "aircraft_data.csv"):
        self.save_dir = Path(__file__).parent.parent / "data"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.save_dir / filename

    def save_aircraft(
        self,
        aircraft_list: list[Aircraft],
    ) -> int:
        """Сохраняет список самолетов в CSV-файл."""
        with self.file_path.open(
            "w", encoding="utf-8-sig", newline=""
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )
            writer.writeheader()

            for aircraft in aircraft_list:
                writer.writerow(aircraft.to_dict())

        len_aircraft_list = len(aircraft_list)

        logger.info("Сохранено самолетов: %s", len_aircraft_list)

        return len_aircraft_list

    def load_aircraft(self) -> list[Aircraft]:
        """Читает CSV-файл и возвращает список самолетов."""
        aircraft_list = []

        try:
            with self.file_path.open(
                "r", encoding="utf-8-sig", newline=""
            ) as file:
                reader = csv.DictReader(file)

                if not reader.fieldnames or not set(self.FIELDNAMES).issubset(
                    reader.fieldnames
                ):
                    raise ValueError(
                        "CSV-файл не содержит все необходимые столбцы."
                    )

                for row_number, row in enumerate(reader, start=2):
                    try:
                        aircraft = Aircraft(
                            country=row["country"],
                            callsign=row["callsign"],
                            speed=float(row["speed"]),
                            altitude=float(row["altitude"]),
                        )
                        aircraft_list.append(aircraft)

                    except (ValueError, TypeError, KeyError) as error:
                        logger.warning(
                            "Строка %s пропущена: %s",
                            row_number,
                            error,
                        )

        except FileNotFoundError:
            logger.error("CSV-файл не найден: %s", self.file_path)
            raise

        logger.info("Загружено самолетов: %s", len(aircraft_list))
        return aircraft_list

    def add_aircraft(self, aircraft: Aircraft) -> bool:
        raise NotImplementedError()

    def delete_aircraft(self, **criteria) -> None:
        raise NotImplementedError()

    def get_aircraft(self, **criteria) -> list:
        raise NotImplementedError()
