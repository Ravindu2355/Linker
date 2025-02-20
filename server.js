const express = require("express");
const fs = require("fs");
const path = require("path");
const mime = require("mime");

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
            stream_file: "/stream/<filename>"
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

// File streaming route
app.get("/stream/:filename", (req, res) => {
    const filePath = path.join(PUBLIC_DIR, req.params.filename);
    
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: "File not found" });
    }

    const fileSize = fs.statSync(filePath).size;
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

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});
