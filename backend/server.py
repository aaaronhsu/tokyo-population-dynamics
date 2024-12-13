import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import numpy as np
import uuid
from models.simulation import TokyoSimulation
from visualization.video_generator import SimulationVideoGenerator, VideoConfig
from dataclasses import asdict

app = Flask(__name__)
CORS(app)

# Ensure the static directories exist
os.makedirs('static/simulations', exist_ok=True)

@app.route('/static/simulations/<path:filename>')
def serve_simulation(filename):
    """Serve generated simulation videos"""
    try:
        video_path = os.path.join('static/simulations', filename)
        if not os.path.exists(video_path):
            print(f"Video file not found at path: {video_path}")
            return jsonify({
                "status": "error",
                "message": "Video file not found"
            }), 404

        # Create response without adding Content-Length (Flask will handle this)
        response = send_file(
            video_path,
            mimetype='video/mp4'
        )

        # Add only necessary headers
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', 'no-cache')

        return response

    except Exception as e:
        print(f"Error serving video: {e}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/video-info/<path:filename>')
def get_video_info(filename):
    """Debug endpoint to get video file information"""
    try:
        video_path = os.path.join('static/simulations', filename)
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            return jsonify({
                "status": "success",
                "file_exists": True,
                "file_size": file_size,
                "file_path": video_path,
                "is_readable": os.access(video_path, os.R_OK)
            })
        return jsonify({
            "status": "error",
            "message": "File not found",
            "checked_path": video_path
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        # Get simulation parameters from request
        params = request.json or {}

        # Create simulation
        simulation = TokyoSimulation(
                    num_agents=params.get('num_agents', 1000),
                    city_bounds=((35.5, 139.4), (35.8, 139.9)),
                    simulation_params={
                        'transmission_rate': params.get('transmission_rate', 0.01),  # Reduced base rate
                        'initial_infected': params.get('initial_infected', 3),
                        'num_stations': params.get('num_stations', 7),
                        'izakaya_probability': params.get('izakaya_probability', 0.7),
                        'izakaya_capacity': params.get('izakaya_capacity', 50),
                        'train_commuter_ratio': params.get('train_commuter_ratio', 0.9),
                        'avg_transfers': params.get('avg_transfers', 2.3)
                    }
                )

        # Run simulation for one week (24 * 7 hours)
        states = []
        for _ in range(24 * 7):
            simulation.step()
            states.append(simulation.get_state())

        # Generate video
        video_config = VideoConfig(
            width=params.get('video_width', 1280),
            height=params.get('video_height', 720),
            fps=params.get('video_fps', 5)
        )

        video_generator = SimulationVideoGenerator(video_config)

        # Generate unique filename
        video_id = str(uuid.uuid4())
        video_path = f"static/simulations/{video_id}.mp4"

        success = video_generator.generate_video(states, video_path)

        if not success:
            return jsonify({
                "status": "error",
                "message": "Failed to generate video"
            }), 500

        return jsonify({
            "status": "success",
            "video_url": f"/static/simulations/{video_id}.mp4",
            "statistics": {
                "final_infection_rate": states[-1]['infection_rate'],
                "total_infected": states[-1]['infected_count'],
                "simulation_duration_days": 7
            }
        })

    except Exception as e:
        print(f"Error in simulate endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Add headers for video streaming
@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

if __name__ == '__main__':
    app.run(debug=True)
