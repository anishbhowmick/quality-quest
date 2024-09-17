import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="Home">
      <h1>Welcome to the Detection App</h1>
      <div className="home-buttons">
        <button onClick={() => navigate('/ocr-barcode')}>OCR Barcode Detection</button>
        <button onClick={() => navigate('/fruit-detection')}>Fruit Detection</button>
      </div>
    </div>
  );
}

export default Home;