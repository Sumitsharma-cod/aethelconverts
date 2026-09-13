import os, uuid, subprocess, shutil
from flask import Flask, render_template, request, send_from_directory, jsonify

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE, "uploads")
OUTPUTS = os.path.join(BASE, "outputs")
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB

ALLOWED = {"mp4", "mp3", "mov", "m4v", "webm", "mkv", "wav", "aac", "m4a"}

def find_ffmpeg():
    env = os.environ.get("FFMPEG_PATH")
    if env and os.path.isfile(env):
        return env
    found = shutil.which("ffmpeg")
    if found:
        return found
    # Common local Windows locations, including a folder layout often used by ffmpeg zip builds.
    candidates = [
        os.path.join(BASE, "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.expanduser(r"~\Downloads\pro\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe"),
        os.path.expanduser(r"~\Downloads\website\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify(error="No file selected."), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify(error="No file selected."), 400

    ext = os.path.splitext(f.filename)[1].lower().lstrip(".")
    mode = request.form.get("mode", "").lower()

    if ext not in ALLOWED:
        return jsonify(error="Unsupported file type."), 400

    if mode not in {"mp3", "mp4"}:
        return jsonify(error="Invalid conversion type."), 400

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        return jsonify(error="FFmpeg was not found. Install FFmpeg or set FFMPEG_PATH."), 500

    job = uuid.uuid4().hex
    input_path = os.path.join(UPLOADS, f"{job}.{ext}")
    output_ext = "mp3" if mode == "mp3" else "mp4"
    output_path = os.path.join(OUTPUTS, f"{job}.{output_ext}")

    f.save(input_path)

    try:
        if mode == "mp3":
            cmd = [ffmpeg, "-y", "-i", input_path, "-vn", "-codec:a", "libmp3lame",
                   "-b:a", "192k", output_path]
        else:
            # Creates a simple MP4 video from the source audio using a generated black frame.
            # This keeps the service free and avoids requiring an uploaded image.
            cmd = [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30",
                   "-i", input_path, "-c:v", "libx264", "-preset", "veryfast",
                   "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
                   "-shortest", "-pix_fmt", "yuv420p", output_path]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0 or not os.path.exists(output_path):
            return jsonify(error="Conversion failed. Please try another valid media file."), 500

        return jsonify(
            success=True,
            download=f"/download/{job}/{job}.{output_ext}",
            filename=f"AethelConverts_{os.path.splitext(f.filename)[0]}.{output_ext}"
        )
    finally:
        try:
            os.remove(input_path)
        except OSError:
            pass

@app.route("/download/<job>/<filename>")
def download(job, filename):
    return send_from_directory(OUTPUTS, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(_):
    return jsonify(error="File is too large. Maximum size is 500 MB."), 413

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
