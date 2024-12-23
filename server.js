const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');
require('dotenv').config(); // Load environment variables from .env file

const app = express();
const port = process.env.PORT || 3000; // Use PORT from environment variables or default to 3000

// MongoDB connection string
const uri = process.env.MONGO_URI;

if (!uri) {
  console.error('Error: MONGO_URI not set in environment variables.');
  process.exit(1); // Exit the application if MONGO_URI is missing
}

// Enable CORS for all origins (you can restrict this to specific origins if needed)
app.use(cors());
app.use(express.json());

// MongoDB connection and initialization
let db;
MongoClient.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(client => {
    db = client.db('Stocks'); // Assuming the database name is "Stocks"
    console.log('Connected to MongoDB');
  })
  .catch(error => {
    console.error('Error connecting to MongoDB:', error);
    process.exit(1); // Exit the application on connection error
  });

// API route to fetch stock data for a company
app.get('/api/Stocks/:company', async (req, res) => {
  try {
    const company = req.params.company;

    if (!db) {
      return res.status(500).json({ message: 'Database not initialized' });
    }

    // Fetch stock data from the collection based on the company name
    const stockData = await db.collection(company).find().toArray();

    if (stockData.length === 0) {
      return res.status(404).json({ message: `No data found for ${company}` });
    }

    res.json(stockData);
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
