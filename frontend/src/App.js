import React from "react";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
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
      <SimulationPlayer />
    </ThemeProvider>
  );
}

export default App;
