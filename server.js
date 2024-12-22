const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();
const Stocks = require('./models/Stocks'); // Adjust the path to the actual location of your model


// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI,)
.then(() => console.log("Connected to MongoDB"))
.catch(err => console.error("MongoDB connection error:", err));

// Define Routes
app.get('/api/Stocks/:company', async (req, res) => {
    try {
      const company = req.params.company;  // Get the company name from the URL
  
      // Dynamically get the collection by the company name
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
  

// Start Server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
