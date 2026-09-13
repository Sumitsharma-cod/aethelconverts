# AethelConverts

Free MP4 → MP3 and MP3 → MP4 web converter.

## Run on Windows

1. Install Python 3.11+.
2. Install FFmpeg and make sure `ffmpeg.exe` is in PATH, or set:
   `set FFMPEG_PATH=C:\path\to\ffmpeg.exe`
3. Open PowerShell in this folder.
4. Run:
   `python -m pip install -r requirements.txt`
5. Run:
   `python app.py`
6. Open `http://127.0.0.1:5000`

## Important for production

This starter is designed to be easy to run locally. Before public launch:
- Add authentication/rate limiting or per-IP quotas.
- Add automatic cleanup for old output files.
- Use HTTPS.
- Run behind a production WSGI server/reverse proxy.
- Add real contact information to the policies.
- Replace the ad placeholder with an ad network only after meeting its approval rules.
- Consider a queue/worker system for many simultaneous conversions.
