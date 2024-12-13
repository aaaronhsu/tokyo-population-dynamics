from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class Schedule:
    location_type: str  # 'home', 'work', 'home_station', 'work_station', 'transfer', 'izakaya'
    duration: float    # in hours
    start_time: float  # 24-hour format

class TokyoResident:
    def __init__(
        self,
        id: int,
        home_location: Tuple[float, float],
        work_location: Tuple[float, float],
        home_station: Optional[Tuple[float, float]],
        work_station: Optional[Tuple[float, float]],
        transfer_stations: List[Tuple[float, float]],
        izakaya_location: Optional[Tuple[float, float]],
        uses_train: bool = True,
        goes_to_izakaya: bool = True,
        has_idea: bool = False
    ):
        self.id = id
        self.home_location = home_location
        self.work_location = work_location
        self.home_station = home_station
        self.work_station = work_station
        self.transfer_stations = transfer_stations
        self.izakaya_location = izakaya_location
        self.uses_train = uses_train
        self.goes_to_izakaya = goes_to_izakaya
        self.current_location = home_location
        self.has_idea = has_idea
        self.schedule: List[Schedule] = []
        self.current_time = 0

    def generate_daily_schedule(self) -> List[Schedule]:
        """Creates a realistic daily schedule with transfers"""
        # Randomize work start time (most people start between 8-10)
        work_start = np.random.normal(9, 0.5)  # Normal distribution centered at 9
        work_start = max(min(work_start, 10), 8)  # Clamp between 8 and 10

        schedule = []
        current_time = 0.0

        # Morning at home
        schedule.append(Schedule("home", work_start, current_time))
        current_time = work_start

        if self.uses_train:
            # Morning commute with transfers
            schedule.append(Schedule("home_station", 0.3, current_time))
            current_time += 0.3

            # Add transfer stations to morning commute
            for transfer_station in self.transfer_stations:
                schedule.append(Schedule("transfer", 0.2, current_time))
                current_time += 0.2

            schedule.append(Schedule("work_station", 0.3, current_time))
            current_time += 0.3
        else:
            # Direct commute without train
            current_time += 0.5  # Simple commute time

        # Work day
        work_duration = np.random.normal(8, 0.5)  # Normal distribution around 8 hours
        work_duration = max(min(work_duration, 9), 7)  # Clamp between 7-9 hours
        schedule.append(Schedule("work", work_duration, current_time))
        current_time += work_duration

        # Evening activities
        if self.goes_to_izakaya and self.izakaya_location:
            # Randomly decide between early night and late night
            late_night = np.random.random() < 0.2  # 20% chance of staying out late

            if late_night:
                # Stay until last train or even later
                izakaya_duration = np.random.uniform(4, 6)
                schedule.append(Schedule("izakaya", izakaya_duration, current_time))
                current_time += izakaya_duration

                if np.random.random() < 0.3:  # 30% chance of missing last train
                    # Stay until first train (around 5 AM)
                    schedule.append(Schedule("izakaya", 24 - current_time, current_time))
                    return schedule
            else:
                # Regular izakaya visit
                izakaya_duration = np.random.uniform(1.5, 3)
                schedule.append(Schedule("izakaya", izakaya_duration, current_time))
                current_time += izakaya_duration

        # Evening commute
        if self.uses_train:
            schedule.append(Schedule("work_station", 0.3, current_time))
            current_time += 0.3

            # Return journey transfers
            for transfer_station in reversed(self.transfer_stations):
                schedule.append(Schedule("transfer", 0.2, current_time))
                current_time += 0.2

            schedule.append(Schedule("home_station", 0.3, current_time))
            current_time += 0.3
        else:
            # Direct commute home
            current_time += 0.5

        # Rest of the day at home
        schedule.append(Schedule("home", 24 - current_time, current_time))

        self.schedule = schedule
        return schedule

    def move(self, time: int) -> Tuple[float, float]:
        """Updates location based on schedule and time"""
        time_float = float(time)

        for schedule in self.schedule:
            if schedule.start_time <= time_float < (schedule.start_time + schedule.duration):
                if schedule.location_type == "home":
                    self.current_location = self.home_location
                elif schedule.location_type == "work":
                    self.current_location = self.work_location
                elif schedule.location_type == "home_station" and self.home_station:
                    self.current_location = self.home_station
                elif schedule.location_type == "work_station" and self.work_station:
                    self.current_location = self.work_station
                elif schedule.location_type == "transfer":
                    idx = sum(1 for s in self.schedule[:self.schedule.index(schedule)]
                            if s.location_type == "transfer")
                    if 0 <= idx < len(self.transfer_stations):
                        self.current_location = self.transfer_stations[idx]
                    else:
                        # Fallback to work station if index is out of range
                        self.current_location = self.work_station if self.work_station else self.work_location
                elif schedule.location_type == "izakaya" and self.izakaya_location:
                    self.current_location = self.izakaya_location
                break

        return self.current_location

    def interact(self, other_agents: List['TokyoResident'], base_transmission_rate: float):
        """Attempt to spread idea to other agents at same location"""
        if not self.has_idea:
            return

        # Get current schedule entry to determine location type
        current_schedule = next(
            (s for s in self.schedule
             if s.start_time <= (self.current_time % 24) < s.start_time + s.duration),
            None
        )

        if current_schedule:
            # Modify transmission rate based on location type
            modified_rate = base_transmission_rate
            if current_schedule.location_type == "work":
                modified_rate *= 0.2  # Significantly reduce transmission at work
            elif current_schedule.location_type == "izakaya":
                modified_rate *= 5.0  # Significantly increase transmission at izakaya
            elif current_schedule.location_type in ["transfer", "work_station", "home_station"]:
                modified_rate *= 2.0  # Moderate increase in crowded transit areas
            elif current_schedule.location_type == "home":
                modified_rate *= 0.1  # Very low transmission at home

            # Apply transmission to other agents
            for agent in other_agents:
                if (agent.current_location == self.current_location and
                    not agent.has_idea and
                    np.random.random() < modified_rate):
                    agent.has_idea = True
