from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
import yt_dlp
import os
import tempfile
import io

def index(request):
    return render(request, 'index.html')

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

            if not video_url:
                return JsonResponse({'status': 'error', 'message': 'URL is required.'}, status=400)

            with tempfile.TemporaryDirectory() as temp_dir:
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }
                
                if cookie_data:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_cookie_file:
                        temp_cookie_file.write(cookie_data)
                        cookie_file_path = temp_cookie_file.name
                    ydl_opts['cookiefile'] = cookie_file_path

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