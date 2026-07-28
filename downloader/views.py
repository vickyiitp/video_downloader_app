from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
import yt_dlp
import os
import tempfile
import time
import shutil
import re
import urllib.parse


def _normalize_video_url(url):
    """Normalize & clean video URLs across various platforms (SharePoint, Google Drive, etc.)."""
    if not url:
        return url
    url = url.strip()

    # SharePoint URL normalization
    if 'sharepoint.com' in url and '/personal/' in url:
        try:
            parsed = urllib.parse.urlparse(url)
            path = urllib.parse.unquote(parsed.path)
            if '/personal/' in path:
                rel_path = '/personal/' + path.split('/personal/', 1)[1]
                netloc = parsed.netloc
                return f"https://{netloc}/_layouts/15/stream.aspx?id={urllib.parse.quote(rel_path)}"
        except Exception:
            pass

    return url


def _format_cookies_txt(cookie_raw):
    """Normalize user-pasted cookies from any format to valid Netscape tab-separated format."""
    if not cookie_raw or not cookie_raw.strip():
        return ""
    lines = ["# Netscape HTTP Cookie File"]
    for line in cookie_raw.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        parts = re.split(r'\s+', s)
        if len(parts) >= 7:
            domain, flag, path, secure, exp, name = parts[:6]
            val = ' '.join(parts[6:])
            lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{exp}\t{name}\t{val}")
        elif len(parts) >= 6:
            domain, flag, path, secure, name, val = parts[:6]
            lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t0\t{name}\t{val}")
        else:
            lines.append(s)
    return '\n'.join(lines)


def _get_base_ydl_opts(video_url=""):
    """Universal yt-dlp options for maximum compatibility across any website."""
    parsed_domain = ""
    if video_url:
        try:
            parsed_domain = urllib.parse.urlparse(video_url).netloc
        except Exception:
            pass

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }
    if parsed_domain:
        headers['Referer'] = f'https://{parsed_domain}/'

    return {
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'noprogress': True,
        'quiet': True,
        'socket_timeout': 120,
        'retries': 30,
        'fragment_retries': 30,
        'js_runtimes': {'node': {}},
        'remote_components': ['ejs:github'],
        'http_headers': headers,
        'user_agent': user_agent,
        'allow_unauthenticated': True,
    }


def index(request):
    return render(request, 'index.html')


def tutorial_view(request):
    return render(request, 'tutorial.html')


def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    return render(request, 'contact.html')


