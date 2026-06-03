import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { fileURLToPath } from 'url';
import * as BinanceModule from 'binance-api-node';
const Binance = (BinanceModule as any).default || BinanceModule;
import cors from 'cors';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';

import fs from 'fs';

dotenv.config();

import axios from 'axios';

// Load Bot Configuration
const botConfig = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'bot_config.json'), 'utf8'));

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

import { spawn } from 'child_process';

async function startServer() {
  // Start Vhalinor Python Engine
  console.log('🚀 Iniciando Vhalinor Python Engine...');
  
  const startPython = (cmd: string) => {
    console.log(`[System] Tentando iniciar motor com: ${cmd}`);
    const pythonEngine = spawn(cmd, ['vhalinor_engine.py']);
    
    pythonEngine.stdout.on('data', (data) => {
      console.log(`[Python Engine]: ${data}`);
    });

    pythonEngine.stderr.on('data', (data) => {
      console.error(`[Python Engine Error]: ${data}`);
    });

    pythonEngine.on('error', (err: any) => {
      if (err.code === 'ENOENT' && cmd === 'python3') {
        console.log('⚠️ python3 não encontrado, tentando "python"...');
        startPython('python');
      } else {
        console.error(`❌ Erro ao iniciar motor Python (${cmd}):`, err.message);
      }
    });

    pythonEngine.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`⚠️ Motor Python encerrou com código ${code}. Reiniciando em 5s...`);
        setTimeout(() => startPython(cmd), 5000);
      }
    });
    
    return pythonEngine;
  };

  startPython('python3');

  const app = express();
  const httpServer = createServer(app);
  const io = new Server(httpServer, {
    cors: {
      origin: '*',
    },
  });

  const PORT = 3000;
  const PYTHON_API = 'http://127.0.0.1:3001/api';

  app.use(cors());
  app.use(express.json());

  // API Routes (Proxying to Python)
  app.get('/api/health', async (req, res) => {
    try {
      const response = await axios.get(`${PYTHON_API}/status`);
      res.json({ 
        status: 'ok', 
        node: 'active',
        python: response.data
      });
    } catch (e) {
      res.status(503).json({ status: 'error', python: 'offline' });
    }
  });

  app.get('/api/market', async (req, res) => {
    try {
      const response = await axios.get(`${PYTHON_API}/market`);
      res.json(response.data);
    } catch (e) {
      res.status(500).json({ error: 'Python Engine unreachable' });
    }
  });

  app.get('/api/analysis/central_ai', async (req, res) => {
    try {
      const response = await axios.get(`${PYTHON_API}/analysis/central_ai`, { timeout: 5000 });
      res.json(response.data);
    } catch (e: any) {
      console.error(`[Proxy Error] /api/analysis/central_ai: ${e.message}`);
      res.status(500).json({ error: 'Python Engine unreachable', details: e.message });
    }
  });

  app.get('/api/analysis/:symbol', async (req, res) => {
    try {
      const response = await axios.get(`${PYTHON_API}/analysis/${req.params.symbol}`);
      res.json(response.data);
    } catch (e) {
      res.status(500).json({ error: 'Python Engine unreachable' });
    }
  });

  app.post('/api/lextrader/analyze', async (req, res) => {
    try {
      const response = await axios.post(`${PYTHON_API}/lextrader/analyze`, req.body);
      res.json(response.data);
    } catch (e) {
      res.status(500).json({ error: 'Python Engine unreachable' });
    }
  });

  app.post('/api/central_ai/command', async (req, res) => {
    try {
      const response = await axios.post(`${PYTHON_API}/central_ai/command`, req.body);
      res.json(response.data);
    } catch (e) {
      res.status(500).json({ error: 'Python Engine unreachable' });
    }
  });

  // WebSocket for real-time price updates (Polling Python Engine)
  setInterval(async () => {
    try {
      const response = await axios.get(`${PYTHON_API}/market`);
      io.emit('ticker_update', response.data);
    } catch (e) {
      // Silent fail if engine is starting
    }
  }, 1000);

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  httpServer.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('Failed to start server:', err);
});
