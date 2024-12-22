const mongoose = require('mongoose');

const stockSchema = new mongoose.Schema({
  Date: String,
  'Open Price': Number,
  'High Price': Number,
  'Low Price': Number,
  'Close Price': Number,
  'Average Price': Number,
  Volume: Number,
  'No. of Trades': Number,
  'Total Turnover (Rs.)': Number,
  'Deliverable Quantity': Number,
  '% Deli. Qty to Traded Qty': Number,
  'Spread High-Low': Number,
  'Spread Close-Open': Number
});

const Stocks = mongoose.model('Stocks', stockSchema);

module.exports = Stocks;
