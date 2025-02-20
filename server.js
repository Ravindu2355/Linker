const express = require("express");
const fs = require("fs");
const path = require("path");
const mime = require("mime");
const { spawn } = require("child_process");

const app = express();

// Directories
const PUBLIC_DIR = process.env.dl || "./RvxDl";

// Ensure directories exist
if (!fs.existsSync(PUBLIC_DIR)) {
    fs.mkdirSync(PUBLIC_DIR, { recursive: true });
}

// Home route
app.get("/", (req, res) => {
    res.json({
        message: "Welcome to the RVX File Hoster Bot",
        instructions: {
            download_file: "/download/<filename>",
            stream_file: "/stream/<filename>",
            m3u8_stream: "/m3u8/<filename>"
        }
    });
});

// File download route
app.get("/download/:filename", (req, res) => {
    const filePath = path.join(PUBLIC_DIR, req.params.filename);
    
    if (fs.existsSync(filePath)) {
        res.download(filePath);
    } else {
        res.status(404).json({ error: "File not found" });
    }
});

// Improved video streaming route (supports seeking)
app.get("/stream/:filename", (req, res) => {
    const filePath = path.join(PUBLIC_DIR, req.params.filename);

    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: "File not found" });
    }

    const stat = fs.statSync(filePath);
    const fileSize = stat.size;
    const range = req.headers.range;

    if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

        if (start >= fileSize) {
            return res.status(416).json({ error: "Range start exceeds file size" });
        }

        const chunkSize = end - start + 1;
        const fileStream = fs.createReadStream(filePath, { start, end });

        res.writeHead(206, {
            "Content-Range": `bytes ${start}-${end}/${fileSize}`,
            "Accept-Ranges": "bytes",
            "Content-Length": chunkSize,
            "Content-Type": mime.getType(filePath),
        });

        fileStream.pipe(res);
    } else {
        res.writeHead(200, { "Content-Type": mime.getType(filePath) });
        fs.createReadStream(filePath).pipe(res);
    }
});

// Dynamic M3U8 streaming (on-the-fly HLS)
app.get("/m3u8/:filename", (req, res) => {
    const filePath = path.join(PUBLIC_DIR, req.params.filename);

    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: "File not found" });
    }

    res.setHeader("Content-Type", "application/vnd.apple.mpegurl");

    // Spawn FFmpeg to convert video to M3U8 format in real-time
    const ffmpeg = spawn("ffmpeg", [
        "-i", filePath,         // Input file
        "-c:v", "libx264",      // Video codec
        "-preset", "veryfast",  // Faster conversion
        "-c:a", "aac",          // Audio codec
        "-f", "hls",            // Output format: HLS
        "-hls_time", "5",       // Each segment = 5s
        "-hls_list_size", "6",  // Store only recent segments
        "-hls_flags", "delete_segments", // Delete old segments
        "pipe:1"                // Output to response stream
    ]);

    ffmpeg.stdout.pipe(res);
    ffmpeg.stderr.on("data", (data) => console.error(`FFmpeg error: ${data}`));
    ffmpeg.on("close", () => console.log(`FFmpeg stream closed for ${req.params.filename}`));
});

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});
