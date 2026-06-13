import yt_dlp
import os
import re

def download_media(url, mode='mp3', quality='192', output_path='downloads'):
    """
    Downloads media from YouTube.
    mode: 'mp3' for audio, 'mp4' for video
    quality: for mp3 (128, 192, 320), for mp4 (best, 720, 480)
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if mode == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': True,
            'no_warnings': True,
        }
    else: # mode == 'mp4'
        # Handle video quality mapping
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '720': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        }
        fmt = quality_map.get(quality, 'bestvideo+bestaudio/best')
        
        ydl_opts = {
            'format': fmt,
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Correct extension based on mode
            if mode == 'mp3':
                final_filename = re.sub(r'\.[^.]+$', '.mp3', filename)
            else:
                final_filename = re.sub(r'\.[^.]+$', '.mp4', filename)
                
            return {"status": "success", "title": info.get('title'), "path": final_filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}
