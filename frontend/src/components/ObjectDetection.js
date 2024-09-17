import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import './ObjectDetection.css';

function ObjectDetection() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [model, setModel] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [facingMode, setFacingMode] = useState('environment'); // 'user' or 'environment'
  const [stream, setStream] = useState(null);

  const publishableKey = process.env.REACT_APP_ROBOFLOW_KEY;
  const modelName = process.env.REACT_APP_ROBOFLOW_MODEL;
  const modelVersion = process.env.REACT_APP_ROBOFLOW_VERSION;

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://cdn.roboflow.com/0.2.26/roboflow.js';
    script.async = true;
    script.onload = () => {
      loadModel();
    };
    document.body.appendChild(script);

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const loadModel = () => {
    window.roboflow
      .auth({
        publishable_key: publishableKey,
      })
      .load({
        model: modelName,
        version: modelVersion,
      })
      .then((loadedModel) => {
        setModel(loadedModel);
        console.log('Model loaded');
      })
      .catch((error) => {
        console.error('Error loading the model: ', error);
      });
  };

  const startVideo = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }

    navigator.mediaDevices
      .getUserMedia({ 
        video: { facingMode: facingMode },
        audio: false 
      })
      .then((currentStream) => {
        videoRef.current.srcObject = currentStream;
        videoRef.current.play();
        setStream(currentStream);
        detectFromVideoFrame();
      })
      .catch((err) => {
        console.error('Error accessing the camera: ', err);
      });
  };

  const detectFromVideoFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const renderFrame = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA && model) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        model
          .detect(canvas)
          .then((predictions) => {
            setPredictions(predictions);
            drawPredictions(predictions, ctx);
          })
          .catch((err) => {
            console.error('Detection error: ', err);
          });
      }
      requestAnimationFrame(renderFrame);
    };

    renderFrame();
  };

  const drawPredictions = (predictions, ctx) => {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    predictions.forEach((prediction) => {
      ctx.strokeStyle = '#00FFFF';
      ctx.lineWidth = 2;
      ctx.strokeRect(
        prediction.bbox.x - prediction.bbox.width / 2,
        prediction.bbox.y - prediction.bbox.height / 2,
        prediction.bbox.width,
        prediction.bbox.height
      );

      ctx.fillStyle = '#00FFFF';
      ctx.font = '16px Arial';
      ctx.fillText(
        `${prediction.class} (${(prediction.confidence * 100).toFixed(2)}%)`,
        prediction.bbox.x - prediction.bbox.width / 2,
        prediction.bbox.y - prediction.bbox.height / 2 - 10
      );
    });
  };

  const flipCamera = () => {
    const newFacingMode = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(newFacingMode);
    startVideo();
  };

  return (
    <div className="ObjectDetection">
      <Link to="/" className="home-button">Home</Link>
      <Helmet>
        {/* Roboflow script will be dynamically loaded */}
      </Helmet>
      <h1>Fruit Quality Detection</h1>
      <div className="video-container">
        <video
          ref={videoRef}
          width="640"
          height="480"
          className="video-feed"
        />
        <canvas
          ref={canvasRef}
          width="640"
          height="480"
          className="canvas-overlay"
        />
      </div>
      <div className="button-group">
        <button onClick={startVideo} className="start-button">Start Object Detection</button>
        <button onClick={flipCamera} className="flip-button">Flip Camera</button>
      </div>
      <div className="prediction-results">
        {predictions.map((prediction, index) => (
          <p key={index}>
            Object: {prediction.class} | Confidence: {(prediction.confidence * 100).toFixed(2)}%
          </p>
        ))}
      </div>
    </div>
  );
}

export default ObjectDetection;
