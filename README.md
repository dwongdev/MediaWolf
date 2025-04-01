# MediaWolf 

🚧 **Project Status: Early Development** 🚧  

This project is still in the early stages of development and **is not yet ready for general use**.  

---

### 💡 Getting Involved  

Contributions are welcome from anyone who wants to help shape the project! Here’s how to jump in:  
 
> **1. Start a discussion** – Before diving in, use the repo's Discussions tab to share what you’re planning. This helps avoid overlap and keeps everyone on the same page.  
>  
> **2. Create a Fork** – Fork the repository to create your own copy. Next, create a new branch within your fork for your changes. Push your branch so your progress is visible, and when you're ready, submit a Pull Request (PR).
>
> **3. Recognition** – Contributors who handle a significant part of the work will be added as maintainers of the project and the organisation to help guide the project forward.  

**Note:** Be sure to check out [TheWicklowWolf](https://github.com/TheWicklowWolf) for reference and proof of concepts — it will serve as a guide for formats, docker builds, actions and overall structure/style.  

Thanks for your interest! 🚀  


## **🌍 Proposed Project Features:**

### Books (Readarr & Anna’s Archive)  
✅ Missing List → Read from Readarr, fetch missing books and auto-download via Anna’s Archive  
✅ Manual Search → Search Anna’s Archive and download books (user selection and defined file structure)  
✅ Recommendations → Generate book suggestions based on Readarr library (using a background tasks to scrape from Goodreads) - with options to add or dismiss suggestions including filters and sorting  

### Movies (Radarr & TMDB)  
✅ Recommendations → Read Radarr library and suggest similar movies via TMDB (with options to add or dismiss suggestions including filters and sorting)  
✅ Manual Search → Search via TMDB with option to add to Radarr

### TV Shows (Sonarr & TMDB)  
✅ Recommendations → Read Sonarr library and suggest similar shows via TMDB (with options to add or dismiss suggestions including filters and sorting)  
✅ Manual Search → Search via TMDB with option to add to Sonarr

### Music (Lidarr, LastFM, yt-dlp & Spotify)  
✅ Manual Search → Search Spotify for music and download via spotDL (which uses yt-dlp)  
✅ Recommendations → Generate artist recommendations from LastFM based on Lidarr library (with options to add or dismiss suggestions including filters and sorting)  
✅ Missing List → Read Lidarr library, fetch missing albums and download via yt-dlp  

### Audiobooks (Readarr, Spotify, AudioBookBay & LibriVox??)  
✅ Missing List → Read from Readarr library, fetch missing audiobooks and auto-download  
✅ Manual Search → Search Spotify and download audiobooks (user selection and defined file structure)  
✅ Recommendations → Generate audiobook suggestions based on Readarr library - with options to add or dismiss suggestions including filters and sorting  

### Downloads (via yt-dlp)  
✅ Direct Download Page → Input YouTube or Spotify link and download video/audio using spotDL or yt-dlp  

### Subscriptions (via spotdl and yt-dlp)  
✅ Schedule System → Subscribe to YouTube Channels, Spotify or YouTube Playlists and download on a schedule  


### 🛠️ **Tech Stack Overview**  

| Layer            | Technology                                             |
|------------------|--------------------------------------------------------|
| Frontend         | Bootstrap                                              |
| Backend          | Python with Flask                                      |
| Database         | SQLite (SQLAlchemy)                                    |
| Scheduler        | APScheduler (for cron-based scheduling)                |
| Downloader       | spotdl and yt-dlp                                      |
| Containerization | Docker + Docker Compose                                |


📂 **Proposed Project Structure**

```plaintext
MediaWolf/
├── backend/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── example_api.py  # e.g. API for various sections
│   ├── db/
│   │   ├── __init__.py
│   │   └── example_db_handler.py  # e.g. DB handler
│   ├── services/
│   │   ├── __init__.py
│   │   └── example_services.py  # e.g. services for various integrations
│   ├── utils/
│   │   ├── __init__.py
│   │   └── string_cleaner.py
│   ├── logger.py
│   └── main.py
├── docker/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── gunicorn_config.py
│   ├── init.sh
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── js/
│   │   │   └── example_script.js  # e.g. script for various sections
│   │   ├── css/
│   │   │   └── example_style.css  # e.g. styles
│   │   └── assets/
│   └── templates/
│       ├── base.html
│       └── example_template.html  # e.g. template for various sections
├── docs/
│   └── screenshot.png
├── tests/
│   └── generate_recommendations_for_test.py
└── README.md

```


# 📊 Project Progress Tracker

**Books (Readarr & Anna’s Archive)**
- [ ] Readarr Missing List Scheduled Downloader -> Similar to [BookBounty](https://github.com/TheWicklowWolf/BookBounty)
- [ ] Manual Search -> Similar to [calibre-web-automated-book-downloader](https://github.com/calibrain/calibre-web-automated-book-downloader)
- [ ] Recommendations based on Readarr Book List -> Similar to [eBookBuddy](https://github.com/TheWicklowWolf/eBookBuddy)
- [ ] Download engine -> Similar to [calibre-web-automated-book-downloader](https://github.com/calibrain/calibre-web-automated-book-downloader)

**Movies (Radarr & TMDB)**
- [x] Recommendations based on Radarr Movie List -> Similar to [RadaRec](https://github.com/TheWicklowWolf/RadaRec)
- [x] Manual Search

**TV Shows (Sonarr & TMDB)**
- [ ] Recommendations based on Sonarr Show List -> Similar to [SonaShow](https://github.com/TheWicklowWolf/SonaShow)
- [ ] Manual Search

**Music (Lidarr, LastFM, yt-dlp, Spotify)**
- [ ] Lidarr Missing List Scheduled Downloader -> Similar to [LidaTube](https://github.com/TheWicklowWolf/LidaTube)
- [x] Manual Search
- [x] Recommendations

**Audiobooks (Spotify & LibriVox??)**
- [ ] Missing List Scheduled Downloader -> Similar to [audiobookbay-automated](https://github.com/JamesRy96/audiobookbay-automated)
- [ ] Manual Search -> Similar to [AudioBookRequest](https://github.com/markbeep/AudioBookRequest)
- [ ] Recommendations based on Readarr Audiobook List

**Downloads**
- [ ] Download via SpotDL or yt-dlp directly -> Similar to [SpotTube](https://github.com/TheWicklowWolf/SpotTube)

**Tasks**
- [x] Task Manager System (Cron schedule, Manual Start, Stop, Enable and Disable)

**Subscriptions**
- [ ] YouTube Channels (Audio, Video, Live) -> Similar to [ChannelTube](https://github.com/TheWicklowWolf/ChannelTube)
- [ ] YouTube and Spotify Playlists (Audio) -> Similar to [Syncify](https://github.com/TheWicklowWolf/Syncify)
- [ ] Playlist Generators (For Audio Files) -> Similar to [PlaylistDir](https://github.com/TheWicklowWolf/PlaylistDir)

**Login Manager**
- [x] Login and User Management

**Settings Manager**
- [x] Settings Loader & Saver

# 📦 Local Development Setup

## Docker Setup

To quickly get started with the project, you can use the Docker Compose file.

- Make sure you have Docker and Docker Compose installed.
- Clone the repository.
- Run `docker compose up -d`.
- Access the application at `http://127.0.0.1:5000`.

## Manual Setup

- Clone the repository.
- Create a virtual environment and activate it (You can use `pyenv` to manage multiple Python versions easily).
- Run `pip install -r docker/requirements.txt`.
- Run `export FLASK_APP=backend/main.py && flask run`.
- Access the application at `http://127.0.0.1:5000`.

## Committing Changes

Ensure you have pre-commit hooks installed by running:

```sh
pre-commit install
- Run `git add .`
- Run `git commit -m "Commit Message"`
- Run `git push`
```

If pre-commit hooks flag any issues, follow the suggested fixes and commit again.

## Example Development Setup

A recommended development setup includes:

- **VSCode** with Black formatting (line length set to 200 characters).
- **isort** configured for organizing imports.
- Default formatters for JavaScript, CSS, and HTML.
- Python 3.12.

## Docker Compose - Preview Image with minimal Functionality

```yaml
services:
  mediawolf:
    image: ghcr.io/mediawolforg/mediawolf:develop_latest
    container_name: mediawolf
    environment:
      - lidarr_address=http://localhost:8686
      - lidarr_api_key=""
      - readarr_address=http://localhost:8787
      - readarr_api_key=""
      - radarr_address=http://localhost:7878
      - radarr_api_key=""
      - sonarr_address=http://localhost:8989
      - sonarr_api_key=""
      - lastfm_api_key=""
      - lastfm_api_secret=""
      - tmdb_api_key=""
      - tvdb_api_key=""
      - spotify_client_id=""
      - spotify_client_secret=""
    volumes:
      - /path/to/config:/config
      - /path/to/downloads:/downloads
    ports:
      - 5000:5000
    restart: unless-stopped
```

# Discord
https://discord.gg/hxXzH9Xkcx
