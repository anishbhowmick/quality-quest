const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(cors()); // Allow requests from React app

// Set up storage for uploaded images
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/'); // Directory to store uploaded images
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname)); // File naming convention
  }
});

const upload = multer({ storage });

// Helper function to process images
const processImage = (imagePath, callback) => {
  exec(`python barcode-detection.py ${imagePath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${error.message}`);
      return callback(`Error processing image: ${imagePath}`);
    }

    const barcodeData = stdout;

    exec(`python mfg-expiry.py ${imagePath}`, (err, mfgExpiryOutput) => {
      if (err) {
        console.error(`Error extracting dates: ${err.message}`);
        return callback(`Error extracting dates: ${imagePath}`);
      }

      const result = {
        barcodeData,
        manufacturingExpiryDates: mfgExpiryOutput
      };

      // Delete the image file after processing
      fs.unlink(imagePath, (unlinkErr) => {
        if (unlinkErr) {
          console.error(`Error deleting file: ${unlinkErr.message}`);
        }
      });

      callback(null, result);
    });
  });
};

// Endpoint to upload images and process barcode detection for a single product
app.post('/upload-single-product', upload.single('productImage'), (req, res) => {
  const imagePath = req.file.path;
  const fileName = req.file.originalname;

  processImage(imagePath, (err, result) => {
    if (err) {
      return res.status(500).send(err);
    }
    const combinedResult = {
      ...result,
      fileName: fileName
    };
    return res.json(combinedResult);
  });
});

// Endpoint to upload images and process barcode detection for multiple products
app.post('/upload-multiple-products', upload.array('productImages', 6), (req, res) => {
  const imagePaths = req.files.map(file => file.path);
  const fileNames = req.files.map(file => file.originalname);
  const results = [];

  let processedCount = 0;
  imagePaths.forEach((imagePath, index) => {
    processImage(imagePath, (err, result) => {
      if (err) {
        return res.status(500).send(err);
      }
      results.push({ ...result, fileName: fileNames[index] });
      processedCount++;
      if (processedCount === imagePaths.length) {
        return res.json(results);
      }
    });
  });
});

// Start server
app.listen(5000, () => {
  console.log('Server running on http://localhost:5000');
});
