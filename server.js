const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- API Routes ---

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/api/stats', (req, res) => {
  res.json({
    videos: 1247,
    subscribers: 84320,
    categories: 12,
    hoursWatched: 98400,
  });
});

app.get('/api/features', (req, res) => {
  res.json([
    {
      id: 1,
      icon: '🎬',
      title: 'Video Library',
      description: 'Browse and discover thousands of curated tech tutorials, reviews, and deep-dives.',
    },
    {
      id: 2,
      icon: '🤖',
      title: 'AI Summaries',
      description: 'Get instant AI-generated summaries for any video so you can learn faster.',
    },
    {
      id: 3,
      icon: '📌',
      title: 'Smart Playlists',
      description: 'Automatically organize content into smart playlists based on your interests.',
    },
    {
      id: 4,
      icon: '🔔',
      title: 'Topic Alerts',
      description: 'Subscribe to topics and get notified when new relevant content drops.',
    },
    {
      id: 5,
      icon: '📊',
      title: 'Learning Paths',
      description: 'Follow structured learning paths from beginner to advanced on any tech stack.',
    },
    {
      id: 6,
      icon: '🌐',
      title: 'Community',
      description: 'Join discussions, share notes, and collaborate with other tech enthusiasts.',
    },
  ]);
});

app.get('/api/trending', (req, res) => {
  res.json([
    { id: 1, title: 'Building AI Agents from Scratch', channel: 'Tech Insights', views: '142K', category: 'AI/ML' },
    { id: 2, title: 'Rust vs Go in 2026', channel: 'Systems Lab', views: '98K', category: 'Languages' },
    { id: 3, title: 'Full-Stack with Next.js 15', channel: 'WebDev Pro', views: '87K', category: 'Web Dev' },
    { id: 4, title: 'Docker & Kubernetes Deep Dive', channel: 'DevOps HQ', views: '76K', category: 'DevOps' },
  ]);
});

// Catch-all: serve the frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`GeekBot server running at http://localhost:${PORT}`);
});
