"""Video source handling with URL download support.

Provides video source resolution with priority:
1. Command line argument (path or URL)
2. Local video.mp4 file
3. Default URL (Big Buck Bunny from Google)
"""

import sys
import tempfile
import urllib.request
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
LOCAL_VIDEO = VIDEO_DIR / 'video.mp4'
DEFAULT_VIDEO_URL = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'

# Global cache for downloaded video
_downloaded_video_path: str | None = None


def download_video_with_headers(url: str) -> str:
    """Download video from URL with browser headers to handle redirects.
    
    Returns path to temporary file.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'video/mp4,video/*;q=0.9,*/*;q=0.8',
    }
    
    request = urllib.request.Request(url, headers=headers)
    
    # Create temp file with .mp4 extension
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    
    print(f'Downloading video from {url}...')
    with urllib.request.urlopen(request) as response:
        # Read in chunks
        chunk_size = 1024 * 1024  # 1MB
        total = 0
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            temp_file.write(chunk)
            total += len(chunk)
            print(f'  Downloaded {total / 1024 / 1024:.1f} MB', end='\r')
    
    temp_file.close()
    print(f'\nDownloaded to {temp_file.name}')
    return temp_file.name


def get_video_source() -> str:
    """Get video source from command line, local file, or default URL.
    
    Priority:
    1. Command line argument (path or URL)
    2. Local video.mp4 file
    3. Default URL (Big Buck Bunny from Google)
    
    Downloads URL once and caches the result globally.
    """
    global _downloaded_video_path
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
    elif LOCAL_VIDEO.exists():
        return str(LOCAL_VIDEO)
    else:
        source = DEFAULT_VIDEO_URL
    
    # If it's a URL, download once at startup
    if source.startswith(('http://', 'https://')):
        if _downloaded_video_path is None:
            try:
                _downloaded_video_path = download_video_with_headers(source)
            except Exception as e:
                print(f'Failed to download video: {e}')
                return source  # Return original URL, will fail later
        return _downloaded_video_path
    
    return source


# Resolve video source at import time
VIDEO_SOURCE = get_video_source()