@csrf_exempt
def fetch_info(request):
    """Fetch video metadata (title, thumbnail, duration, channel) from any supported site."""
    if request.method in ['POST', 'GET']:
        cookie_file_path = None
        try:
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    data = json.loads(request.body or '{}')
                else:
                    data = request.POST
            else:
                data = request.GET

            raw_url = data.get('url', '').strip()
            video_url = _normalize_video_url(raw_url)
            cookie_data = data.get('cookies', '').strip()

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL is required.'}, status=400)

            ydl_opts = _get_base_ydl_opts(video_url)
            ydl_opts['skip_download'] = True

            if cookie_data:
                formatted_cookies = _format_cookies_txt(cookie_data)
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as f:
                    f.write(formatted_cookies)
                    cookie_file_path = f.name
                ydl_opts['cookiefile'] = cookie_file_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            title = info.get('title') or 'Video'
            thumbnail = info.get('thumbnail') or ''
            if not thumbnail and info.get('thumbnails'):
                thumbnail = info['thumbnails'][-1].get('url', '')

            # Format duration as mm:ss or hh:mm:ss
            duration_secs = info.get('duration') or 0
            if duration_secs >= 3600:
                hours = int(duration_secs // 3600)
                minutes = int((duration_secs % 3600) // 60)
                seconds = int(duration_secs % 60)
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            elif duration_secs > 0:
                minutes = int(duration_secs // 60)
                seconds = int(duration_secs % 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Video Stream"

            extractor_name = info.get('extractor_key') or info.get('extractor') or 'Web Video'

            result = {
                'status': 'ok',
                'title': title,
                'thumbnail': thumbnail,
                'duration': duration_str,
                'duration_secs': duration_secs,
                'channel': info.get('channel') or info.get('uploader') or info.get('uploader_id') or extractor_name,
                'view_count': info.get('view_count'),
                'webpage_url': info.get('webpage_url', raw_url),
                'site': extractor_name,
            }

            return JsonResponse(result)

        except Exception as e:
            err_msg = str(e)
            if 'login.microsoftonline.com' in err_msg or 'Session cookies are required' in err_msg:
                err_msg = "Private / Protected video requiring authentication. Please log in on your browser, play the video once, and paste fresh cookies.txt into the cookies box."
            elif 'Private video' in err_msg or 'Sign in' in err_msg or 'login' in err_msg.lower():
                err_msg = f"Private content detected. Please paste your cookies.txt for this website in the cookies box below to unlock access."
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        finally:
            if cookie_file_path and os.path.exists(cookie_file_path):
                try:
                    os.remove(cookie_file_path)
                except Exception:
                    pass

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def download_video(request):
    """Download video from any website with universal format merging & fallback."""
    if request.method in ['POST', 'GET']:
        cookie_file_path = None
        temp_dir = None
        try:
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    data = json.loads(request.body or '{}')
                else:
                    data = request.POST
            else:
                data = request.GET

            raw_url = data.get('url', '').strip()
            video_url = _normalize_video_url(raw_url)
            cookie_data = data.get('cookies', '').strip()

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL is required.'}, status=400)

            # Use dedicated temp directory for downloads
            downloads_dir = os.path.join(tempfile.gettempdir(), 'rapidgrab_downloads')
            os.makedirs(downloads_dir, exist_ok=True)

            # Cleanup older temp downloads (older than 1 hour)
            now = time.time()
            for item in os.listdir(downloads_dir):
                item_path = os.path.join(downloads_dir, item)
                try:
                    if os.path.isdir(item_path) and (now - os.path.getmtime(item_path)) > 3600:
                        shutil.rmtree(item_path, ignore_errors=True)
                except Exception:
                    pass

            temp_dir = tempfile.mkdtemp(dir=downloads_dir)

            ydl_opts = _get_base_ydl_opts(video_url)
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best/b',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'concurrent_fragment_downloads': 64,
                'http_chunk_size': 10485760,
                'buffersize': 10485760,
                'retries': 30,
                'fragment_retries': 30,
            })

            if cookie_data:
                formatted_cookies = _format_cookies_txt(cookie_data)
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as f:
                    f.write(formatted_cookies)
                    cookie_file_path = f.name
                ydl_opts['cookiefile'] = cookie_file_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'video')

            # Find downloaded file
            downloaded_files = os.listdir(temp_dir)
            if not downloaded_files:
                raise Exception("Download failed — no output file was produced by yt-dlp.")

            file_path = os.path.join(temp_dir, downloaded_files[0])
            ext = os.path.splitext(downloaded_files[0])[1] or '.mp4'
            safe_title = "".join(c for c in title if c.isalnum() or c in ' ._-').strip() or 'video'
            filename = f"{safe_title}{ext}"

            # Stream directly from disk without reading entire file into RAM
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, as_attachment=True, filename=filename)
            return response

        except Exception as e:
            err_msg = str(e)
            if 'login.microsoftonline.com' in err_msg or 'Session cookies are required' in err_msg:
                err_msg = "Private / Protected video requiring authentication. Please log in on your browser, play the video once, and paste fresh cookies.txt into the cookies box."
            elif 'Private video' in err_msg or 'Sign in' in err_msg or 'login' in err_msg.lower():
                err_msg = f"Private content detected. Please paste your cookies.txt for this website in the cookies box below to unlock access."
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            return JsonResponse({'status': 'error', 'message': err_msg}, status=400)
        finally:
            if cookie_file_path and os.path.exists(cookie_file_path):
                try:
                    os.remove(cookie_file_path)
                except Exception:
                    pass

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)