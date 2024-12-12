import sys
import os
# Add the backend directory to the Python path
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
        print('test')
        params = request.json or {}

        # Create simulation with default values if not provided
        simulation = TokyoSimulation(
            num_agents=params.get('num_agents', 1000),
            city_bounds=((35.5, 139.4), (35.8, 139.9)),  # Tokyo bounds
            simulation_params={
                'transmission_rate': params.get('transmission_rate', 0.3),
                'initial_infected': params.get('initial_infected', 5),
                'num_stations': params.get('num_stations', 30),
                'num_izakayas': params.get('num_izakayas', 50),
                'station_capacity': params.get('station_capacity', 1000),
                'izakaya_capacity': params.get('izakaya_capacity', 50),
                'work_capacity': params.get('work_capacity', 200)
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
            fps=params.get('video_fps', 30),
            background_color=params.get('background_color', (25, 25, 25)),
            agent_radius=params.get('agent_radius', 3),
            idea_color=params.get('idea_color', (0, 255, 0)),
            no_idea_color=params.get('no_idea_color', (50, 50, 255))
        )

        video_generator = SimulationVideoGenerator(video_config)

        # Generate unique filename for the video
        video_id = str(uuid.uuid4())
        video_path = f"static/simulations/{video_id}.mp4"

        # Generate the video
        success = video_generator.generate_video(states, video_path)

        if not success:
            return jsonify({
                "status": "error",
                "message": "Failed to generate video"
            }), 500

        # Calculate additional statistics
        hourly_rates = [state['infection_rate'] for state in states]

        # Prepare response
        response_data = {
            "status": "success",
            "video_url": f"/static/simulations/{video_id}.mp4",
            "statistics": {
                "final_infection_rate": states[-1]['infection_rate'],
                "total_infected": states[-1]['infected_count'],
                "hourly_rates": hourly_rates,
                "peak_infection_rate": max(hourly_rates),
                "simulation_duration_hours": len(states),
                "total_agents": simulation.num_agents,
                "simulation_parameters": {
                    "transmission_rate": simulation.params['transmission_rate'],
                    "initial_infected": simulation.params['initial_infected'],
                    "num_stations": simulation.params['num_stations'],
                    "num_izakayas": simulation.params['num_izakayas']
                }
            },
            "video_config": asdict(video_config)
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/static/simulations/<path:filename>')
def serve_simulation(filename):
    """Serve generated simulation videos"""
    return send_from_directory('static/simulations', filename)

@app.route('/cleanup', methods=['POST'])
def cleanup_old_simulations():
    """Clean up old simulation videos to free up space"""
    try:
        # Keep only the 10 most recent files
        simulation_dir = 'static/simulations'
        files = os.listdir(simulation_dir)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(simulation_dir, x)))

        # Remove all but the 10 most recent files
        files_to_delete = files[:-10] if len(files) > 10 else []

        for file in files_to_delete:
            os.remove(os.path.join(simulation_dir, file))

        return jsonify({
            "status": "success",
            "message": f"Cleaned up {len(files_to_delete)} old simulation files"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/simulation_params')
def get_default_params():
    """Return default simulation parameters"""
    return jsonify({
        "simulation_parameters": {
            "num_agents": 1000,
            "transmission_rate": 0.3,
            "initial_infected": 5,
            "num_stations": 30,
            "num_izakayas": 50,
            "station_capacity": 1000,
            "izakaya_capacity": 50,
            "work_capacity": 200,
            "simulation_hours": 24
        },
        "video_parameters": {
            "width": 1280,
            "height": 720,
            "fps": 30,
            "background_color": [25, 25, 25],
            "agent_radius": 3,
            "idea_color": [0, 255, 0],
            "no_idea_color": [50, 50, 255]
        }
    })

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',  # Makes the server externally visible
        port=5000
    )
