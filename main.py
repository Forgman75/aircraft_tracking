from src.nominatim_api import NominatimAPI
from src.opensky_api import OpenSkyAPI
from src.aircraft import Aircraft


nominatim = NominatimAPI()
opensky = OpenSkyAPI()

country = "Canada"

boundingbox = nominatim.get_data(country)
aircraftes_data = opensky.get_data(boundingbox)
aircraftes = Aircraft.cast_to_object_list(aircraftes_data)



print("Координаты страны:", boundingbox)
print("Данные о самолетах:", aircraftes)