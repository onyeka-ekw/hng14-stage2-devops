const express = require('express');
const axios = require('axios');
const path = require('path');
const helmet = require('helmet');
const app = express();

// Environment variables
const API_URL = process.env.API_URL || "http://localhost:8000";
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'frontend' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    console.error('Submit job error:', err.message);
    const status = err.response ? err.response.status : 500;
    const message = err.response ? err.response.data : { error: "API connection failed" };
    res.status(status).json(message);
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    console.error('Get status error:', err.message);
    const status = err.response ? err.response.status : 500;
    const message = err.response ? err.response.data : { error: "API connection failed" };
    res.status(status).json(message);
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend running on port ${PORT}`);
  console.log(`API URL: ${API_URL}`);
});
