import React from 'react';
import RoutesList from './components/RoutesList'; // Import the component
import './App.css'; // Import your stylesheet for better styling

function App() {
  return (
    <div className="app-container">
      <header className="header">
        <h1>Toronto Transit Routes</h1>
        <p>Get live updates about bus routes and arrival times</p>
      </header>
      <main className="main-content">
        <RoutesList />
      </main>
      <footer className="footer">
        <p>&copy; 2025 Toronto Transit App | All Rights Reserved</p>
      </footer>
    </div>
  );
}

export default App;
