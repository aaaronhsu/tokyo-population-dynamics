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
        """Get the base frame from cached file or create new"""
        cached_map_path = os.path.join('static', 'base_map.png')

        if os.path.exists(cached_map_path):
            print("Loading cached Tokyo map...")
            frame = cv2.imread(cached_map_path)
            if frame is not None:
                frame = cv2.resize(frame, (self.config.width, self.config.height))
                print(f"Successfully loaded cached map with shape: {frame.shape}")
                return frame

        print("Cached map not found or invalid, generating new map...")
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

            # Save the generated map for future use
            os.makedirs('static', exist_ok=True)
            cv2.imwrite(cached_map_path, frame)
            print(f"Generated and cached new map with shape: {frame.shape}")

            return frame

        except Exception as e:
            print(f"Error creating base frame: {str(e)}")
            # Return a black frame as fallback
            return np.full(
                (self.config.height, self.config.width, 3),
                self.config.background_color,
                dtype=np.uint8
            )


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
            print(f"Starting video generation to: {output_path}")

            # Try different codec options
            codecs = [
                ('mp4v', '.mp4'),
                ('avc1', '.mp4'),
                ('X264', '.mp4'),
                ('XVID', '.avi'),
            ]

            for codec, ext in codecs:
                try:
                    # Update output path with correct extension
                    current_output = output_path.rsplit('.', 1)[0] + ext

                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    out = cv2.VideoWriter(
                        current_output,
                        fourcc,
                        self.config.fps,
                        (self.config.width, self.config.height)
                    )

                    if out.isOpened():
                        print(f"Successfully initialized VideoWriter with codec: {codec}")
                        break
                except Exception as e:
                    print(f"Failed to initialize codec {codec}: {e}")
                    continue
            else:
                print("Failed to initialize any video codec")
                return False

            print(f"Processing {len(simulation_states)} frames")
            for i, state in enumerate(simulation_states):
                frame = self.create_frame(state)
                out.write(frame)
                if i % 50 == 0:
                    print(f"Processed frame {i}/{len(simulation_states)}")

            out.release()

            # Verify file was created
            if os.path.exists(current_output):
                file_size = os.path.getsize(current_output)
                print(f"Video generated successfully. File size: {file_size} bytes")

                # If the output path is different from the original, rename it
                if current_output != output_path:
                    os.rename(current_output, output_path)

                return True
            else:
                print("Video file not found after generation")
                return False

        except Exception as e:
            print(f"Error generating video: {e}")
            import traceback
            print(traceback.format_exc())
            return False
