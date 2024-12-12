from typing import List, Dict
import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class VideoConfig:
    width: int = 1280
    height: int = 720
    fps: int = 30
    background_color: tuple = (25, 25, 25)  # Dark background
    agent_radius: int = 3
    idea_color: tuple = (0, 255, 0)  # Green for agents with idea
    no_idea_color: tuple = (50, 50, 255)  # Red for agents without idea

class SimulationVideoGenerator:
    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        
    def _tokyo_coords_to_pixel(
        self,
        lat: float,
        lon: float,
        bounds: tuple = ((35.5, 139.4), (35.8, 139.9))  # Tokyo bounds
    ) -> tuple:
        """Convert geo coordinates to pixel coordinates"""
        min_lat, min_lon = bounds[0]
        max_lat, max_lon = bounds[1]
        
        # Normalize coordinates to [0,1] range
        x = (lon - min_lon) / (max_lon - min_lon)
        y = (lat - min_lat) / (max_lat - min_lat)
        
        # Convert to pixel coordinates
        pixel_x = int(x * (self.config.width - 20) + 10)  # 10px padding
        pixel_y = int((1-y) * (self.config.height - 20) + 10)  # Flip Y axis
        
        return (pixel_x, pixel_y)

    def create_frame(self, state: Dict) -> np.ndarray:
        """Create a single frame showing agent positions and idea spread"""
        # Create blank frame
        frame = np.full(
            (self.config.height, self.config.width, 3),
            self.config.background_color,
            dtype=np.uint8
        )
        
        # Draw agents
        for location, has_idea in state['agent_locations']:
            pixel_pos = self._tokyo_coords_to_pixel(location[0], location[1])
            color = self.config.idea_color if has_idea else self.config.no_idea_color
            cv2.circle(
                frame,
                pixel_pos,
                self.config.agent_radius,
                color,
                -1  # Filled circle
            )
        
        # Add stats overlay
        cv2.putText(
            frame,
            f"Time: {state['time']:02d}:00",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        cv2.putText(
            frame,
            f"Infection Rate: {state['infection_rate']:.1%}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        # Draw location markers (stations, izakayas, etc.)
        # You can add this if needed
        
        return frame

    def generate_video(
        self,
        simulation_states: List[Dict],
        output_path: str
    ) -> bool:
        """Generate video from simulation states"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                self.config.fps,
                (self.config.width, self.config.height)
            )
            
            for state in simulation_states:
                frame = self.create_frame(state)
                out.write(frame)
                
            out.release()
            return True
            
        except Exception as e:
            print(f"Error generating video: {e}")
            return False
