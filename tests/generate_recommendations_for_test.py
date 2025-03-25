import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db.movie_db_handler import MovieDBHandler
from backend.db.music_db_handler import MusicDBHandler
from backend.services.config_services import Config
from backend.services.lidarr_services import LidarrService
from backend.services.radarr_services import RadarrService

generation_choice = "movies"

if generation_choice == "music":
    db = MusicDBHandler()
    lidarr_sevice = LidarrService(Config(), db)
    lidarr_sevice.refresh_lidarr_artists()
    lidarr_sevice.generate_and_store_lastfm_recommendations()

elif generation_choice == "movies":
    db = MovieDBHandler()
    radarr_service = RadarrService(Config(), db)
    radarr_service.refresh_radarr_movies()
    radarr_service.generate_and_store_tmbd_recommendations()
