from typing import List, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class Schedule:
    location_type: str  # 'home', 'work', 'home_station', 'work_station', 'izakaya'
    duration: int      # in hours
    start_time: int    # 24-hour format

class TokyoResident:
    def __init__(
        self,
        id: int,
        home_location: Tuple[float, float],
        work_location: Tuple[float, float],
        home_station: Tuple[float, float],
        work_station: Tuple[float, float],
        izakaya_location: Tuple[float, float],
        has_idea: bool = False
    ):
        self.id = id
        self.home_location = home_location
        self.work_location = work_location
        self.home_station = home_station
        self.work_station = work_station
        self.izakaya_location = izakaya_location
        self.current_location = home_location
        self.has_idea = has_idea
        self.schedule: List[Schedule] = []
        self.current_time = 0

    def generate_daily_schedule(self) -> List[Schedule]:
        """Creates a realistic daily schedule with commute patterns"""
        # Add some randomization to timing
        work_start = np.random.randint(7, 10)  # Wider range of start times
        izakaya_prob = 0.4  # Reduced from 0.7

        schedule = [
            Schedule("home", work_start, 0),
            Schedule("home_station", 1, work_start),
            Schedule("work_station", 1, work_start + 1),
            Schedule("work", 8, work_start + 2),
        ]

        # Add evening activities
        if np.random.random() < izakaya_prob:
            schedule.extend([
                Schedule("izakaya", np.random.randint(1, 3), work_start + 10),  # Variable duration
                Schedule("work_station", 1, work_start + 12),
                Schedule("home_station", 1, work_start + 13),
                Schedule("home", 24 - (work_start + 14), work_start + 14)
            ])
        else:
            schedule.extend([
                Schedule("work_station", 1, work_start + 10),
                Schedule("home_station", 1, work_start + 11),
                Schedule("home", 24 - (work_start + 12), work_start + 12)
            ])

        self.schedule = schedule
        return schedule

    def move(self, time: int) -> Tuple[float, float]:
        """Updates location based on schedule and time"""
        for schedule in self.schedule:
            if schedule.start_time <= time < schedule.start_time + schedule.duration:
                if schedule.location_type == "home":
                    self.current_location = self.home_location
                elif schedule.location_type == "work":
                    self.current_location = self.work_location
                elif schedule.location_type == "home_station":
                    self.current_location = self.home_station
                elif schedule.location_type == "work_station":
                    self.current_location = self.work_station
                elif schedule.location_type == "izakaya":
                    self.current_location = self.izakaya_location
                break

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
