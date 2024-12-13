import { CssBaseline, Box, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import SimulationDescription from "./components/SimulationDescription";
import SimulationPlayer from "./components/SimulationPlayer";

const theme = createTheme({
  palette: {
    mode: "dark",
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ maxWidth: 1200, margin: "0 auto", padding: 3 }}>
        <Typography variant="h3" gutterBottom align="center" sx={{ mb: 4 }}>
          Tokyo Idea Propagation Simulation
        </Typography>
        <SimulationDescription />
        <SimulationPlayer />
      </Box>
    </ThemeProvider>
  );
}

export default App;
