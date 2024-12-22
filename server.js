const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
mongoose.connect(process.env.MONGO_URI, {
    // useNewUrlParser: true,
    // useUnifiedTopology: true,
})
.then(() => console.log("Connected to MongoDB"))
.catch(err => console.error("MongoDB connection error:", err));

// Define Routes
app.get("/api/stocks/:company", async (req, res) => {
    try {
        const { company } = req.params;

        // Dynamic collection selection
        const collection = mongoose.connection.db.collection(company);
        const data = await collection.find({}).toArray();
        
        if (data.length === 0) {
            return res.status(404).send(`No data found for ${company}`);
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
