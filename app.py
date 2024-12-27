from flask import Flask, request, send_from_directory, jsonify, Response
import os

app = Flask(__name__)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, os.getenv("dl","./RvxDl"))

# Ensure directories exist
os.makedirs(PUBLIC_DIR, exist_ok=True)

@app.route("/")
def index():
    """Home route with instructions."""
    return jsonify({
        "message": "Welcome to the RVX File Hoster Bot",
        "instructions": {
            "download_file": "/download/<filename>",
            "stream_file": "/stream/<filename>"
        }
    })


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Download a file from the public directory."""
    try:
        return send_from_directory(PUBLIC_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404



@app.route("/stream/<filename>", methods=["GET"])
def stream_file(filename):
    """Stream a video, audio, or image file."""
    file_path = os.path.join(PUBLIC_DIR, filename)

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    def generate():
        """Generator to read the file in chunks for streaming."""
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                yield chunk

    # Set the appropriate MIME type based on the file extension
    mime_type = get_mime_type(filename)
    return Response(generate(), content_type=mime_type)


def get_mime_type(filename):
    """Determine the MIME type based on the file extension."""
    ext = os.path.splitext(filename)[1].lower()

    if ext in [".mp4", ".mkv", ".webm"]:
        return "video/mp4"  # Default to MP4
    elif ext in [".mp3", ".wav", ".ogg"]:
        return "audio/mpeg"  # Default to audio/mpeg
    elif ext in [".jpg", ".jpeg", ".png", ".gif"]:
        return "image/jpeg"  # Default to image/jpeg
    else:
        return "application/octet-stream"  # Fallback for unknown types


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
