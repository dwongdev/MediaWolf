import { socket } from './socket_script.js';

export class TasksPage {
    constructor() {
        socket.on('load_task_data', (tasks) => {
            this.renderTasks(tasks);
        });

        socket.on('update_task', (task) => {
            this.updateTask(task)
        });
    }

    init() {
        socket.emit("request_tasks")
    }

    updateTask(task) {
        const row = document.querySelector(`#task-row-${task.id}`);

        if (row) {
            row.querySelector('.task-name').textContent = task.name;
            row.querySelector('.task-cron').textContent = task.cron;
            row.querySelector('.task-status').textContent = task.status;
        }
    }

    manualStart(taskId) {
        socket.emit("task_manual_start", taskId);
    }

    pauseTask(taskId) {
        socket.emit("task_pause", taskId);
    }

    stopTask(taskId) {
        socket.emit("task_stop", taskId);
    }

    cancelTask(taskId) {
        socket.emit("task_cancel", taskId);
    }

    disableTask(taskId) {
        socket.emit("task_disable", taskId);
    }

    renderTasks(tasks) {
        const tableBody = document.getElementById('tasks-table');
        tableBody.innerHTML = '';

        tasks.forEach(task => {
            const template = document.getElementById('task-template');
            const newRow = template.content.cloneNode(true);

            newRow.querySelector('.task-name').textContent = task.name;
            newRow.querySelector('.task-cron').textContent = task.cron;
            newRow.querySelector('.task-status').textContent = task.status;

            const row = newRow.querySelector('tr');
            row.id = `task-row-${task.id}`;

            newRow.querySelector('.btn-primary').addEventListener('click', () => this.manualStart(task.id));
            newRow.querySelector('.btn-warning').addEventListener('click', () => this.pauseTask(task.id));
            newRow.querySelector('.btn-danger').addEventListener('click', () => this.stopTask(task.id));
            newRow.querySelector('.btn-secondary').addEventListener('click', () => this.cancelTask(task.id));
            newRow.querySelector('.btn-info').addEventListener('click', () => this.disableTask(task.id));

            tableBody.appendChild(newRow);
        });
        this.initializeTooltips();
    }

    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}