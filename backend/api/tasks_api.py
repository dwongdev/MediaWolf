from flask import Blueprint, render_template
from flask_socketio import SocketIO
from services.config_services import Config
from services.lidarr_services import LidarrService
from services.radarr_services import RadarrService
from services.readarr_services import ReadarrService
from services.sonarr_services import SonarrService
from services.tasks import Tasks

tasks_bp = Blueprint("tasks", __name__)


class TasksAPI:
    def __init__(self, socketio: SocketIO, config: Config, lidarr_service: LidarrService, radarr_service: RadarrService, readarr_service: ReadarrService, sonarr_service: SonarrService):
        self.socketio = socketio
        self.tasks_manager = Tasks(config, lidarr_service, radarr_service, readarr_service, sonarr_service)

        self.setup_routes()
        self.setup_socket_events()

    def setup_routes(self):
        """Define Flask routes."""

        @tasks_bp.route("/tasks")
        def serve_page():
            return render_template("tasks.html")

    def setup_socket_events(self):
        """Handle Socket.IO events."""

        @self.socketio.on("task_manual_start")
        def handle_manual_start(task_id):
            """Manually trigger a task to run immediately."""
            task = self.tasks_manager.get_task(task_id)
            if task:
                try:
                    task.status = "Running"
                    self.socketio.emit("update_task", task.to_dict())

                    self.tasks_manager.scheduler.add_job(
                        func=self.tasks_manager.run_task,
                        trigger="date",
                        id=f"task_{task_id}",
                        replace_existing=True,
                        kwargs={"task_id": task_id},
                    )

                    task_list = self.tasks_manager.list_tasks()
                    self.socketio.emit("load_task_data", task_list)

                except Exception as e:
                    self.socketio.emit("new_toast_msg", {"title": "Task Error", "message": f"Error with Manual start for Task {task.name}: {str(e)}"})
            else:
                self.socketio.emit("new_toast_msg", {"title": "Failed to start Task", "message": "Task not found, check config"})

        @self.socketio.on("task_stop")
        def handle_stop(task_id):
            """Stop a running task (removes from scheduler)."""
            task = self.tasks_manager.get_task(task_id)
            if task:
                task.status = "Stopped"
                job = self.tasks_manager.scheduler.get_job(f"task_{task_id}")
                if job:
                    job.remove()
                self.tasks_manager.save_tasks()
                self.socketio.emit("update_task", task.to_dict())

        @self.socketio.on("task_disable")
        def handle_disable(task_id):
            """Disable a task (stops and prevents further runs)."""
            task = self.tasks_manager.get_task(task_id)
            if task:
                task.status = "Disabled"
                if self.tasks_manager.scheduler.get_job(f"task_{task_id}"):
                    self.tasks_manager.scheduler.remove_job(f"task_{task_id}")
                self.tasks_manager.save_tasks()
                self.socketio.emit("update_task", task.to_dict())

        @self.socketio.on("task_enable")
        def handle_enable(task_id):
            """Re-enable a disabled task."""
            task = self.tasks_manager.get_task(task_id)
            if task and task.status == "Disabled":
                task.status = "Scheduled"
                self.tasks_manager.schedule_task(task_id, task.to_dict())
                self.tasks_manager.save_tasks()
                self.socketio.emit("update_task", task.to_dict())

        @self.socketio.on("request_tasks")
        def handle_request_tasks():
            """Emit a list of all tasks to the client."""
            task_list = self.tasks_manager.list_tasks()
            self.socketio.emit("load_task_data", task_list)

        @self.socketio.on("update_task_cron")
        def handle_update_task_cron(data):
            """Update a task's cron expression."""
            task_id = data.get("taskId")
            new_cron = data.get("newCron")

            if task_id and new_cron:
                self.tasks_manager.update_task_cron(task_id, new_cron)

                task = self.tasks_manager.get_task(task_id)
                if task:
                    task.status = "Updated"
                    self.socketio.emit("update_task", task.to_dict())

                    self.tasks_manager.schedule_task(task_id, task.to_dict())

    def get_blueprint(self):
        return tasks_bp
