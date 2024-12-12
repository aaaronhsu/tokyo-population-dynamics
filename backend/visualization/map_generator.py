from typing import List, Tuple, Dict
import folium
from folium.plugins import HeatMap, TimestampedGeoJson
import numpy as np
from datetime import datetime, timedelta

class TokyoMapGenerator:
    def __init__(
        self,
        center: Tuple[float, float] = (35.6762, 139.6503),  # Tokyo coordinates
        zoom_start: int = 11
    ):
        self.center = center
        self.zoom_start = zoom_start
        
    def create_base_map(self) -> folium.Map:
        """Create base Tokyo map"""
        return folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            tiles='cartodbpositron'  # Clean, modern style
        )
        
    def add_heatmap_layer(
        self,
        map_obj: folium.Map,
        points: List[Tuple[float, float, float]],
        name: str = "Idea Spread"
    ):
        """Add heatmap layer showing idea spread intensity"""
        HeatMap(
            points,
            name=name,
            min_opacity=0.3,
            max_val=1.0,
            radius=17,
            blur=15,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(map_obj)
        
    def add_location_markers(
        self,
        map_obj: folium.Map,
        locations: Dict[str, Tuple[float, float]],
        location_types: Dict[str, str]  # type to icon mapping
    ):
        """Add markers for significant locations"""
        for loc_id, coords in locations.items():
            loc_type = location_types.get(loc_id, 'info')
            folium.Marker(
                coords,
                popup=loc_id,
                icon=folium.Icon(color='red', icon=loc_type, prefix='fa')
            ).add_to(map_obj)
            
    def generate_timestamped_data(
        self,
        simulation_states: List[Dict],
        start_time: datetime
    ) -> Dict:
        """Generate GeoJSON for animated visualization"""
        features = []
        
        for i, state in enumerate(simulation_states):
            time = start_time + timedelta(hours=i)
            
            for agent_idx, (location, has_idea) in enumerate(state['agent_locations']):
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [location[1], location[0]]  # lon, lat
                    },
                    'properties': {
                        'time': time.isoformat(),
                        'icon': 'circle',
                        'popup': f'Agent {agent_idx}',
                        'style': {
                            'color': 'red' if has_idea else 'blue',
                            'radius': 5
                        }
                    }
                }
                features.append(feature)
                
        return {
            'type': 'FeatureCollection',
            'features': features
        }
        
    def create_animated_map(
        self,
        simulation_states: List[Dict],
        locations: Dict[str, Tuple[float, float]],
        save_path: str
    ):
        """Create and save an animated map of the simulation"""
        m = self.create_base_map()
        
        # Add base locations
        self.add_location_markers(
            m,
            locations,
            {
                'station': 'train',
                'izakaya': 'glass',
                'office': 'building',
                'home': 'home'
            }
        )
        
        # Add animated agent movements
        timestamped_data = self.generate_timestamped_data(
            simulation_states,
            datetime.now()
        )
        
        TimestampedGeoJson(
            timestamped_data,
            period='PT1H',  # 1 hour between frames
            duration='PT10M',  # Time each frame is displayed
            transition_time=200,  # Transition time between frames
            auto_play=True
        ).add_to(m)
        
        # Add final heatmap layer
        final_state = simulation_states[-1]
        heatmap_data = [
            [loc[0], loc[1], 1.0 if has_idea else 0.2]
            for loc, has_idea in final_state['agent_locations']
        ]
        self.add_heatmap_layer(m, heatmap_data, "Final State")
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(save_path)
