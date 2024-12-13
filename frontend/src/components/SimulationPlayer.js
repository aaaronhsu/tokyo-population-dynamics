import React, { useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Typography,
  TextField,
  Alert,
} from "@mui/material";
import axios from "axios";

const BACKEND_URL = "http://127.0.0.1:5000";

const DEFAULT_PARAMS = {
  num_agents: 1000,
  transmission_rate: 0.05,
  initial_infected: 3,
};

const SimulationPlayer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [videoUrl, setVideoUrl] = useState(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    setVideoUrl(null);
    try {
      const response = await axios.post(`${BACKEND_URL}/simulate`, params);
      if (response.data.status === "success") {
        // Instead of opening in a new tab, set the video URL
        setVideoUrl(`${BACKEND_URL}${response.data.video_url}`);
        setStats(response.data.statistics);
      }
    } catch (err) {
      console.error("Simulation error:", err);
      setError(
        err.response?.data?.message || "An error occurred during simulation",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleParamChange = (param) => (event) => {
    const value = parseFloat(event.target.value);
    if (!isNaN(value)) {
      setParams((prev) => ({
        ...prev,
        [param]: value,
      }));
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, margin: "0 auto", padding: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tokyo Population Dynamics Simulation
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Simulation Parameters
        </Typography>
        <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
          <TextField
            label="Number of Agents"
            type="number"
            value={params.num_agents}
            onChange={handleParamChange("num_agents")}
            sx={{ width: 200 }}
            inputProps={{ min: 1 }}
          />
          <TextField
            label="Transmission Rate"
            type="number"
            inputProps={{
              step: 0.01,
              min: 0,
              max: 1,
            }}
            value={params.transmission_rate}
            onChange={handleParamChange("transmission_rate")}
            sx={{ width: 200 }}
          />
          <TextField
            label="Initial Infected"
            type="number"
            value={params.initial_infected}
            onChange={handleParamChange("initial_infected")}
            sx={{ width: 200 }}
            inputProps={{ min: 1 }}
          />
        </Box>
        <Button
          variant="contained"
          onClick={runSimulation}
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={24} color="inherit" />
              <span>Generating Simulation...</span>
            </Box>
          ) : (
            "Run Simulation"
          )}
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {videoUrl && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ width: "100%", aspectRatio: "16/9", bgcolor: "black" }}>
            <video
              controls
              width="100%"
              height="100%"
              style={{ maxWidth: "100%", maxHeight: "100%" }}
            >
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </Box>
        </Paper>
      )}

      {stats && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Simulation Results
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Typography>
              Final Infection Rate:{" "}
              {(stats.final_infection_rate * 100).toFixed(1)}%
            </Typography>
            <Typography>Total Infected: {stats.total_infected}</Typography>
            {stats.simulation_duration_days && (
              <Typography>
                Simulation Duration: {stats.simulation_duration_days} days
              </Typography>
            )}
          </Box>
        </Paper>
      )}

      {videoUrl && (
        <Box sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            onClick={() => window.open(videoUrl, "_blank")}
          >
            Open Video in New Tab
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default SimulationPlayer;
