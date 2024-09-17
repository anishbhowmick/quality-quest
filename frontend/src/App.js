import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import OcrBarcode from './components/OcrBarcode';
import ObjectDetection from './components/ObjectDetection';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ocr-barcode" element={<OcrBarcode />} />
        <Route path="/fruit-detection" element={<ObjectDetection />} />
      </Routes>
    </Router>
  );
}

export default App;
