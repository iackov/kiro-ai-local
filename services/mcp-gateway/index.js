#!/usr/bin/env node

/**
 * MCP Gateway - Simple REST proxy for RAG API
 * Simplified version without MCP SDK dependency
 */

import express from 'express';
import axios from 'axios';
import winston from 'winston';

// Configure logging
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: '/logs/mcp-gateway.log' }),
    new winston.transports.Console({ format: winston.format.simple() })
  ]
});

const RAG_API_URL = process.env.RAG_API_URL || 'http://rag-api:8001';
const PORT = process.env.PORT || 8002;

const app = express();
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'mcp-gateway' });
});

// Proxy to RAG API
app.post('/query', async (req, res) => {
  try {
    logger.info('Query request', { query: req.body.query });
    const response = await axios.post(`${RAG_API_URL}/query`, req.body);
    res.json(response.data);
  } catch (error) {
    logger.error('Query failed', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

app.post('/ingest', async (req, res) => {
  try {
    logger.info('Ingest request', { path: req.body.path });
    const response = await axios.post(`${RAG_API_URL}/ingest`, req.body);
    res.json(response.data);
  } catch (error) {
    logger.error('Ingest failed', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

app.get('/inspect', async (req, res) => {
  try {
    const response = await axios.get(`${RAG_API_URL}/inspect`);
    res.json(response.data);
  } catch (error) {
    logger.error('Inspect failed', { error: error.message });
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  logger.info(`MCP Gateway listening on port ${PORT}`);
  logger.info(`Proxying to RAG API at ${RAG_API_URL}`);
});
