from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class LocationParams:
    density: float              # How densely packed people are (affects transmission)
    transmission_multiplier: float  # Location-specific transmission rate modifier
    capacity: int              # Maximum number of people allowed

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
        """
        Add an agent to this location if capacity allows
        Returns True if successful, False if at capacity
        """
        if len(self.current_occupants) < self.params.capacity:
            self.current_occupants.append(agent_id)
            return True
        return False

    def remove_occupant(self, agent_id: int) -> None:
        """Remove an agent from this location"""
        if agent_id in self.current_occupants:
            self.current_occupants.remove(agent_id)

    def get_occupancy_ratio(self) -> float:
        """Return current occupancy ratio (0.0 to 1.0)"""
        return len(self.current_occupants) / self.params.capacity

    def get_transmission_factor(self) -> float:
        """
        Calculate transmission factor based on occupancy and location type
        Higher occupancy = higher transmission probability
        """
        occupancy_ratio = self.get_occupancy_ratio()
        base_factor = self.params.density * self.params.transmission_multiplier

        # Increase transmission rate as occupancy increases
        occupancy_multiplier = 1.0 + (occupancy_ratio * 0.5)  # Max 50% increase at full capacity

        return base_factor * occupancy_multiplier

class LocationManager:
    def __init__(self):
        self.locations: Dict[str, Location] = {}

    def add_location(self, location_id: str, location: Location) -> None:
        """Add a location to the manager"""
        self.locations[location_id] = location

    def get_location(self, location_id: str) -> Location:
        """Get a location by ID"""
        return self.locations.get(location_id)

    def get_locations_by_type(self, location_type: str) -> List[Tuple[str, Location]]:
        """Get all locations of a specific type"""
        return [(loc_id, loc) for loc_id, loc in self.locations.items()
                if loc.type == location_type]

    def get_nearby_locations(
        self,
        coordinates: Tuple[float, float],
        radius: float,
        location_type: str = None
    ) -> List[Tuple[str, Location]]:
        """Find locations within radius of coordinates"""
        nearby = []
        for loc_id, loc in self.locations.items():
            if location_type and loc.type != location_type:
                continue

            dist = ((coordinates[0] - loc.coordinates[0])**2 +
                   (coordinates[1] - loc.coordinates[1])**2)**0.5

            if dist <= radius:
                nearby.append((loc_id, loc))

        return nearby

    def update_capacities(self, location_type: str, new_capacity: int) -> None:
        """Update capacity for all locations of a specific type"""
        for location in self.locations.values():
            if location.type == location_type:
                location.params.capacity = new_capacity
                # Remove excess occupants if necessary
                while len(location.current_occupants) > new_capacity:
                    location.current_occupants.pop()

    def get_occupancy_stats(self) -> Dict[str, Dict]:
        """Get occupancy statistics for all location types"""
        stats = {}
        for location_type in set(loc.type for loc in self.locations.values()):
            locations_of_type = [loc for loc in self.locations.values()
                               if loc.type == location_type]

            total_capacity = sum(loc.params.capacity for loc in locations_of_type)
            total_occupants = sum(len(loc.current_occupants) for loc in locations_of_type)

            stats[location_type] = {
                'total_capacity': total_capacity,
                'total_occupants': total_occupants,
                'occupancy_rate': total_occupants / total_capacity if total_capacity > 0 else 0,
                'num_locations': len(locations_of_type)
            }

        return stats

    def clear_all_occupants(self) -> None:
        """Clear all occupants from all locations"""
        for location in self.locations.values():
            location.current_occupants.clear()
