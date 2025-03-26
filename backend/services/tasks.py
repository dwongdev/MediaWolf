import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional

import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from logger import logger
from services.config_services import Config
from services.lidarr_services import LidarrService
from services.radarr_services import RadarrService
from services.readarr_services import ReadarrService
from services.sonarr_services import SonarrService


@dataclass
class Task:
    id: int
    name: str
    cron: str
    description: str
    function_name: str
    last_run: str
    status: str = "Scheduled"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def default_tasks(cls) -> List["Task"]:
        """Return a list of default tasks."""
        return [
            cls(1, "Lidarr Sync", "0 1 * * *", "Refreshes Lidarr artist list.", "lidarr_sync", ""),
            cls(2, "Artist Recommendations", "0 2 * * *", "Generates artist recommendations list.", "generate_artist_recommendations", ""),
            cls(3, "Radarr Sync", "0 3 * * *", "Updates Radarr movie database.", "radarr_sync", ""),
            cls(4, "Movie Recommendations", "0 4 * * *", "Generates movie recommendations list.", "generate_movie_recommendations", ""),
            cls(5, "Sonarr Sync", "0 5 * * *", "Syncs Sonarr series list.", "sonarr_sync", ""),
            cls(6, "TV Recommendations", "0 6 * * *", "Generates tv recommendations list.", "generate_tv_recommendations", ""),
            cls(7, "Readarr Sync", "0 7 * * *", "Updates Readarr book collection.", "readarr_sync", ""),
            cls(8, "Book Recommendations", "0 8 * * *", "Generates book recommendations list.", "generate_book_recommendations", ""),
            cls(9, "Spotify Sync", "0 9 * * *", "Syncs Spotify playlists.", "spotify_sync", ""),
            cls(10, "YouTube Sync", "0 10 * * *", "Syncs YouTube playlists and channels.", "youtube_sync", ""),
        ]


