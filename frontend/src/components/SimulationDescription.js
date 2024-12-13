import React from "react";
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  Settings as SettingsIcon,
  Train as TrainIcon,
  LocalBar as BarIcon,
  People as PeopleIcon,
} from "@mui/icons-material";

const SimulationDescription = () => (
  <Paper sx={{ p: 3, mb: 3, backgroundColor: "rgba(0, 0, 0, 0.1)" }}>
    <Typography variant="h6" gutterBottom>
      About This Simulation
    </Typography>

    <Typography variant="body1" paragraph>
      This simulation explores how ideas spread through Tokyo's urban landscape,
      modeling the city's unique social dynamics and transportation patterns.
      The simulation follows Tokyo residents as they move through their daily
      routines: commuting via the extensive train network (with multiple
      transfers), working in office districts, and socializing in yokocho
      (traditional alley districts filled with small bars and eateries).
    </Typography>

    <Typography variant="body1" sx={{ mb: 2 }}>
      You can adjust various parameters to explore different scenarios:
    </Typography>

    <List sx={{ mb: 2 }}>
      <ListItem>
        <ListItemIcon>
          <PeopleIcon />
        </ListItemIcon>
        <ListItemText
          primary="Population and Ideas"
          secondary="Set the initial number of people who have an idea and how easily it spreads through social interactions"
        />
      </ListItem>

      <ListItem>
        <ListItemIcon>
          <BarIcon />
        </ListItemIcon>
        <ListItemText
          primary="Social Spaces"
          secondary="Modify how many people visit yokocho after work and the capacity of these social gathering spaces"
        />
      </ListItem>

      <ListItem>
        <ListItemIcon>
          <TrainIcon />
        </ListItemIcon>
        <ListItemText
          primary="Transportation Network"
          secondary="Adjust the proportion of train commuters and the complexity of their routes through Tokyo's rail system"
        />
      </ListItem>

      <ListItem>
        <ListItemIcon>
          <SettingsIcon />
        </ListItemIcon>
        <ListItemText
          primary="Simulation Controls"
          secondary="Fine-tune parameters like idea spread rates and observe how they affect the propagation patterns"
        />
      </ListItem>
    </List>

    <Typography variant="body1" paragraph>
      The simulation generates a video visualization showing how the idea
      spreads across Tokyo over the course of a week, with green dots
      representing people who have encountered the idea and red dots
      representing those who haven't yet. Watch how ideas spread more rapidly in
      social spaces and through the transit system during rush hours!
    </Typography>

    <Typography
      variant="body1"
      sx={{
        backgroundColor: "rgba(0, 0, 0, 0.2)",
        p: 2,
        borderRadius: 1,
        fontStyle: "italic",
      }}
    >
      Note: This simulation is inspired by Tokyo's unique urban fabric, where
      millions of people navigate through an intricate network of trains and
      social spaces daily, creating perfect conditions for the natural spread of
      ideas.
    </Typography>
  </Paper>
);

export default SimulationDescription;
