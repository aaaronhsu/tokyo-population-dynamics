import { useState } from "react";

function App() {
  const [showMap, setShowMap] = useState(false);

  const handleSimulate = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/simulate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        setShowMap(true);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div>
      <button onClick={handleSimulate}>Run Simulation</button>
      {showMap && (
        <iframe
          src="http://127.0.0.1:5000/static/map.html"
          width="800"
          height="600"
          frameBorder="0"
        />
      )}
    </div>
  );
}

export default App;
