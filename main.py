from flask import Flask, request, render_template, jsonify, send_from_directory
from app.downloader import download_media
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, 
            static_folder='/home/hika/youtube-to-mp3/static', 
            template_folder='/home/hika/youtube-to-mp3/static')

DOWNLOAD_FOLDER = '/home/hika/youtube-to-mp3/downloads'

# Global executor for background downloads
executor = ThreadPoolExecutor(max_workers=4)
# Simple in-memory store for task status
tasks = {}

def run_download(task_id, url, mode, quality):
    """Worker function to handle the download process."""
    try:
        tasks[task_id] = {"status": "downloading", "result": None}
        result = download_media(url, mode=mode, quality=quality, output_path=DOWNLOAD_FOLDER)
        tasks[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        tasks[task_id] = {"status": "error", "result": {"status": "error", "message": str(e)}}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def handle_download():
    data = request.json
    url = data.get('url')
    mode = data.get('mode', 'mp3') # options: 'mp3', 'original', 'mp4'
    quality = data.get('quality', '192')
    
    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400
    
    # Create a unique task ID
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "result": None}
    
    # Submit to executor (Non-blocking)
    executor.submit(run_download, task_id, url, mode, quality)
    
    return jsonify({
        "status": "success", 
        "task_id": task_id, 
        "message": "Download started in background"
    }), 202

@app.route('/status/<task_id>')
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404
    
    if task['status'] == 'completed':
        result = task['result']
        if result['status'] == 'success':
            filename = os.path.basename(result['path'])
            # Merge result with file_url for the frontend
            return jsonify({
                "status": "completed",
                "title": result['title'],
                "file_url": f"/download_file/{filename}"
            })
        else:
            return jsonify({"status": "error", "message": result.get('message', 'Download failed')}), 400
            
    return jsonify({"status": task['status']})

@app.route('/download_file/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
