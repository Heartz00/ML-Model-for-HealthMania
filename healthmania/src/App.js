import React from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Use updated syntax
import HomePage from "./components/HomePage"; // Import your existing homepage
import GlucoSensePage from "./components/GlucoSense"; // Import your GlucoSensePage



function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} /> {/* Home page route */}
        <Route path="/glucosense" element={<GlucoSensePage />} /> {/* GlucoSense page */}
      </Routes>
    </Router>
  );
}

export default App;
