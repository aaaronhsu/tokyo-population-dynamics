from typing import List, Dict
import cv2
import numpy as np
from dataclasses import dataclass
import folium
import os
import io
from PIL import Image
from datetime import datetime, timedelta

@dataclass
class VideoConfig:
    width: int = 1280
    height: int = 720
    fps: int = 5
    agent_radius: int = 2
    idea_color: tuple = (0, 255, 0)
    no_idea_color: tuple = (50, 50, 255)
    background_color: tuple = (25, 25, 25)

class SimulationVideoGenerator:
    def __init__(self, config: VideoConfig = None):
        self.config = config or VideoConfig()
        self.start_date = datetime(2024, 1, 1)
        try:
            self.base_frame = self._create_base_frame()
            # Save base frame for verification
            os.makedirs('static', exist_ok=True)
            cv2.imwrite('static/base_map.png', self.base_frame)
            print("Base map saved to static/base_map.png")
        except Exception as e:
            print(f"Error in initialization: {str(e)}")
            print(traceback.format_exc())
            raise

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

            # Save map to HTML first for debugging
            os.makedirs('static', exist_ok=True)
            m.save('static/debug_map.html')
            print("Debug map HTML saved")

            # Get PNG data
            img_data = m._to_png(5)
            print("PNG data received from Folium")

            # Save raw PNG data for debugging
            with open('static/debug_raw_map.png', 'wb') as f:
                f.write(img_data)
            print("Raw PNG data saved")

            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            print(f"PIL Image size: {img.size}")

            # Convert PIL Image to numpy array
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            print(f"Numpy array shape: {frame.shape}")

            # Resize to match video dimensions
            frame = cv2.resize(frame, (self.config.width, self.config.height))
            print(f"Final frame shape: {frame.shape}")

            return frame

        except Exception as e:
            print(f"Error creating base frame: {str(e)}")
            print(traceback.format_exc())
            raise

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
        # Start with the base map frame
        frame = self.base_frame.copy()

        # Calculate current date and time
        total_hours = state['time']
        current_datetime = self.start_date + timedelta(hours=total_hours)
        day_of_week = current_datetime.strftime('%A')

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

        # Add stats overlay with background
        overlay = frame.copy()
        cv2.rectangle(overlay, (30, 20), (400, 140), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Add text
        cv2.putText(
            frame,
            f"{day_of_week} {current_datetime.strftime('%Y-%m-%d')}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Time: {current_datetime.strftime('%H:00')}",
            (50, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Infection Rate: {state['infection_rate']:.1%}",
            (50, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        return frame

    def generate_video(self, simulation_states: List[Dict], output_path: str) -> bool:
        """Generate video from simulation states"""
        try:
            print(f"Starting video generation to: {output_path}")

            # Change codec to 'avc1' which is more web-friendly
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Changed from 'mp4v'
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                self.config.fps,
                (self.config.width, self.config.height)
            )

            if not out.isOpened():
                print("Failed to open VideoWriter")
                # Try fallback codec
                fourcc = cv2.VideoWriter_fourcc(*'H264')
                out = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    self.config.fps,
                    (self.config.width, self.config.height)
                )
                if not out.isOpened():
                    print("Failed to open VideoWriter with fallback codec")
                    return False

            print(f"Processing {len(simulation_states)} frames")
            for i, state in enumerate(simulation_states):
                frame = self.create_frame(state)
                out.write(frame)
                if i % 50 == 0:
                    print(f"Processed frame {i}/{len(simulation_states)}")

            out.release()

            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"Video generated successfully. File size: {file_size} bytes")

                # Try to convert the video to a more web-friendly format using ffmpeg
                try:
                    import subprocess
                    web_output_path = output_path.replace('.mp4', '_web.mp4')
                    subprocess.run([
                        'ffmpeg', '-i', output_path,
                        '-vcodec', 'libx264',
                        '-acodec', 'aac',
                        web_output_path
                    ], check=True)

                    # If conversion successful, replace original file
                    if os.path.exists(web_output_path):
                        os.replace(web_output_path, output_path)
                        print("Successfully converted video to web-friendly format")

                except Exception as e:
                    print(f"Failed to convert video format: {e}")
                    # Continue with original file if conversion fails

                return True
            else:
                print("Video file not found after generation")
                return False

        except Exception as e:
            print(f"Error generating video: {e}")
            print(traceback.format_exc())
            return False
