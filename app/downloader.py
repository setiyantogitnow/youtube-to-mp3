import yt_dlp
import os
import re

def download_media(url, mode='mp3', quality='192', output_path='downloads'):
    """
    Downloads media from YouTube.
    mode: 'mp3' (lossy), 'original' (lossless/best available), 'mp4' (video)
    quality: for mp3 (128, 192, 320), for mp4 (best, 720, 480)
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Handle Cookies for Bot Detection (Vercel Deployment)
    cookie_path = 'cookies.txt'
    cookies_env = os.environ.get('YOUTUBE_COOKIES')
    if cookies_env:
        # Write env var content to a temporary file in /tmp
        cookie_path = os.path.join('/tmp', 'cookies.txt')
        with open(cookie_path, 'w') as f:
            f.write(cookies_env)
    elif not os.path.exists('cookies.txt'):
        # If no env var and no local file, we just proceed and hope for the best
        # but we set it to None to avoid yt-dlp looking for a non-existent file
        cookie_path = None

    if mode == 'original':
        # Lossless/Direct Stream: Get the best audio without re-encoding
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        if cookie_path:
            ydl_opts['cookiefile'] = cookie_path
    elif mode == 'mp3':
        # Lossy: Convert to MP3
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
        if cookie_path:
            ydl_opts['cookiefile'] = cookie_path
    else: # mode == 'mp4'
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
        if cookie_path:
            ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Correct extension based on mode
            if mode == 'mp3':
                final_filename = re.sub(r'\.[^.]+$', '.mp3', filename)
            elif mode == 'original':
                # Use the extension provided by yt-dlp (usually .m4a, .webm, or .opus)
                final_filename = filename
            else:
                final_filename = re.sub(r'\.[^.]+$', '.mp4', filename)
                
            return {"status": "success", "title": info.get('title'), "path": final_filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}
