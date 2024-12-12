from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class Schedule:
    location_type: str  # 'home', 'work', 'station', 'izakaya'
    duration: int      # in hours
    start_time: int    # 24-hour format

class TokyoResident:
    def __init__(
        self,
        id: int,
        home_location: Tuple[float, float],
        work_location: Tuple[float, float],
        iza_location: Optional[Tuple[float, float]] = None,
        station_location: Optional[Tuple[float, float]] = None,
        has_idea: bool = False
    ):
        self.id = id
        self.home_location = home_location
        self.work_location = work_location
        self.current_location = home_location
        self.iza_location = iza_location
        self.station_location = station_location
        self.has_idea = has_idea
        self.schedule: List[Schedule] = []
        self.current_time = 0  # 24-hour format

    def generate_daily_schedule(self) -> List[Schedule]:
        """Creates a typical daily schedule for the resident"""
        # Basic schedule template - can be randomized or made more complex
        self.schedule = [
            Schedule("home", 8, 0),      # Sleep/morning at home
            Schedule("station", 1, 8),    # Morning commute
            Schedule("work", 8, 9),       # Work
            Schedule("izakaya", 2, 17),   # After work social
            Schedule("station", 1, 19),   # Evening commute
            Schedule("home", 4, 20),      # Evening at home
        ]
        return self.schedule

    def move(self, time: int) -> Tuple[float, float]:
        """Updates location based on schedule and time"""
        for schedule in self.schedule:
            if schedule.start_time <= time < schedule.start_time + schedule.duration:
                if schedule.location_type == "home":
                    self.current_location = self.home_location
                elif schedule.location_type == "work":
                    self.current_location = self.work_location
                elif schedule.location_type == "station":
                    # Add station location logic
                    self.current_location = self.station_location or self.work_location
                elif schedule.location_type == "izakaya":
                    # Add izakaya location logic
                    self.current_location = self.iza_location or self.home_location
                else:
                    self.current_location = self.home_location

        return self.current_location

    def interact(self, other_agents: List['TokyoResident'], transmission_rate: float):
        """Attempt to spread idea to other agents at same location"""
        if not self.has_idea:
            return

        for agent in other_agents:
            if (agent.current_location == self.current_location and
                not agent.has_idea and
                np.random.random() < transmission_rate):
                agent.has_idea = True
