from typing import Tuple, List, Dict

# Major residential neighborhoods in Tokyo with approximate coordinates
TOKYO_NEIGHBORHOODS = {
    "Setagaya": {
        "center": (35.6464, 139.6533),
        "population_weight": 0.20,  # Largest ward
        "radius": 0.03
    },
    "Nerima": {
        "center": (35.7357, 139.6516),
        "population_weight": 0.15,
        "radius": 0.025
    },
    "Ota": {
        "center": (35.5613, 139.7166),
        "population_weight": 0.15,
        "radius": 0.025
    },
    "Suginami": {
        "center": (35.6994, 139.6364),
        "population_weight": 0.12,
        "radius": 0.02
    },
    "Adachi": {
        "center": (35.7750, 139.8047),
        "population_weight": 0.15,
        "radius": 0.025
    },
    "Koto": {
        "center": (35.6729, 139.8269),
        "population_weight": 0.12,
        "radius": 0.02
    },
    "Minato": {
        "center": (35.6581, 139.7514),
        "population_weight": 0.11,
        "radius": 0.02
    }
}

def generate_home_location(neighborhood: Dict) -> Tuple[float, float]:
    """Generate a random location within a neighborhood's radius"""
    import numpy as np

    center = neighborhood["center"]
    radius = neighborhood["radius"]

    # Generate random angle and radius (using sqrt for uniform distribution)
    angle = np.random.uniform(0, 2 * np.pi)
    r = radius * np.sqrt(np.random.uniform(0, 1))

    # Convert to cartesian coordinates
    lat_offset = r * np.cos(angle)
    lon_offset = r * np.sin(angle)

    return (
        center[0] + lat_offset,
        center[1] + lon_offset
    )

def select_random_neighborhood() -> Dict:
    """Select a random neighborhood based on population weights"""
    import numpy as np

    neighborhoods = list(TOKYO_NEIGHBORHOODS.values())
    weights = [n["population_weight"] for n in neighborhoods]

    return np.random.choice(neighborhoods, p=weights)