class Tasks:
    def __init__(self, config: Config, lidarr_service: LidarrService, radarr_service: RadarrService, readarr_service: ReadarrService, sonarr_service: SonarrService):
        self.lidarr_service = lidarr_service
        self.radarr_service = radarr_service
        self.readarr_service = readarr_service
        self.sonarr_service = sonarr_service
        self.config = config
        self.tasks: Dict[int, Task] = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        self.load_tasks()
        self.schedule_all_tasks()

    def load_tasks(self):
        """Load tasks from JSON file, falling back to defaults if missing."""
        if os.path.exists(self.config.TASKS_CONFIG_FILE_NAME):
            try:
                with open(self.config.TASKS_CONFIG_FILE_NAME, "r") as f:
                    tasks_data = json.load(f)
                    self.tasks = {}
                    for task_id, data in tasks_data.items():
                        task = Task(**data)
                        if task.status == "Running":
                            task.status = "Scheduled"
                        self.tasks[int(task_id)] = task

                logger.info("Tasks loaded from file.")

            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading tasks: {e}")
                self.create_default_tasks()
        else:
            self.create_default_tasks()

    def create_default_tasks(self):
        """Create default tasks and save them."""
        default_tasks = Task.default_tasks()
        self.tasks = {task.id: task for task in default_tasks}
        self.save_tasks()
        logger.info("Default tasks created and saved.")

    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            with open(self.config.TASKS_CONFIG_FILE_NAME, "w") as f:
                json.dump({str(task_id): task.to_dict() for task_id, task in self.tasks.items()}, f, indent=4)
            logger.info("Tasks successfully saved.")

        except IOError as e:
            logger.error(f"Failed to save tasks: {e}")

    def update_task(self, task_id: str, **updates):
        """Update task attributes dynamically."""
        task = self.tasks.get(task_id)
        if task:
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
            self.schedule_task(task_id, task.to_dict())
            logger.info(f"Task '{task_id}' updated: {updates}")
        else:
            logger.warning(f"Task '{task_id}' not found.")

    def update_task_cron(self, task_id: str, new_cron: str):
        """Update the cron expression of a specific task and save it."""
        if task_id in self.tasks:
            self.tasks[task_id].cron = new_cron
            self.save_tasks()
            self.schedule_task(task_id, self.tasks[task_id].to_dict())
            logger.info(f"Updated cron for task '{task_id}' to '{new_cron}'")
        else:
            logger.warning(f"Task '{task_id}' not found.")

    def schedule_task(self, task_id, task_data):
        """Schedules a task with APScheduler using cron."""
        job_id = f"task_{task_id}"

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        try:
            self.scheduler.add_job(
                func=self.run_task,
                trigger=CronTrigger.from_crontab(task_data["cron"]),
                id=job_id,
                replace_existing=True,
                kwargs={"task_id": task_id},
            )
            logger.info(f"Task '{task_id}' scheduled with cron: {task_data['cron']}")

        except Exception as e:
            logger.error(f"Failed to schedule task '{task_id}': {e}")

    def schedule_all_tasks(self):
        """Schedule all active tasks."""
        for task_id, task in self.tasks.items():
            if task.status != "Disabled":
                self.schedule_task(task_id, task.to_dict())

    def run_task(self, task_id):
        """Executes the task's specific functions."""
        task = self.get_task(task_id)
        if not task:
            logger.error(f"Task '{task_id}' not found!")
            return

        logger.info(f"Running task: {task.name}")
        task.status = "Running"
        self.save_tasks()

        try:
            func_name = task.function_name
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                ret_status = func()
                task.status = ret_status
                logger.info(f"Task {task_id}: {task.name} - {ret_status}")
            else:
                logger.error(f"Function {func_name} not found for task '{task_id}'")

        except Exception as e:
            logger.error(f"Error running task '{task_id}': {e}")
            task.status = "Error"

        timestamp = datetime.now()
        task.last_run = timestamp.strftime("%d-%B-%Y %H:%M:%S")
        self.save_tasks()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self.tasks.get(task_id)

    def list_tasks(self) -> Dict[str, Task]:
        """Return all tasks."""
        return [task.to_dict() for task in self.tasks.values()]

    def lidarr_sync(self):
        logger.info("Starting Lidarr Sync...")
        ret_status = self.lidarr_service.refresh_lidarr_artists()
        logger.info(f"Lidarr Sync: {ret_status}")
        return ret_status

    def generate_artist_recommendations(self):
        logger.info("Starting to Generate Artist Recommendations...")
        ret_status = self.lidarr_service.generate_and_store_lastfm_recommendations()
        logger.info(f"Generation of Artist Recommendations: {ret_status}")
        return ret_status

    def radarr_sync(self):
        logger.info("Running Radarr Sync...")
        ret_status = self.radarr_service.refresh_radarr_movies()
        logger.info(f"Radarr Sync: {ret_status}")
        return ret_status

    def generate_movie_recommendations(self):
        logger.info("Starting to Generate Movie Recommendations...")
        ret_status = self.radarr_service.generate_and_store_tmbd_recommendations()
        logger.info(f"Generation of Movie Recommendations: {ret_status}")
        return ret_status

    def sonarr_sync(self):
        logger.info("Starting Sonarr Sync...")
        ret_status = "Completed"  #  self.sonarr_service.refresh_sonarr_series()
        logger.info(f"Sonarr Sync: {ret_status}")
        return ret_status

    def generate_tv_recommendations(self):
        logger.info("Starting to Generate TV Recommendations...")
        ret_status = "Completed"  # self.sonarr_service.generate_and_store_tv_recommendations()
        logger.info(f"Generation of TV Recommendations: {ret_status}")
        return ret_status

    def readarr_sync(self):
        logger.info("Starting Readarr Sync...")
        ret_status = "Completed"  #  self.readarr_service.refresh_readarr_books()
        logger.info(f"Readarr Sync: {ret_status}")
        return ret_status

    def generate_book_recommendations(self):
        logger.info("Starting to Generate Book Recommendations...")
        ret_status = "Completed"  #  self.readarr_service.generate_and_store_book_recommendations()
        logger.info(f"Generation of Book Recommendations: {ret_status}")
        return ret_status

    def spotify_sync(self):
        logger.info("Starting Spotify Sync...")
        ret_status = "Completed"  # self.spotify_service.sync_spotify_playlists()
        logger.info(f"Spotify Sync: {ret_status}")
        return ret_status

    def youtube_sync(self):
        logger.info("Starting YouTube Sync...")
        ret_status = "Completed"  #  self.youtube_service.sync_youtube_playlists_and_channels()
        logger.info(f"YouTube Sync: {ret_status}")
        return ret_status
