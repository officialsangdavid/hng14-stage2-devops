const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

// FIX: Use environment variable instead of hardcoded localhost
const API_URL = process.env.API_URL || "http://api:8000";

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// FIX: Added health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: "something went wrong" });
  }
});

// FIX: Bind to 0.0.0.0 to accept external connections
app.listen(3000, '0.0.0.0', () => {
  console.log('Frontend running on 0.0.0.0:3000');
});