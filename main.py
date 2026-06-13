from flask import Flask, request, render_template, jsonify, send_from_directory
from app.downloader import download_media
import os

app = Flask(__name__, 
            static_folder='/home/hika/youtube-to-mp3/static', 
            template_folder='/home/hika/youtube-to-mp3/static')

DOWNLOAD_FOLDER = '/home/hika/youtube-to-mp3/downloads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def handle_download():
    data = request.json
    url = data.get('url')
    mode = data.get('mode', 'mp3')
    quality = data.get('quality', '192')
    
    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400
    
    result = download_media(url, mode=mode, quality=quality, output_path=DOWNLOAD_FOLDER)
    
    if result['status'] == 'success':
        filename = os.path.basename(result['path'])
        return jsonify({
            "status": "success", 
            "title": result['title'], 
            "file_url": f"/download_file/{filename}"
        })
    
    return jsonify(result, 400)

@app.route('/download_file/<filename>')
def serve_file(filename):
    # This forces the browser to trigger a "Save As" dialog
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
