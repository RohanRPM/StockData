const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI,)
.then(() => console.log("Connected to MongoDB"))
.catch(err => console.error("MongoDB connection error:", err));

// Define Routes
app.get("/api/stocks/:company", async (req, res) => {
    try {
        const company = req.params.company;
        const data = await Stock.find({ company: company });
        if (!data || data.length === 0) {
          return res.status(404).json({ message: `No data found for ${company}` });
        }
        res.json(data);
    } catch (err) {
        console.error(err);
        res.status(500).send("Server error");
    }
});

// Start Server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
