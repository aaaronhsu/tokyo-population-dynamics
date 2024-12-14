# Tokyo Idea Propagation Simulation

[video](https://github.com/aaaronhsu/tokyo-population-dynamics/blob/1dda26edf2363ee521ae12ce276b6727eb76493a/backend/static/simulations/default.mp4)
[view here](https://tokyo-population-dynamics.onrender.com)

## Overview
This project simulates how ideas spread through Tokyo's urban landscape by modeling the city's unique social dynamics and transportation patterns. The simulation follows Tokyo residents through their daily routines, including commuting via the train network, working in office districts, and socializing in yokocho (traditional alley districts).

## Features
- Agent-based simulation of Tokyo residents
- Realistic daily schedules with:
  - Variable work hours
  - Complex train commute patterns with transfers
  - Social activities in yokocho districts
- Interactive parameter adjustment for:
  - Population size and initial idea carriers
  - Social space capacity and attendance
  - Transportation network usage
  - Idea transmission rates
- Real-time visualization showing idea spread across Tokyo
- Week-long simulation with day/night cycles

## Technical Stack
- **Frontend**: React with Material-UI
  - Interactive parameter controls
  - Video playback of simulation
  - Responsive design
- **Backend**: Flask (Python)
  - Agent-based simulation engine
  - Video generation with OpenCV
  - Geographical coordinate handling
- **Visualization**:
  - OpenCV for video generation
  - Folium for Tokyo map rendering
  - Custom visualization overlays

## Installation

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend Server
```bash
cd backend
flask run
```

### Start the Frontend Development Server
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Simulation Parameters

### Basic Parameters
- **Number of People**: Total population in the simulation
- **Idea Spread Rate**: Base probability of idea transmission during interactions
- **Initial People with Idea**: Number of people who start with the idea

### Yokocho Parameters
- **Probability of Visiting**: Likelihood of people visiting yokocho after work
- **Yokocho Capacity**: Maximum number of people in each yokocho location

### Transportation Parameters
- **Train Commuter Ratio**: Proportion of people using trains
- **Average Number of Transfers**: Complexity of train commute routes

## Implementation Details

### Agent Behavior
- Agents follow realistic daily schedules
- Movement patterns based on Tokyo's geography
- Different interaction probabilities based on location type
- Complex commute patterns with multiple train transfers

### Location Types
- Train stations (major Tokyo stations)
- Yokocho districts
- Office areas
- Residential neighborhoods

### Data Visualization
- Color-coded agents (green for idea carriers, red for others)
- Tokyo map background
- Time and date display
- Real-time statistics

## Project Structure
```
project/
├── backend/
│   ├── models/
│   │   ├── agent.py
│   │   ├── location.py
│   │   └── simulation.py
│   ├── visualization/
│   │   └── video_generator.py
│   └── server.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SimulationPlayer.js
│   │   │   └── SimulationDescription.js
│   │   └── App.js
│   └── package.json
└── README.md
```

## Future Improvements
- Add more sophisticated interaction models
- Include additional location types
- Implement multiple competing ideas
- Add historical data comparison
- Enhance visualization options
- Add time-of-day effects on transmission rates
- Include weather effects on movement patterns

## Acknowledgments
- Inspired by Tokyo's unique urban fabric and social dynamics
- Built with data from Tokyo's transportation and urban planning resources
- Uses real Tokyo station locations and neighborhood data

---
*Note: This simulation is a simplified model and should not be used for actual epidemiological or social network analysis.*
