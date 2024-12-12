from typing import List, Dict, Tuple
import numpy as np
from .agent import TokyoResident
from .location import Location, LocationManager, LocationParams

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
        # Example location creation - expand based on your needs
        station_params = LocationParams(
            density=0.8,
            transmission_multiplier=1.2,
            capacity=1000
        )
        
        izakaya_params = LocationParams(
            density=0.9,
            transmission_multiplier=1.5,
            capacity=50
        )
        
        # Add some sample locations
        # In practice, you'd want to load real Tokyo data
        for i in range(self.params.get('num_stations', 10)):
            lat = np.random.uniform(self.city_bounds[0][0], self.city_bounds[1][0])
            lon = np.random.uniform(self.city_bounds[0][1], self.city_bounds[1][1])
            station = Location('station', (lat, lon), station_params)
            self.location_manager.add_location(f'station_{i}', station)
            
    def _create_agents(self):
        """Initialize agents with home/work locations"""
        for i in range(self.num_agents):
            home_loc = (
                np.random.uniform(self.city_bounds[0][0], self.city_bounds[1][0]),
                np.random.uniform(self.city_bounds[0][1], self.city_bounds[1][1])
            )
            work_loc = (
                np.random.uniform(self.city_bounds[0][0], self.city_bounds[1][0]),
                np.random.uniform(self.city_bounds[0][1], self.city_bounds[1][1])
            )
            agent = TokyoResident(i, home_loc, work_loc)
            agent.generate_daily_schedule()
            self.agents.append(agent)
            
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
        self.current_time = (self.current_time + 1) % 24
        
        # Move agents
        for agent in self.agents:
            agent.move(self.current_time)
            
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
                agent.interact(agents, self.params.get('transmission_rate', 0.1))
                
    def get_state(self) -> Dict:
        """Return current simulation state"""
        return {
            'time': self.current_time,
            'infected_count': sum(1 for agent in self.agents if agent.has_idea),
            'agent_locations': [(agent.current_location, agent.has_idea) 
                              for agent in self.agents],
            'infection_rate': sum(agent.has_idea for agent in self.agents) / len(self.agents)
        }
