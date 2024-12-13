from typing import List, Dict
import cv2
import numpy as np
from dataclasses import dataclass
import folium
import os
import io
from PIL import Image

@dataclass
class VideoConfig:
    width: int = 1280
    height: int = 720
    fps: int = 5
    agent_radius: int = 2
    idea_color: tuple = (0, 255, 0)  # Green for agents with idea
    no_idea_color: tuple = (50, 50, 255)  # Red for agents without idea
    background_color: tuple = (25, 25, 25)  # Dark background for text overlay

class SimulationVideoGenerator:
    # Class variable to store the cached map
    _cached_base_frame = None

    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        self.base_frame = self._get_base_frame()

    def _get_base_frame(self) -> np.ndarray:
        """Get the base frame, either from cache or create new"""
        if SimulationVideoGenerator._cached_base_frame is None:
            print("Generating new Tokyo map...")
            SimulationVideoGenerator._cached_base_frame = self._create_base_frame()

            # Save the base frame for verification if needed
            os.makedirs('static', exist_ok=True)
            cv2.imwrite('static/base_map.png', SimulationVideoGenerator._cached_base_frame)
            print("Base map cached and saved to static/base_map.png")

        # Return a copy of the cached frame
        return SimulationVideoGenerator._cached_base_frame.copy()

    def _create_base_frame(self) -> np.ndarray:
        """Create the base Tokyo map frame"""
        try:
            # Create Folium map
            m = folium.Map(
                location=[35.65, 139.65],  # Tokyo center
                zoom_start=11,
                tiles='CartoDB dark_matter',
                width=self.config.width,
                height=self.config.height
            )

            # Get PNG data
            img_data = m._to_png(5)

            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))

            # Convert PIL Image to numpy array
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Resize to match video dimensions
            frame = cv2.resize(frame, (self.config.width, self.config.height))

            return frame

        except Exception as e:
            print(f"Error creating base frame: {str(e)}")
            # Return a black frame as fallback
            return np.full(
                (self.config.height, self.config.width, 3),
                self.config.background_color,
                dtype=np.uint8
            )

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
        # Start with a copy of the base frame
        frame = self.base_frame.copy()

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
        overlay = frame.copy()
        cv2.rectangle(overlay, (30, 20), (320, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Calculate current date and time
        hour = state['time'] % 24
        day = state['time'] // 24 + 1  # Add 1 to start from day 1

        # Add text
        cv2.putText(
            frame,
            f"Day {day}, {hour:02d}:00",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Idea Adoption Rate: {state['infection_rate']:.1%}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        return frame

    def generate_video(
        self,
        simulation_states: List[Dict],
        output_path: str
    ) -> bool:
        """Generate video from simulation states"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
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
