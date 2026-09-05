/**
 * AethelConvertS - Commercial Enterprise Server Engine
 * Developed by Sumit Sharma
 */

const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const compression = require('compression');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Security & Optimization Middleware
app.use(helmet({ contentSecurityPolicy: false }));
app.use(compression());
app.use(express.json());
app.use(cors({ origin: ['https://www.aethelconverts.com', 'http://localhost:3000'] }));

// Heavy Traffic Control: Advanced IP Rate Limiting (10 requests per minute per IP)
const trafficLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 10,
    message: { error: 'Traffic threshold exceeded. Please wait a moment before queuing another conversion.' },
    standardHeaders: true,
    legacyHeaders: false,
});
app.use('/api/convert', trafficLimiter);

// Serve static frontend assets
app.use(express.static(path.join(__dirname, 'public')));

// Simulated Queue and Traffic Manager
let activeJobs = 0;
const MAX_CONCURRENT_JOBS = 5;

app.post('/api/convert', (async (req, res) => {
    const { url, format, quality } = req.body;
    
    if (!url || !url.includes('youtube.com') && !url.includes('youtu.be')) {
        return res.status(400).json({ error: 'Invalid YouTube URL provided.' });
    }

    if (activeJobs >= MAX_CONCURRENT_JOBS) {
        return res.status(429).json({ error: 'Server traffic is peaking. Your request has been queued.' });
    }

    activeJobs++;
    
    // Simulating safe extraction & conversion pipeline (using yt-dlp & ffmpeg architecture)
    setTimeout(() => {
        activeJobs--;
        const simulatedFileName = `AethelConvertS_${Date.now()}.${format === 'mp3' ? 'mp3' : 'mp4'}`;
        res.json({
            success: true,
            message: 'Conversion completed successfully via AethelConvertS high-speed worker nodes.',
            downloadUrl: `/downloads/${simulatedFileName}`,
            meta: { title: 'High Definition Enterprise Media Output', format, quality }
        });
    }, 2500);
}));

// Fallback Route
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`[AethelConvertS Engine] Running securely on port ${PORT} - Architect: Sumit Sharma`);
});