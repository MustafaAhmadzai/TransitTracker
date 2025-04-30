import React, { useState, useEffect } from "react";
import axios from "axios";
import './RoutesList.css'; // Make sure the path is correct


const RoutesList = () => {
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState("");
  const [directions, setDirections] = useState([]);
  const [selectedDirection, setSelectedDirection] = useState("");
  const [stops, setStops] = useState([]);
  const [selectedStop, setSelectedStop] = useState("");
  const [predictedMinutes, setPredictedMinutes] = useState(null);

  useEffect(() => {
    // get routes on bootup
    axios
      .get("http://localhost:8000/routes")
      .then((response) => {
        console.log("Routes API Response:", response.data);
        setRoutes(response.data.routes);
      })
      .catch((error) => console.error("Error fetching routes:", error));
  }, []);

  const handleRouteChange = (event) => {
    const routeTag = event.target.value;
    setSelectedRoute(routeTag);
    setSelectedDirection("");
    setDirections([]);
    setStops([]);

    if (routeTag) {
      // get directions after route selection
      axios
        .get(`http://localhost:8000/route_config/${routeTag}`)
        .then((response) => {
          console.log("Route Config API Response:", response.data);
          setDirections(response.data.directions);
        })
        .catch((error) => console.error("Error fetching directions:", error));
    }
  };

  const handleDirectionChange = (event) => {
    const directionTitle = event.target.value;
    setSelectedDirection(directionTitle);

    // Find stops for the selected direction
    const selectedDir = directions.find(dir => dir.directionTitle === directionTitle);
    setStops(selectedDir ? selectedDir.stops : []);
  };

  const handleStopChange = (event) => {
    setSelectedStop(event.target.value);
  };

  const handleConfirmSelection = () => {
    console.log("Fetching data for:", selectedRoute, selectedDirection, selectedStop);
  
    axios.get(`http://localhost:8000/predictions/${selectedStop}/${selectedRoute}`)
    .then(response => {
      console.log("Schedule Data:", response.data);
      
      response.data.predictions.forEach(prediction => {
        console.log("Prediction Direction:", prediction.direction);
      });
  
      console.log("Selected Direction:", selectedDirection);
  
      // Find the prediction for the selected direction
      const matchingPrediction = response.data.predictions.find(prediction => 
        prediction.direction === selectedDirection
      );
  
      if (matchingPrediction) {
        console.log("Matching Prediction Found:", matchingPrediction);
        setPredictedMinutes(matchingPrediction.minutes)
      } else {
        console.log("No matching prediction found.");
        setPredictedMinutes("N/A")
      }
    })
    .catch(error => console.error("Error fetching schedule:", error));
  
  };
  


  return (
    <div className="route-planner-container">
      <h2>Route Planner</h2>

      {/* Route Dropdown */}
      <label>Select a Route:</label>
      <select value={selectedRoute} onChange={handleRouteChange}>
        <option value="">-- Select --</option>
        {routes.map((route) => (
          <option key={route.route_tag} value={route.route_tag}>
            {route.route_name} ({route.route_tag})
          </option>
        ))}
      </select>

      {/* Direction Dropdown (shows up after selecting a route) */}
      {directions.length > 0 && (
        <>
          <label>Select a Direction:</label>
          <select value={selectedDirection} onChange={handleDirectionChange}>
            <option value="">-- Select --</option>
            {directions.map((direction) => (
              <option key={direction.directionTitle} value={direction.directionTitle}>
                {direction.directionTitle}
              </option>
            ))}
          </select>
        </>
      )}

      {/* Stop Dropdown (shows up after selecting a direction) */}
      {stops.length > 0 && (
        <>
          <label>Select a Stop:</label>
          <select value={selectedStop} onChange={handleStopChange}>
            <option value="">-- Select --</option>
            {stops.map((stop) => (
              <option key={stop.stopId} value={stop.stopId}>
                {stop.stopName}
              </option>
            ))}
          </select>
        </>
      )}

      {/* Confirm Button */}
      <button
      className="confirm-button"
      onClick={handleConfirmSelection}
      disabled={!selectedRoute || !selectedDirection || !selectedStop}
        >
      Confirm Selection
        </button>

        {predictedMinutes && (
  <div>
    <h3>Next Bus in: {predictedMinutes} minutes</h3>
  </div>
)}

    </div>
  );
};

export default RoutesList;
