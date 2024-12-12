from typing import List, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class Schedule:
    location_type: str
    duration: float
    start_time: float
    station_id: str = None

class TokyoResident:
    def __init__(
        self,
        id: int,
        home_location: Tuple[float, float],
        work_location: Tuple[float, float],
        home_station: Tuple[float, float],
        work_station: Tuple[float, float],
        transfer_stations: List[Tuple[float, float]],
        izakaya_location: Tuple[float, float],
        has_idea: bool = False
    ):
        self.id = id
        self.home_location = home_location
        self.work_location = work_location
        self.home_station = home_station
        self.work_station = work_station
        self.transfer_stations = transfer_stations
        self.izakaya_location = izakaya_location
        self.current_location = home_location
        self.has_idea = has_idea
        self.schedule: List[Schedule] = []
        self.current_time = 0

    def generate_daily_schedule(self) -> List[Schedule]:
        """Creates a realistic daily schedule with transfers and late night behavior"""
        # Randomize work start time (most people start between 8-10)
        work_start = np.random.normal(9, 0.5)  # Normal distribution centered at 9
        work_start = max(min(work_start, 10), 8)  # Clamp between 8 and 10

        # Different types of evening schedules
        schedule_type = np.random.random()

        # Basic morning commute
        schedule = [
            Schedule("home", work_start, 0),
            Schedule("home_station", 0.3, work_start)
        ]

        # Morning transfers
        current_time = work_start
        for transfer_station in self.transfer_stations:
            current_time += 0.3
            schedule.append(Schedule("transfer", 0.2, current_time))

        # Arrive at work
        current_time += 0.3
        schedule.extend([
            Schedule("work_station", 0.3, current_time),
            Schedule("work", 8, current_time + 0.3)
        ])

        # Evening schedule variations
        work_end = current_time + 8.6  # Standard work duration

        if schedule_type < 0.4:  # 40% chance of regular schedule (go straight home)
            schedule.extend(self._generate_evening_commute(work_end))

        elif schedule_type < 0.75:  # 35% chance of izakaya but catch last train
            # Go to izakaya but leave by 23:00 to catch train
            izakaya_duration = np.random.uniform(1.5, 3)
            schedule.extend([
                Schedule("izakaya", izakaya_duration, work_end)
            ])
            schedule.extend(self._generate_evening_commute(work_end + izakaya_duration))

        elif schedule_type < 0.9:  # 15% chance of staying out late
            # Stay at izakaya until late, then take taxi home
            late_duration = np.random.uniform(4, 6)
            schedule.extend([
                Schedule("izakaya", late_duration, work_end),
                Schedule("home", 24 - (work_end + late_duration), work_end + late_duration)
            ])

        else:  # 10% chance of staying until first train
            # Stay at izakaya until very late, then take first train
            schedule.extend([
                Schedule("izakaya", 7, work_end),  # Stay until around 4-5 AM
                Schedule("work_station", 0.3, work_end + 7)
            ])
            # Morning transfers
            current_time = work_end + 7.3
            for transfer_station in reversed(self.transfer_stations):
                schedule.append(Schedule("transfer", 0.2, current_time))
                current_time += 0.3
            schedule.extend([
                Schedule("home_station", 0.3, current_time),
                Schedule("home", 24 - (current_time + 0.3), current_time + 0.3)
            ])

        self.schedule = schedule
        return schedule

    def _generate_evening_commute(self, start_time: float) -> List[Schedule]:
        """Generate a standard evening commute schedule"""
        schedule = [Schedule("work_station", 0.3, start_time)]
        current_time = start_time + 0.3

        # Evening transfers
        for transfer_station in reversed(self.transfer_stations):
            schedule.append(Schedule("transfer", 0.2, current_time))
            current_time += 0.3

        # Final leg home
        schedule.extend([
            Schedule("home_station", 0.3, current_time),
            Schedule("home", 24 - (current_time + 0.3), current_time + 0.3)
        ])

        return schedule

    def move(self, time: int) -> Tuple[float, float]:
        """Updates location based on schedule"""
        # Convert integer time to float for more precise scheduling
        time_float = float(time)

        for schedule in self.schedule:
            if schedule.start_time <= time_float < (schedule.start_time + schedule.duration):
                if schedule.location_type == "home":
                    self.current_location = self.home_location
                elif schedule.location_type == "work":
                    self.current_location = self.work_location
                elif schedule.location_type == "home_station":
                    self.current_location = self.home_station
                elif schedule.location_type == "work_station":
                    self.current_location = self.work_station
                elif schedule.location_type == "transfer":
                    # Only access transfer stations if they exist
                    if self.transfer_stations:
                        idx = self.schedule.index(schedule)
                        # Count previous transfer stations in schedule
                        transfer_idx = sum(1 for s in self.schedule[:idx]
                                         if s.location_type == "transfer")
                        # Ensure we don't exceed the transfer stations list
                        if 0 <= transfer_idx - 1 < len(self.transfer_stations):
                            self.current_location = self.transfer_stations[transfer_idx - 1]
                        else:
                            # Fallback to work station if index is out of range
                            self.current_location = self.work_station
                    else:
                        # Fallback to work station if no transfers
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
