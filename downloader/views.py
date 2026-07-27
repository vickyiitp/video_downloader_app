from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
import yt_dlp
import os
import tempfile
import io
import sys
import shutil

def index(request):
    default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    return render(request, 'index.html', {'default_path': default_path})

def tutorial_view(request):
    return render(request, 'tutorial.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

@csrf_exempt
def get_video_info(request):
    if request.method == 'POST':
        cookie_file_path = None
        try:
            data = json.loads(request.body)
            video_url = data.get('url')
            cookie_data = data.get('cookies')

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL is required.'}, status=400)

            ydl_opts = {'noplaylist': True}

            if cookie_data:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_cookie_file:
                    temp_cookie_file.write(cookie_data)
                    cookie_file_path = temp_cookie_file.name
                ydl_opts['cookiefile'] = cookie_file_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_info = {
                    'title': info_dict.get('title'),
                    'thumbnail': info_dict.get('thumbnail'),
                    'uploader': info_dict.get('uploader'),
                    'duration_string': info_dict.get('duration_string'),
                }
            return JsonResponse({'status': 'success', 'info': video_info})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if cookie_file_path and os.path.exists(cookie_file_path):
                os.remove(cookie_file_path)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@csrf_exempt
def download_video(request):
    if request.method == 'POST':
        cookie_file_path = None
        try:
            data = json.loads(request.body)
            video_url = data.get('url')
            cookie_data = data.get('cookies')
            save_to_system = data.get('save_to_system', False)
            system_path = data.get('system_path', '')

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL is required.'}, status=400)

            # Build common yt-dlp options
            base_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'noplaylist': True,
                'concurrent_fragment_downloads': 50,
                'http_chunk_size': 20971520,  # 20MB chunk size
                'buffersize': 10485760,       # 10MB buffer
                'retries': 30,
                'fragment_retries': 30,
                'nocheckcertificate': True,
                'ffmpeg_location': os.path.dirname(sys.executable),
            }

            if cookie_data:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_cookie_file:
                    temp_cookie_file.write(cookie_data)
                    cookie_file_path = temp_cookie_file.name
                base_opts['cookiefile'] = cookie_file_path

            # --- Save directly to system path (no temp directory) ---
            if save_to_system and system_path:
                os.makedirs(system_path, exist_ok=True)
                ydl_opts = {**base_opts, 'outtmpl': os.path.join(system_path, '%(title)s.%(ext)s')}

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_title = info_dict.get('title', 'video')
                    safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()

                # Find the saved file
                saved_files = [f for f in os.listdir(system_path) if safe_title in f]
                saved_path = os.path.join(system_path, saved_files[0]) if saved_files else os.path.join(system_path, f"{safe_title}.mp4")

                return JsonResponse({
                    'status': 'success',
                    'saved_to_system': True,
                    'saved_path': saved_path
                })

            # --- Browser download (use temp directory) ---
            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {**base_opts, 'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s')}

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_title = info_dict.get('title', 'video')
                    safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()
                    downloaded_files = os.listdir(temp_dir)
                    if not downloaded_files:
                        raise Exception("Failed to download video file.")
                    file_path = os.path.join(temp_dir, downloaded_files[0])

                    with open(file_path, 'rb') as f:
                        in_memory_file = io.BytesIO(f.read())

                response = FileResponse(in_memory_file, as_attachment=True, filename=f"{safe_title}.mp4")
                return response

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if cookie_file_path and os.path.exists(cookie_file_path):
                os.remove(cookie_file_path)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)