<div align="center">

# ⚡ RapidGrab — Universal Media Ingestion Engine
### High-Throughput Video & Audio Extraction Platform Powered by Django 5 & yt-dlp

[![Live Demo](https://img.shields.io/badge/Live%20Demo-rapidgrab.onrender.com-10b981?style=for-the-badge&logo=render)](https://rapidgrab.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![yt-dlp](https://img.shields.io/badge/Engine-yt--dlp-red?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)
[![Author: Vicky Kumar](https://img.shields.io/badge/Architect-Vicky%20Kumar%20(%40vickyiitp)-8b5cf6?style=for-the-badge&logo=github)](https://github.com/vickyiitp)

<p align="center">
  <b>Extract high-definition video and lossless audio streams from 1,000+ platforms with zero ads, cookie authentication, and real-time streaming buffers.</b>
</p>

</div>

---

## 🏗️ System Architecture & Data Flow

```
                      ┌──────────────────────┐
                      │    Client Browser    │
                      └──────────┬───────────┘
                                 │ HTTP POST /extract
                                 ▼
                      ┌──────────────────────┐
                      │ Gunicorn / WhiteNoise│ (Static Asset Optimization)
                      └──────────┬───────────┘
                                 │
                                 ▼
                      ┌──────────────────────┐
                      │   Django 5 Service   │
                      │   (Request Router)   │
                      └──────────┬───────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │                                   │
               ▼                                   ▼
    [ URL Sanitizer & Security ]       [ Stream Quality Inspector ]
    (Domain Whitelist & Auth)          (Format Code Discovery)
               │                                   │
               └─────────────────┬─────────────────┘
                                 │
                                 ▼
                     [ yt-dlp Ingestion Engine ]
                     (Multi-Segment Parallel Pull)
                                 │
                                 ▼
                  [ Direct Stream to Client / CDN ]
```

---

## ⚡ Core Features

- 🌐 **1,000+ Platforms Supported**: Seamlessly extracts media from YouTube, Twitter/X, Instagram Reels, TikTok, Vimeo, Reddit, SoundCloud, and Facebook.
- 💎 **Adaptive Resolution Discovery**: Automatically detects available stream formats from 4K/2K Ultra HD down to 720p/480p and 320kbps MP3 audio.
- 🔒 **Cookie & Authentication Support**: Built-in credential handling for age-gated, private, and subscription-tier streams.
- 🚀 **Asynchronous Streaming Pipelines**: Streams data directly to the client without saturating server RAM.
- 🛡️ **Production-Hardened**: Served with `Gunicorn` WSGI, cached with `WhiteNoise`, and configured with anti-scraping countermeasures.

---

## 🛠️ Tech Stack & Engineering Specifications

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend Runtime** | Python 3.11+ | High-concurrency async execution |
| **Web Framework** | Django 5.2 | Request routing, CSRF protection, URL dispatching |
| **Media Engine** | `yt-dlp` (>=2026.07.04) | Core streaming extraction and format demuxing |
| **WSGI Server** | Gunicorn 23.0 | Multi-worker production process manager |
| **Asset Delivery** | WhiteNoise 6.9 | Compressed, cached zero-overhead static asset server |
| **Deployment** | Render / PaaS | Production live deployment |

---

## 📂 Project Structure

```
video_downloader_app/
├── backend/            # Django application settings & core logic
├── downloader/         # Primary media parsing and download views
│   ├── views.py        # Stream resolution extractors & handlers
│   ├── urls.py         # REST routing
│   └── forms.py        # Input validation & sanitization
├── static/             # Frontend assets, stylesheets & scripts
├── templates/          # HTML5 responsive UI templates
├── manage.py           # Django CLI orchestrator
└── requirements.txt    # Production dependencies
```

---

## 🚀 Quick Start Guide

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/vickyiitp/video_downloader_app.git
cd video_downloader_app

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Database Migrations & Start Local Server

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
Open **`http://localhost:8000`** in your browser.

---

## 👨‍💻 Architect & Maintenance

Engineered by **Vicky Kumar** (`@vickyiitp`) — Founder @ [Devil Labs](https://devillabs.dev)  
- GitHub: [@vickyiitp](https://github.com/vickyiitp)  
- Contact: [devil.labs.contact@gmail.com](mailto:devil.labs.contact@gmail.com)
