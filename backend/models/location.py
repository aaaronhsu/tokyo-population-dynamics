from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class LocationParams:
    density: float
    transmission_multiplier: float
    capacity: int

class Location:
    def __init__(
        self,
        location_type: str,
        coordinates: Tuple[float, float],
        params: LocationParams
    ):
        self.type = location_type
        self.coordinates = coordinates
        self.params = params
        self.current_occupants: List[int] = []  # List of agent IDs

class LocationManager:
    def __init__(self):
        self.locations: Dict[str, Location] = {}

    def add_location(self, location_id: str, location: Location):
        self.locations[location_id] = location
