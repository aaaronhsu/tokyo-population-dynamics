from typing import List, Dict, Tuple
import numpy as np
from .agent import TokyoResident
from .location import Location, LocationManager, LocationParams
from .neighborhoods import TOKYO_NEIGHBORHOODS, generate_home_location, select_random_neighborhood

class TokyoSimulation:
    def __init__(
        self,
        num_agents: int,
        city_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
        simulation_params: Dict
    ):
        self.num_agents = num_agents
        self.city_bounds = city_bounds  # ((min_lat, min_lon), (max_lat, max_lon))
        self.params = simulation_params
        self.current_time = 0

        self.location_manager = LocationManager()
        self.agents: List[TokyoResident] = []

        self.initialize_simulation()

    def initialize_simulation(self):
        """Set up initial simulation state"""
        self._create_locations()
        self._create_agents()
        self._initialize_idea_spread()

    def _create_locations(self):
        """Initialize locations across Tokyo"""
        station_params = LocationParams(
            density=0.6,
            transmission_multiplier=1.1,
            capacity=1000
        )

        # Major stations with accurate coordinates
        major_stations = [
            ("Tokyo", (35.6812, 139.7671)),
            ("Shinjuku", (35.6896, 139.7006)),
            ("Shibuya", (35.6580, 139.7016)),
            ("Ikebukuro", (35.7295, 139.7109)),
            ("Shinagawa", (35.6284, 139.7387)),
            ("Ueno", (35.7141, 139.7774)),
            ("Akihabara", (35.6982, 139.7731)),

            # Additional stations for transfers
            ("Harajuku", (35.6702, 139.7027)),
            ("Ebisu", (35.6462, 139.7103)),
            ("Meguro", (35.6340, 139.7157)),
            ("Gotanda", (35.6262, 139.7233)),
            ("Osaki", (35.6197, 139.7286)),
            ("Tamachi", (35.6457, 139.7475)),
            ("Hamamatsucho", (35.6553, 139.7571)),
            ("Yurakucho", (35.6749, 139.7628)),
            ("Kanda", (35.6918, 139.7712)),
            ("Nippori", (35.7281, 139.7707)),
            ("Komagome", (35.7373, 139.7468)),
            ("Tabata", (35.7381, 139.7608)),
        ]

        for name, coords in major_stations:
            station = Location('station', coords, station_params)
            self.location_manager.add_location(f'station_{name}', station)

        # Create izakayas near stations with custom capacity
        izakaya_params = LocationParams(
            density=0.7,
            transmission_multiplier=1.3,
            capacity=self.params.get('izakaya_capacity', 50)
        )

        # Create clusters of izakayas near each station
        for station_name, station_coords in major_stations:
            for i in range(3):  # 3 izakayas per station
                lat_offset = np.random.uniform(-0.005, 0.005)
                lon_offset = np.random.uniform(-0.005, 0.005)
                izakaya_coords = (
                    station_coords[0] + lat_offset,
                    station_coords[1] + lon_offset
                )
                izakaya = Location('izakaya', izakaya_coords, izakaya_params)
                self.location_manager.add_location(f'izakaya_{station_name}_{i}', izakaya)

    def _create_agents(self):
        """Initialize agents with realistic locations"""
        stations = [(loc_id, loc) for loc_id, loc in self.location_manager.locations.items()
                   if loc.type == 'station']
        izakayas = [(loc_id, loc) for loc_id, loc in self.location_manager.locations.items()
                   if loc.type == 'izakaya']

        # Get parameters with defaults
        train_commuter_ratio = self.params.get('train_commuter_ratio', 0.9)
        avg_transfers = self.params.get('avg_transfers', 2.3)
        izakaya_probability = self.params.get('izakaya_probability', 0.7)

        for i in range(self.num_agents):
            # Generate home location in a neighborhood
            neighborhood = select_random_neighborhood()
            home_loc = generate_home_location(neighborhood)

            # Determine if agent uses train
            uses_train = np.random.random() < train_commuter_ratio

            if uses_train:
                # Assign nearest station to home
                home_station_id, home_station = min(stations,
                                                  key=lambda s: self._distance(home_loc, s[1].coordinates))

                # Create weights for station selection
                station_weights = []
                for station_id, _ in stations:
                    weight = 1.5 if ('Tokyo' in station_id or 'Shinjuku' in station_id) else 1.0
                    station_weights.append(weight)

                # Normalize weights
                station_weights = np.array(station_weights, dtype=float)
                station_weights /= station_weights.sum()

                # Select work station
                selected_idx = np.random.choice(len(stations), p=station_weights)
                work_station_id, work_station = stations[selected_idx]

                # Generate transfer stations
                num_transfers = np.random.poisson(avg_transfers)
                num_transfers = min(max(num_transfers, 0), 5)  # Limit to 0-5 transfers

                # Select transfer stations along the route
                transfer_stations = self._select_transfer_stations(
                    home_station.coordinates,
                    work_station.coordinates,
                    stations,
                    num_transfers
                )
            else:
                # Non-train commuters have direct routes
                home_station = None
                work_station = None
                transfer_stations = []

            # Work location near station or random location
            if work_station:
                work_loc = self._add_offset(work_station.coordinates, max_offset=0.005)
            else:
                work_loc = (
                    np.random.uniform(self.city_bounds[0][0], self.city_bounds[1][0]),
                    np.random.uniform(self.city_bounds[0][1], self.city_bounds[1][1])
                )

            # Assign izakaya near work location if agent goes to izakayas
            goes_to_izakaya = np.random.random() < izakaya_probability
            if goes_to_izakaya and work_station:
                nearby_izakayas = [
                    iz for iz in izakayas
                    if self._distance(iz[1].coordinates, work_station.coordinates) < 0.01
                ]
                if nearby_izakayas:
                    _, izakaya = nearby_izakayas[np.random.randint(len(nearby_izakayas))]
                    izakaya_loc = izakaya.coordinates
                else:
                    izakaya_loc = work_station.coordinates
            else:
                izakaya_loc = None

            agent = TokyoResident(
                id=i,
                home_location=home_loc,
                work_location=work_loc,
                home_station=home_station.coordinates if home_station else None,
                work_station=work_station.coordinates if work_station else None,
                transfer_stations=transfer_stations,
                izakaya_location=izakaya_loc,
                uses_train=uses_train,
                goes_to_izakaya=goes_to_izakaya
            )
            agent.generate_daily_schedule()
            self.agents.append(agent)

    def _select_transfer_stations(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        stations: List[Tuple[str, Location]],
        num_transfers: int
    ) -> List[Tuple[float, float]]:
        """Select reasonable transfer stations between start and end stations"""
        if num_transfers == 0:
            return []

        potential_transfers = [
            s for s in stations
            if self._is_between(s[1].coordinates, start_coords, end_coords)
        ]

        transfer_stations = []
        if potential_transfers:
            # Sort by distance from start
            potential_transfers.sort(
                key=lambda s: self._distance(start_coords, s[1].coordinates)
            )

            # Select evenly spaced stations
            if num_transfers > 0:
                step = len(potential_transfers) // (num_transfers + 1)
                if step > 0:
                    for i in range(num_transfers):
                        idx = min((i + 1) * step, len(potential_transfers) - 1)
                        transfer_stations.append(potential_transfers[idx][1].coordinates)

        return transfer_stations

    def _initialize_idea_spread(self):
        """Select initial agents who have the idea"""
        initial_spreaders = np.random.choice(
            self.agents,
            size=self.params.get('initial_infected', 1),
            replace=False
        )
        for agent in initial_spreaders:
            agent.has_idea = True

    def step(self):
        """Advance simulation by one time step"""
        self.current_time += 1

        # Move agents
        for agent in self.agents:
            agent.move(self.current_time % 24)  # Pass hour of day

        # Process interactions
        self._process_interactions()

    def _process_interactions(self):
        """Handle agent interactions and idea transmission"""
        base_transmission_rate = self.params.get('transmission_rate', 0.05)

        # Group agents by location
        location_groups: Dict[Tuple[float, float], List[TokyoResident]] = {}
        for agent in self.agents:
            loc = agent.current_location
            if loc not in location_groups:
                location_groups[loc] = []
            location_groups[loc].append(agent)

        # Process interactions for each location
        for agents in location_groups.values():
            # Additional density-based modification
            group_size = len(agents)
            density_multiplier = min(group_size / 10, 2.0)  # Cap at 2x for large groups

            for agent in agents:
                agent.interact(agents, base_transmission_rate * density_multiplier)

    def get_state(self) -> Dict:
        """Return current simulation state"""
        return {
            'time': self.current_time,
            'infected_count': sum(1 for agent in self.agents if agent.has_idea),
            'agent_locations': [(agent.current_location, agent.has_idea)
                              for agent in self.agents],
            'infection_rate': sum(agent.has_idea for agent in self.agents) / len(self.agents)
        }

    @staticmethod
    def _distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate simple distance between two coordinates"""
        return np.sqrt(
            (coord1[0] - coord2[0])**2 +
            (coord1[1] - coord2[1])**2
        )

    @staticmethod
    def _add_offset(coords: Tuple[float, float], max_offset: float = 0.005) -> Tuple[float, float]:
        """Add small random offset to coordinates"""
        return (
            coords[0] + np.random.uniform(-max_offset, max_offset),
            coords[1] + np.random.uniform(-max_offset, max_offset)
        )

    @staticmethod
    def _is_between(
        point: Tuple[float, float],
        start: Tuple[float, float],
        end: Tuple[float, float],
        tolerance: float = 0.1
    ) -> bool:
        """Check if a point is roughly between start and end points"""
        d_start_end = np.sqrt(
            (start[0] - end[0])**2 +
            (start[1] - end[1])**2
        )
        d_start_point = np.sqrt(
            (start[0] - point[0])**2 +
            (start[1] - point[1])**2
        )
        d_point_end = np.sqrt(
            (point[0] - end[0])**2 +
            (point[1] - end[1])**2
        )

        return abs(d_start_point + d_point_end - d_start_end) < (d_start_end * tolerance)
