from flask import Flask, jsonify
from flask_cors import CORS
import numpy as np
import folium
from folium.plugins import HeatMap  # Add this import

app = Flask(__name__)
CORS(app)

@app.route('/simulate', methods=['POST'])
def simulate():
    # Create a simple heat map
    map_tokyo = folium.Map(
        location=[35.6762, 139.6503],  # Tokyo coordinates
        zoom_start=10
    )

    # Generate random population data (replace with your simple model)
    # Generate points around Tokyo
    center_lat, center_lon = 35.6762, 139.6503
    num_points = 1000
    np.random.seed(42)

    # Generate random points with normal distribution
    lats = np.random.normal(center_lat, 0.1, num_points)
    lons = np.random.normal(center_lon, 0.1, num_points)
    intensities = np.random.random(num_points)

    # Combine the data
    data = [[lat, lon, int] for lat, lon, int in zip(lats, lons, intensities)]

    # Add heatmap to the map
    HeatMap(data).add_to(map_tokyo)  # Use HeatMap instead of Heatmap

    # Save as HTML
    map_tokyo.save('static/map.html')
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
