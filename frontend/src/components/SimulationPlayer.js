import React, { useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Typography,
  TextField,
  Alert,
  Slider,
  InputLabel,
  FormControl,
} from "@mui/material";
import axios from "axios";

const BACKEND_URL = "/api";

const DEFAULT_PARAMS = {
  num_agents: 3000,
  transmission_rate: 0.075,
  initial_infected: 3,
  izakaya_probability: 0.6, // 70% of people go to izakaya
  izakaya_capacity: 15, // seats per izakaya
  train_commuter_ratio: 0.6, // 90% take train to work
  avg_transfers: 2.3, // average number of transfers
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

  // Handler for slider changes
  const handleSliderChange = (param) => (event, newValue) => {
    setParams((prev) => ({
      ...prev,
      [param]: newValue,
    }));
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

        {/* Basic Parameters */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" gutterBottom>
            Basic Parameters
          </Typography>
          <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
            <TextField
              label="Number of Office Workers"
              type="number"
              value={params.num_agents}
              onChange={handleParamChange("num_agents")}
              sx={{ width: 200 }}
              inputProps={{ min: 1 }}
            />
            <TextField
              label="Idea Virality"
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
              label="Number of Initial Idea Spreaders"
              type="number"
              value={params.initial_infected}
              onChange={handleParamChange("initial_infected")}
              sx={{ width: 200 }}
              inputProps={{ min: 1 }}
            />
          </Box>
        </Box>

        {/* Izakaya Parameters */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" gutterBottom>
            Yokocho Parameters
          </Typography>
          <Box sx={{ width: "100%", mb: 2 }}>
            <Typography gutterBottom>
              Probability of Going to Yokocho:{" "}
              {(params.izakaya_probability * 100).toFixed(0)}%
            </Typography>
            <Slider
              value={params.izakaya_probability}
              onChange={handleSliderChange("izakaya_probability")}
              min={0}
              max={1}
              step={0.1}
              marks
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
            />
          </Box>
          <TextField
            label="Yokocho Capacity"
            type="number"
            value={params.izakaya_capacity}
            onChange={handleParamChange("izakaya_capacity")}
            sx={{ width: 200 }}
            inputProps={{ min: 1 }}
          />
        </Box>

        {/* Transportation Parameters */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle1" gutterBottom>
            Transportation Parameters
          </Typography>
          <Box sx={{ width: "100%", mb: 2 }}>
            <Typography gutterBottom>
              Train Commuter Ratio:{" "}
              {(params.train_commuter_ratio * 100).toFixed(0)}%
            </Typography>
            <Slider
              value={params.train_commuter_ratio}
              onChange={handleSliderChange("train_commuter_ratio")}
              min={0}
              max={1}
              step={0.1}
              marks
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
            />
          </Box>
          <Box sx={{ width: "100%", mb: 2 }}>
            <Typography gutterBottom>
              Average Number of Transfers: {params.avg_transfers}
            </Typography>
            <Slider
              value={params.avg_transfers}
              onChange={handleSliderChange("avg_transfers")}
              min={0}
              max={5}
              step={0.1}
              marks
              valueLabelDisplay="auto"
            />
          </Box>
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
              Final Idea Adoption Rate (%):{" "}
              {(stats.final_infection_rate * 100).toFixed(1)}%
            </Typography>
            <Typography>
              Total People With Idea: {stats.total_infected}
            </Typography>
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
