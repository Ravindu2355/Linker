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


#########------------------

@app.route("/stream/<filename>", methods=["GET"])
def stream_file(filename):
    """Stream a video, audio, or image file with support for seeking."""
    file_path = os.path.join(PUBLIC_DIR, filename)

    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404

    # Get the file size
    file_size = os.path.getsize(file_path)

    # Get the range from the client request
    range_header = request.headers.get('Range', None)

    if range_header:
        # Parse the Range header to get start and end byte ranges
        byte_range = range_header.strip().lower()
        if byte_range.startswith("bytes="):
            range_str = byte_range[len("bytes="):]
            start, end = range_str.split("-")

            start = int(start) if start else 0
            end = int(end) if end else file_size - 1

            if start >= file_size:
                return jsonify({"error": "Range start exceeds file size"}), 416

            if end >= file_size:
                end = file_size - 1

            # Set the response status to 206 Partial Content
            status_code = 206
            content_range = f"bytes {start}-{end}/{file_size}"

            def generate():
                """Generator to read the file in chunks starting from the 'start' byte."""
                with open(file_path, "rb") as f:
                    f.seek(start)
                    while start <= end:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        yield chunk
                        start += len(chunk)

            return Response(generate(), status=status_code, content_type=get_mime_type(filename),
                            content_range=content_range)

    # If no range header, return the whole file
    def generate():
        """Generator to read the whole file in chunks for streaming."""
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                yield chunk

    return Response(generate(), content_type=get_mime_type(filename))





#########------------------

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
