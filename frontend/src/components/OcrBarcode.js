import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './OcrBarcode.css';

function OcrBarcode() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [imagePreviews, setImagePreviews] = useState([]);

  const onFileChange = (event) => {
    const files = event.target.files;
    setSelectedFiles(files);
    setResults([]);
    // Generate image previews
    const previews = Array.from(files).map(file => URL.createObjectURL(file));
    setImagePreviews(previews);
  };

  const onFileUploadSingleProduct = () => {
    if (selectedFiles.length !== 1) {
      alert("Please upload exactly one image for single product processing");
      return;
    }

    setLoading(true);
    setResults([]);

    const formData = new FormData();
    formData.append("productImage", selectedFiles[0]);

    axios.post('http://localhost:5000/upload-single-product', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then((response) => {
      setResults([response.data]);
      setLoading(false);
    }).catch((error) => {
      console.error("There was an error uploading the image!", error);
      setLoading(false);
    });
  };

  const onFileUploadMultipleProducts = () => {
    if (selectedFiles.length === 0) {
      alert("Please upload images first");
      return;
    }

    setLoading(true);
    setResults([]);

    const formData = new FormData();
    Array.from(selectedFiles).forEach(file => {
      formData.append("productImages", file);
    });

    axios.post('http://localhost:5000/upload-multiple-products', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then((response) => {
      setResults(response.data);
      setLoading(false);
    }).catch((error) => {
      console.error("There was an error uploading the images!", error);
      setLoading(false);
    });
  };

  return (
    <div className="OcrBarcode">
      <Link to="/" className="home-button">Home</Link>
      <h1>OCR Barcode Detection</h1>
      <input type="file" multiple onChange={onFileChange} />
      <div className="button-group">
        <button onClick={onFileUploadSingleProduct}>Upload and Process Single Product</button>
        <button onClick={onFileUploadMultipleProducts}>Upload and Process Multiple Products</button>
      </div>

      {loading && <p>Processing images...</p>}

      {imagePreviews.length > 0 && (
        <div className="previews">
          <h2>Image Previews</h2>
          {imagePreviews.map((src, index) => (
            <div key={index} className="preview-item">
              <img src={src} alt={`Preview ${index + 1}`} />
              {results[index] && (
                <div className="result">
                  <h3>{results[index].fileName}</h3>
                  <p><strong>Barcode Data:</strong> {results[index].barcodeData}</p>
                  <p><strong>Manufacturing and Expiry Dates:</strong> {results[index].manufacturingExpiryDates}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default OcrBarcode;
