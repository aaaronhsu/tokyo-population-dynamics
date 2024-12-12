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
            # Major Hub Stations
            ("Tokyo", (35.6812, 139.7671)),
            ("Shinjuku", (35.6896, 139.7006)),
            ("Shibuya", (35.6580, 139.7016)),
            ("Ikebukuro", (35.7295, 139.7109)),
            ("Shinagawa", (35.6284, 139.7387)),
            ("Ueno", (35.7141, 139.7774)),
            ("Akihabara", (35.6982, 139.7731)),

            # Yamanote Line
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

            # Chuo Line
            ("Nakano", (35.7073, 139.6659)),
            ("Ogikubo", (35.7047, 139.6199)),
            ("Kichijoji", (35.7029, 139.5800)),
            ("Mitaka", (35.7027, 139.5610)),

            # Other Major Transfer Stations
            ("Otemachi", (35.6859, 139.7664)),
            ("Roppongi", (35.6641, 139.7315)),
            ("Daimon", (35.6563, 139.7555)),
            ("Nihombashi", (35.6820, 139.7741)),
            ("Ginza", (35.6742, 139.7639)),
            ("Kasumigaseki", (35.6731, 139.7504)),
            ("Aoyama-Itchome", (35.6728, 139.7237)),
            ("Iidabashi", (35.7019, 139.7456)),
            ("Takadanobaba", (35.7121, 139.7038)),
        ]

        # Add stations to location manager
        for name, coords in major_stations:
            station = Location('station', coords, station_params)
            self.location_manager.add_location(f'station_{name}', station)

        # Create transfer probabilities between stations
        self.transfer_probabilities = self._create_transfer_probabilities(major_stations)

    def _create_transfer_probabilities(self, stations):
        """Create a dictionary of likely transfer combinations"""
        transfer_prob = {}

        # Define major transfer routes
        common_transfers = {
            "Tokyo": ["Otemachi", "Nihombashi", "Yurakucho"],
            "Shinjuku": ["Takadanobaba", "Nakano", "Harajuku"],
            "Shibuya": ["Harajuku", "Ebisu", "Aoyama-Itchome"],
            "Ikebukuro": ["Takadanobaba", "Komagome", "Tabata"],
            "Ueno": ["Nippori", "Akihabara", "Okachimachi"],
            "Akihabara": ["Kanda", "Nihombashi", "Ueno"],
            "Otemachi": ["Tokyo", "Nihombashi", "Ginza"],
        }

        # Create probability mappings
        for start, transfers in common_transfers.items():
            transfer_prob[f"station_{start}"] = [f"station_{t}" for t in transfers]

        return transfer_prob


    def _create_agents(self):
        """Initialize agents with realistic locations and transfer stations"""
        # Convert locations to lists for easier indexing
        stations = [(loc_id, loc) for loc_id, loc in self.location_manager.locations.items()
                   if loc.type == 'station']
        izakayas = [(loc_id, loc) for loc_id, loc in self.location_manager.locations.items()
                   if loc.type == 'izakaya']

        for i in range(self.num_agents):
            # Generate home location in a neighborhood
            neighborhood = select_random_neighborhood()
            home_loc = generate_home_location(neighborhood)

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
            num_transfers = np.random.poisson(2.3)  # Average 2.3 transfers
            num_transfers = min(max(num_transfers, 1), 3)  # Limit to 1-3 transfers

            # Find potential transfer stations
            potential_transfers = [
                s for s in stations
                if (s[0] != home_station_id and
                    s[0] != work_station_id and
                    self._is_between(s[1].coordinates, home_station.coordinates, work_station.coordinates))
            ]

            # Select transfer stations along the route
            transfer_stations = []
            if potential_transfers and num_transfers > 0:
                # Sort potential transfers by distance from home station
                potential_transfers.sort(
                    key=lambda s: self._distance(home_station.coordinates, s[1].coordinates)
                )

                # Select evenly spaced transfer stations
                step = len(potential_transfers) // (num_transfers + 1)
                if step > 0:
                    for i in range(num_transfers):
                        idx = min((i + 1) * step, len(potential_transfers) - 1)
                        transfer_stations.append(potential_transfers[idx][1].coordinates)

            # Work location near station with smaller offset
            work_loc = self._add_offset(work_station.coordinates, max_offset=0.005)

            # Assign izakaya near work station
            nearby_izakayas = [
                iz for iz in izakayas
                if self._distance(iz[1].coordinates, work_station.coordinates) < 0.01
            ]

            if nearby_izakayas:
                _, izakaya = nearby_izakayas[np.random.randint(len(nearby_izakayas))]
                izakaya_loc = izakaya.coordinates
            else:
                izakaya_loc = work_station.coordinates

            agent = TokyoResident(
                id=i,
                home_location=home_loc,
                work_location=work_loc,
                home_station=home_station.coordinates,
                work_station=work_station.coordinates,
                transfer_stations=transfer_stations,
                izakaya_location=izakaya_loc
            )
            agent.generate_daily_schedule()
            self.agents.append(agent)

    def _is_between(self, point: Tuple[float, float],
                    start: Tuple[float, float],
                    end: Tuple[float, float],
                    tolerance: float = 0.1) -> bool:
        """Check if a point is roughly between start and end points"""
        # Calculate distances
        d_start_end = self._distance(start, end)
        d_start_point = self._distance(start, point)
        d_point_end = self._distance(point, end)

        # Check if point is roughly along the path
        # Allow for some deviation from the direct path
        return abs(d_start_point + d_point_end - d_start_end) < (d_start_end * tolerance)

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
        # Don't modulo by 24 anymore since we're tracking full week
        self.current_time += 1

        # Move agents
        for agent in self.agents:
            agent.move(self.current_time % 24)  # Pass hour of day to agent

        # Process interactions
        self._process_interactions()

    def _process_interactions(self):
        """Handle agent interactions and idea transmission"""
        # Group agents by location
        location_groups: Dict[Tuple[float, float], List[TokyoResident]] = {}
        for agent in self.agents:
            loc = agent.current_location
            if loc not in location_groups:
                location_groups[loc] = []
            location_groups[loc].append(agent)

        # Process interactions for each location
        for agents in location_groups.values():
            for agent in agents:
                agent.interact(agents, self.params.get('transmission_rate', 0.05))

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
