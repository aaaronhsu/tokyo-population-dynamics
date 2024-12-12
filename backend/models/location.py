from typing import List, Tuple, Dict
from dataclasses import dataclass
import numpy as np

@dataclass
class LocationParams:
    density: float  # Population density factor
    transmission_multiplier: float  # How easily ideas spread here
    capacity: int  # Maximum number of people

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
        
    def add_occupant(self, agent_id: int) -> bool:
        """Add an agent to this location"""
        if len(self.current_occupants) < self.params.capacity:
            self.current_occupants.append(agent_id)
            return True
        return False
        
    def remove_occupant(self, agent_id: int):
        """Remove an agent from this location"""
        if agent_id in self.current_occupants:
            self.current_occupants.remove(agent_id)
            
    def get_transmission_probability(self) -> float:
        """Calculate transmission probability based on current conditions"""
        occupancy_factor = len(self.current_occupants) / self.params.capacity
        return min(
            self.params.density * 
            self.params.transmission_multiplier * 
            occupancy_factor,
            1.0
        )

class LocationManager:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        
    def add_location(self, location_id: str, location: Location):
        self.locations[location_id] = location
        
    def get_nearby_locations(
        self,
        coordinates: Tuple[float, float],
        radius: float,
        location_type: str = None
    ) -> List[Location]:
        """Find locations within radius of coordinates"""
        nearby = []
        for loc in self.locations.values():
            if location_type and loc.type != location_type:
                continue
                
            dist = np.sqrt(
                (coordinates[0] - loc.coordinates[0])**2 +
                (coordinates[1] - loc.coordinates[1])**2
            )
            if dist <= radius:
                nearby.append(loc)
        return nearby
