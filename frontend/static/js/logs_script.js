import { socket } from './socket_script.js';

export class LogsPage {
    constructor() {
        socket.on("refreshed_logs", (logs) => {
            const logContent = document.getElementById('logContent');
            logContent.innerText = logs;
        });
    }

    init() {
        this.initTabs();
    }

    fetchLogs() {
        socket.emit("refresh_logs");
    }

    initTabs() {
        const refreshButton = document.getElementById('refreshLogs');
        refreshButton.addEventListener('click', () => this.fetchLogs());
    }
}
