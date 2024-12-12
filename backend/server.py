import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask import Flask, jsonify, request, send_from_directory
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
                'transmission_rate': params.get('transmission_rate', 0.05),  # Reduced from 0.3
                'initial_infected': params.get('initial_infected', 3),  # Reduced from 5
                'num_stations': params.get('num_stations', 7)
            }
        )

        # Run simulation and collect states
        states = []
        for _ in range(params.get('simulation_hours', 24)):
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
                "total_infected": states[-1]['infected_count']
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/static/simulations/<path:filename>')
def serve_simulation(filename):
    """Serve generated simulation videos"""
    return send_from_directory('static/simulations', filename)

if __name__ == '__main__':
    app.run(debug=True)
