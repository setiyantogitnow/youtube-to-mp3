# YouTube to MP3 Downloader

A simple Flask-based web application to download audio from YouTube videos.

## Features
- Clean web interface
- MP3 conversion
- Custom quality settings
- Direct browser downloads

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/setiyantogitnow/youtube-to-mp3.git
   cd youtube-to-mp3
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install flask yt-dlp
   ```

## Usage
Run the application:
```bash
python main.py
```
Open your browser and navigate to `http://localhost:5000`.

## Project Structure
- `main.py`: Flask application entry point.
- `app/downloader.py`: Core downloading logic.
- `static/`: HTML, CSS, and frontend assets.
- `downloads/`: Temporary storage for converted files.
