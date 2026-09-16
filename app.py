import os
import uuid
import subprocess
import shutil

from flask import Flask, render_template, request, send_from_directory, jsonify


# =========================
# PATHS
# =========================

BASE = os.path.dirname(os.path.abspath(__file__))

UPLOADS = os.path.join(BASE, "uploads")
OUTPUTS = os.path.join(BASE, "outputs")

os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)


# =========================
# FLASK
# =========================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024


# =========================
# ALLOWED FILE TYPES
# =========================

ALLOWED = {
    "mp4",
    "mp3",
    "mov",
    "m4v",
    "webm",
    "mkv",
    "wav",
    "aac",
    "m4a"
}


# =========================
# FIND FFMPEG
# =========================

def find_ffmpeg():

    # Check environment variable first
    env = os.environ.get("FFMPEG_PATH")

    if env and os.path.isfile(env):
        return env


    # Check Windows PATH
    found = shutil.which("ffmpeg")

    if found:
        return found


    # Check local project folder and your FFmpeg folder
    candidates = [
        os.path.join(
            BASE,
            "ffmpeg",
            "bin",
            "ffmpeg.exe"
        ),

        os.path.expanduser(
            r"~\Downloads\PRGT\ffmpeg-9.0.1-essentials_build\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"
        )
    ]


    for path in candidates:

        if os.path.isfile(path):
            return path


    return None


# =========================
# HOME
# =========================

@app.route("/")
def index():

    return render_template("index.html")


# =========================
# PRIVACY
# =========================

@app.route("/privacy")
def privacy():

    return render_template("privacy.html")


# =========================
# TERMS
# =========================

@app.route("/terms")
def terms():

    return render_template("terms.html")


# =========================
# CONVERT
# =========================

@app.route("/convert", methods=["POST"])
def convert():

    # Check file
    if "file" not in request.files:

        return jsonify(
            error="No file selected."
        ), 400


    f = request.files["file"]


    if not f.filename:

        return jsonify(
            error="No file selected."
        ), 400


    # Get extension
    ext = os.path.splitext(
        f.filename
    )[1].lower().lstrip(".")


    # Get conversion mode
    mode = request.form.get(
        "mode",
        ""
    ).lower()


    # Check extension
    if ext not in ALLOWED:

        return jsonify(
            error="Unsupported file type."
        ), 400


    # Check conversion type
    if mode not in {"mp3", "mp4"}:

        return jsonify(
            error="Invalid conversion type."
        ), 400


    # Find FFmpeg
    ffmpeg = find_ffmpeg()


    if not ffmpeg:

        return jsonify(
            error="FFmpeg was not found. Install FFmpeg or set FFMPEG_PATH."
        ), 500


    # Create unique job ID
    job = uuid.uuid4().hex


    # Input file
    input_path = os.path.join(
        UPLOADS,
        f"{job}.{ext}"
    )


    # Output extension
    output_ext = (
        "mp3"
        if mode == "mp3"
        else "mp4"
    )


    # Output file
    output_path = os.path.join(
        OUTPUTS,
        f"{job}.{output_ext}"
    )


    # Save uploaded file
    f.save(input_path)


    try:

        # =========================
        # MP4 → MP3
        # =========================

        if mode == "mp3":

            cmd = [
                ffmpeg,
                "-y",
                "-i",
                input_path,
                "-vn",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "192k",
                output_path
            ]


        # =========================
        # MP3 → MP4
        # =========================

        else:

            cmd = [
                ffmpeg,
                "-y",

                "-f",
                "lavfi",

                "-i",
                "color=c=black:s=1280x720:r=30",

                "-i",
                input_path,

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-tune",
                "stillimage",

                "-c:a",
                "aac",

                "-b:a",
                "192k",

                "-shortest",

                "-pix_fmt",
                "yuv420p",

                output_path
            ]


        # Run FFmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        # Check conversion
        if (
            result.returncode != 0
            or not os.path.exists(output_path)
        ):

            print("\n========== FFMPEG ERROR ==========")
            print(result.stderr)
            print("==================================\n")


            return jsonify(
                error="Conversion failed. Please try another valid media file."
            ), 500


        # Success
        return jsonify(

            success=True,

            download=(
                f"/download/{job}/{job}.{output_ext}"
            ),

            filename=(
                f"AethelConverts_"
                f"{os.path.splitext(f.filename)[0]}."
                f"{output_ext}"
            )
        )


    finally:

        # Delete uploaded source file
        try:

            os.remove(input_path)

        except OSError:

            pass


# =========================
# DOWNLOAD
# =========================

@app.route(
    "/download/<job>/<filename>"
)
def download(job, filename):

    return send_from_directory(
        OUTPUTS,
        filename,
        as_attachment=True
    )


# =========================
# FILE TOO LARGE
# =========================

@app.errorhandler(413)
def too_large(error):

    return jsonify(
        error="File is too large. Maximum size is 500 MB."
    ), 413


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )